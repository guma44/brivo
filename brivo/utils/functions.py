import re
import os
import math
from pybeerxml.parser import Parser
from pybeerxml.utils import to_lower
from xml.etree import ElementTree

from django.utils.encoding import smart_str
from django.template import TemplateDoesNotExist
from django.template.loader import render_to_string
from django.conf import settings
from django.core.mail import EmailMessage, EmailMultiAlternatives

from measurement.measures import Volume, Mass

_FLOAT_REGEX = re.compile(r"^-?(?:\d+())?(?:\.\d*())?(?:e-?\d+())?(?:\2|\1\3)$")
_INT_REGEX = re.compile(r"^(?<![\d.])[0-9]+(?![\d.])$")
_EMAIL_REGEX = re.compile(r"(.+@[a-zA-Z0-9\.]+,?){1,}")


def render_mail(template, subject, email, context):
    to = [email] if isinstance(email, str) else email
    # remove superfluous line breaks
    subject = " ".join(subject.splitlines()).strip()
    subject = f"BRIVO: {subject}"

    from_email = settings.DEFAULT_FROM_EMAIL
    ext = os.path.splitext(template)[-1][1:]
    body = render_to_string(
        template,
        context
    ).strip()
    if ext == "txt":
        msg = EmailMultiAlternatives(subject, body, from_email, to)
    elif ext == "html":
        msg = EmailMessage(subject, body, from_email, to)
        msg.content_subtype = "html"  # Main content is now text/html
    else:
        raise Exception("Extention for e-mail template not found")
    return msg


def send_mail(template, subject, email, context):
    msg = render_mail(template, subject, email, context)
    msg.send()


def convert_type(data):
    """Check and convert the type of variable"""
    if isinstance(data, dict):
        return clean_data(data)
    if data is None:
        return None
    elif isinstance(data, (float, int, bool)):
        return data
    elif _FLOAT_REGEX.match(data) is not None:  # Floats
        return float(data)
    elif _INT_REGEX.match(data) is not None:  # Integers
        return int(data)
    elif data == "True" or data == "true":
        return True
    elif data == "False" or data == "false":
        return False
    else:
        return smart_str(data, encoding="utf-8", strings_only=False, errors="strict")


def clean_data(data):
    new_data = {}
    for k, v in data.items():
        if isinstance(v, list):
            l = []
            for d in v:
                l.append(convert_type(d))
            new_data[k] = l
        else:
            new_data[k] = convert_type(v)
    return new_data


def get_user_units_with_repr(user):
    data = {}
    if user.profile.general_units.lower() == "metric":
        data["small_weight"] = ("g", "g")
        data["big_weight"] = ("kg", "kg")
        data["volume"] = ("l", "l")
    else:
        data["small_weight"] = ("oz", "oz")
        data["big_weight"] = ("lb", "lb")
        data["volume"] = ("us_g", "US Gal")
    if user.profile.gravity_units.lower() == "plato":
        data["gravity_units"] = ("Plato", "°P")
    else:
        data["gravity_units"] = ("SG", "SG")
    if user.profile.color_units.lower() == "ebc":
        data["color_units"] = ("EBC", "EBC")
    else:
        data["color_units"] = ("SRM", "SRM")
    if user.profile.temperature_units.lower() == "celsius":
        data["temp_units"] = ("c", "°C")
    elif user.profile.temperature_units.lower() == "fahrenheit":
        data["temp_units"] = ("f", "°F")
    else:
        data["temp_units"] = ("k", "K")
    return data


def get_user_units(user):
    data = {}
    if user.profile.general_units.lower() == "metric":
        data["mass_units"] = "g"
        data["volume_units"] = "l"
    else:
        data["mass_units"] = "oz"
        data["volume_units"] = "us_g"
    if user.profile.gravity_units.lower() == "plato":
        data["gravity_units"] = "plato"
    else:
        data["gravity_units"] = "sg"
    if user.profile.color_units.lower() == "ebc":
        data["color_units"] = "ebc"
    else:
        data["color_units"] = "srm"
    if user.profile.temperature_units.lower() == "celsius":
        data["temperature_units"] = "c"
    elif user.profile.temperature_units.lower() == "fahrenheit":
        data["temperature_units"] = "f"
    else:
        data["temperature_units"] = "k"
    return data


def to_plato(sg):
    """Convert SG to plato"""
    return ((182.4601 * sg - 775.6821) * sg + 1262.7794) * sg - 669.5622


def to_sg(plato):
    """Convert plato to SG"""
    return (plato / (258.6 - ((plato / 258.2) * 227.1))) + 1


def get_beer_calories(og, fg):
    """Calories in 100 ml -
    og & fg in sg
    calories per 12 oz beer = [(6.9 × ABW) + 4.0 × (RE - 0.1)] × fg × 3.55
    to 100ml = ((calories / 12) / 29.573529564) * 100"""
    calories = ((6.9 * get_abw(og, fg)) + 4.0 * (get_real_extract(og, fg) - 0.1)) * fg * 3.55
    return (((calories / 12) / 29.573529564) * 100) * 5


def get_real_extract(og, fg):
    """Real Extract -
    og & fg in sg
    Attenuation = 100 * (og-fg) / og - 1
    """
    return (0.1808 * to_plato(og)) + (0.8192 * to_plato(fg))


def get_attenuation(og, fg):
    """Attenuation -
    og & fg in sg
    Attenuation = 100 * (og-fg) / og - 1"""
    return 100 * (og - fg) / (og - 1.0)


def get_abw(og, fg):
    """Alcohol by Weight -
    og & fg in sg
    ABW = ABV * 0.79336"""
    return 0.79336 * get_abv(og, fg)


def get_abv(og, fg):
    """Alcohol by Volume -
    og & fg in sg"""
    return 76.08 * (og - fg) / (1.775 - og) * (fg / 0.794)

def get_bitterness(og, fg, ibu):
    og = to_plato(og)
    fg = to_plato(fg)
    result = ((ibu / ((0.1808 * og) + (0.8192 * fg))) / 10)
    if not result: # TODO check if this would pick up 0
        result = '-'
    return result


def display_number(number, after_comma):
    """Display number with after_comma precision
    number & after_comma are numbers
    after_comma = the number of digits after the decimal point
    """
    if not number:
        return '-'
    return f"{number:.{after_comma}f}"


def percentage_of_range(min_var, max_var, actual_var):
    result = ((actual_var - min_var) / (max_var - min_var)) * 100
    if (result < 0):
        return 0
    elif (result > 100):
        return 100
    if (result >= 0 and result <= 100):
        return display_number(result, 0)
    return 0


def calculate_mcu(color, weigth, volume):
    """
    Return Color of malt
    * Calculate added color by fermentable for batch
    :param float color:  color in SRM
    :param float weigth: weigth in kilograms
    :param float volume: volume in liters
    :return float:   MCUs for given ingredient
    """
    lovibond = (color + 0.76)/1.3546
    return (lovibond * weigth * 2.205) / (volume * 0.264)


def morey_equation(mcu):
    """
    Convert Malt Color Unit to SRM
    * Caclculate color added by ingredient using Moray Equation
    :param float MCU: Malt Color Units
    :return float:     Added color in SRM
    """
    return 1.4922 * (mcu**0.6859)


def calculate_gravity_points(weigth, extraction, efficiency, volume):
    """
    * Calculate gravity points (GP) added by ingredient to the batch
    :param float weigth:     weigth in kilograms
    :param float extraction: ingredient extraction (%) - 0-100
    :param float efficiency: efficiency of the batch (%) - 0-100
    :param float volume:     volume of batch in liters
    :return float:            Added gravity points
    """
    points = (weigth * (extraction / 100) * (efficiency / 100) * 384) / volume
    return points


# =====================
# =   IBU FORMULAS    =
# =====================

def calculate_ibu_tinseth(og, time, type, alpha, weight, volume):
    """
    Hop IBU FORMULA - Tinseth method
    * Hop IBU calculation using Tinseth formula
    :param float og:     Gravity of the beer in SG
    :param float time:   Time of boil (minutes)
    :param string type:   Type of hops eg. hopPellets
    :param float alpha:  Percent of alpha acids (%)
    :param float weight: Weigth of hops in grams
    :param float volume: Volume of the batch in liters
    :return float:        Added IBU for given hop and batch
    """
    utilization = ((1.65 * (0.000125**(og - 1))) *
        ((1 - (math.e**(-0.04 * time))) / (4.15)))
    if (type == 'PELLETS'):
        utilization = utilization + (utilization * 0.1)

    return utilization * alpha / 100 * weight * 1000 / volume



def calculate_ibu_rager(og, time, type, alpha, weight, volume):
    """
    Hop IBU FORMULA - Rager method
    * Hop IBU calculation using Ranger formula
    :param float og:     Gravity of the beer in SG
    :param float time:   Time of boil (minutes)
    :param string type:   Type of hops eg. PELLETS
    :param float alpha:  Percent of alpha acids (%)
    :param float weight: Weigth of hops in grams
    :param float volume: Volume of the batch in liters
    :return float:        Added IBU for given hop and batch
    """
    utilization = 18.18 + 13.86 * math.tanh((time - 31.32) / 18.27)
    if (type == 'PELLETS'):
        utilization = utilization + (utilization * 0.1)

    u = 0
    if (og > 1.05):
        u = (og - 1.05) / 0.2

    return weight * utilization * alpha / 10 / (volume * (1 + u))


def calculate_abv(og, fg):
    """
    * Calculate alcohol by volume
    :param float og: Original gravity in SG
    :param float fg: Final gravity in SG
    :return float:    Alcohol by Volume
    """
    return (og - fg) * 131.25


def calculate_abw(og, fg):
    """
    * Calculate alcohol by weight
    :param float og: Original gravity in SG
    :param float fg: Final gravity in SG
    :return float:    Alcohol by Weight
    """
    return 0.79336 * calculate_abv(og, fg)


def calculate_priming_sugar(priming_temperature, beer_volume, carbonation_level, sugar_type="TABLE_SUGAR"):
    """
    :param float priming_temperature: Temperature of beer in fahrenheit
    :param float beer_volume: Volume of beer to prime in gallons US
    :param float carbonation_level: Desired carbonation level
    :return Weight: Weight of table sugar to use
    """
    amount = (
        15.195 * beer_volume * (carbonation_level - 3.0378 + (0.050062 * priming_temperature) - (0.00026555 * (priming_temperature ** 2)))
    )
    if sugar_type == "CORN_SUGAR":
        amount = amount + amount*0.1
    elif sugar_type == "DRY_EXTRACT":
        amount = amount + amount*0.46
    return Mass(g=amount)


def calculate_dissolve_volume(sugar_amount, sugar_type, og):
    """Calculate volume to disolve priming sugar
    :param float sugar_amount: Sugar amount in pounds Lb
    :param string sugar_type: Sugar type
    :param float og: OG in SG
    """
    if sugar_type == "DRY_EXTRACT":
        ppg = 36
    else:
        ppg = 46
    print(sugar_amount, og)
    volume = abs(sugar_amount * ppg / (1 - og) / 1000.0)
    volume = volume - 0.1 * volume
    return Volume(us_g=volume)


def get_hex_color_from_srm(srm):
    """Return HEX converted color from SRM"""
    if (srm <= 1):
        return "#FFE699"
    elif (srm <= 2):
        return "#FFD878"
    elif (srm <= 3):
        return "#FFCA5A"
    elif (srm <= 4):
        return "#FFBF42"
    elif (srm <= 5):
        return "#FBB123"
    elif (srm <= 6):
        return "#F8A600"
    elif (srm <= 7):
        return "#F39C00"
    elif (srm <= 8):
        return "#EA8F00"
    elif (srm <= 9):
        return "#E58500"
    elif (srm <= 10):
        return "#DE7C00"
    elif (srm <= 11):
        return "#D77200"
    elif (srm <= 12):
        return "#CF6900"
    elif (srm <= 13):
        return "#CB6200"
    elif (srm <= 14):
        return "#C35900"
    elif (srm <= 15):
        return "#BB5100"
    elif (srm <= 16):
        return "#B54C00"
    elif (srm <= 17):
        return "#B04500"
    elif (srm <= 18):
        return "#A63E00"
    elif (srm <= 19):
        return "#A13700"
    elif (srm <= 20):
        return "#9B3200"
    elif (srm <= 21):
        return "#952D00"
    elif (srm <= 22):
        return "#8E2900"
    elif (srm <= 23):
        return "#882300"
    elif (srm <= 24):
        return "#821E00"
    elif (srm <= 25):
        return "#7B1A00"
    elif (srm <= 26):
        return "#771900"
    elif (srm <= 27):
        return "#701400"
    elif (srm <= 28):
        return "#6A0E00"
    elif (srm <= 29):
        return "#660D00"
    elif (srm <= 30):
        return "#5E0B00"
    elif (srm <= 31):
        return "#5A0A02"
    elif (srm <= 32):
        return "#600903"
    elif (srm <= 33):
        return "#520907"
    elif (srm <= 34):
        return "#4C0505"
    elif (srm <= 35):
        return "#470606"
    elif (srm <= 36):
        return "#440607"
    elif (srm <= 37):
        return "#3F0708"
    elif (srm <= 38):
        return "#3B0607"
    elif (srm <= 39):
        return "#3A070B"
    else:
        return "#36080A"


def beerxml_to_json(xml_file):
    """Convert beerxml recipe to JSON."""
    fermentable_type_map = {
        "grain": "GRAIN",
        "sugar": "SUGAR",
        "extract": "LIQUID EXTRACT",
        "dry extract": "DRY EXTRACT",
        "adjunct": "SUGAR",
    }

    yeast_type_map = {
        "ale": "ALE",
        "lager": "LAGER",
        "wheat": "WHEAT",
        "wine": "CHAMPAGNE",
        "champagne": "CHAMPAGNE",
    }


    yeast_form_map = {
        "liquid": "LIQUID",
        "dry": "DRY",
        "slant": "SLURRY",
        "culture": "CULTURE",
    }

    beers = []
    parser = Parser()
    # with open(xml_file, "rt") as file:
    tree = ElementTree.parse(xml_file)

    for recipe_node in tree.iter():
        if to_lower(recipe_node.tag) != "recipe":
            continue
        recipe = parser.parse_recipe(recipe_node)
        
        print("Working on", recipe.name)
        beer = {
            "fermentables": [],
            "hops": [],
            "yeasts": [],
            "extras": [],
            "mash_steps": [],
            "extra_info": {},
        }
        beer["boil_time"] = math.ceil(recipe.boil_time)
        beer["boil_loss"] = round(recipe.equipment.evap_rate, 2)
        beer["trub_loss"] = math.ceil(
            100 * (recipe.equipment.trub_chiller_loss / recipe.batch_size)
        )
        beer["dry_hopping_loss"] = 10
        beer["type"] = recipe.type.upper()
        beer["expected_beer_volume"] = f"{recipe.batch_size} l"
        # Mashing
        beer["mash_efficiency"] = recipe.efficiency
        beer["liquor_to_grist_ratio"] = 4
        for fermentable in recipe.fermentables:
            print(fermentable)
            beer["fermentables"].append(
                {
                    "type": fermentable_type_map[fermentable.type.lower()],
                    "name": fermentable.name.strip(".").strip(),
                    "amount": f"{fermentable.amount} kg",
                    "extraction": fermentable._yield,
                    "color": f"{fermentable.color} srm",
                    "use": "MASHING"
                    if getattr(fermentable, "is_mashed", "true").lower() == "true"
                    else "BOIL",
                }
            )
        for hop in recipe.hops:
            if hop.use.upper() == "DRY HOP":
                hoptime = math.ceil((hop.time / 60) / 24)
                time_unit = "DAY"
            else:
                hoptime = hop.time
                time_unit = "MINUTE"

            beer["hops"].append(
                {
                    "use": hop.use.upper(),
                    "name": hop.name.strip(".").strip(),
                    "amount": f"{hop.amount} kg",
                    "time": hoptime,
                    "time_unit": time_unit,
                    "alpha_acids": hop.alpha,
                }
            )
        for yeast in recipe.yeasts:
            beer["yeasts"].append(
                {
                    "name": yeast.name.strip(".").strip(),
                    "type": yeast_type_map[yeast.type.lower()],
                    "form": yeast_form_map[yeast.form.lower()],
                    "amount": f"{yeast.amount} kg",  # it could be liters but we keep only one
                    "lab": yeast.laboratory,
                }
            )
        for extra in recipe.miscs:
            beer["extras"].append(
                {
                    "type": extra.type.upper(),
                    "name": extra.name.strip(".").strip(),
                    "use": extra.use.upper(),
                    "amount": f"{extra.amount} kg",
                    "time": extra.time,
                    "time_unit": "MINUTE",
                }
            )
        for mash_step in recipe.mash.steps:
            beer["mash_steps"].append(
                {
                    "temperature": f"{mash_step.step_temp} c",
                    "time": mash_step.step_time,
                }
            )
        beer["name"] = recipe.name
        beer[
            "style"
        ] = f"{int(recipe.style.category_number)}{recipe.style.style_letter}"  # 2015 BJCP Category
        beers.append(beer)
    print(beers)
    return beers