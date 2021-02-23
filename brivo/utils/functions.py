import math


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
    return ((calories / 12) / 29.573529564) * 100


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
    og & fg in sg
    ABV = (og - fg) * 131.25"""
    return (og - fg) * 131.25

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
    :return float:             MCUs for given ingredient
    """
    return (color * weigth * 2.205) / (volume * 0.264)


def morey_equation(mcu):
    """
    Convert Malt Color Unit to SRM
    * Caclculate color added by ingredient using Moray Equation
    :param float MCU: Malt Color Units
    :return float:     Added color in SRM
    """
    return 1.4922 * (mcu^0.6859)


def calculate_gravity_points(weigth, extraction, efficiency, volume):
    """
    * Calculate gravity points (GP) added by ingredient to the batch
    :param float weigth:     weigth in kilograms
    :param float extraction: ingredient extraction (%) - 0-100
    :param float efficiency: efficiency of the batch (%) - 0-100
    :param float volume:     volume of batch in liters
    :return float:            Added gravity points
    """
    return (weigth * (extraction / 100) * (efficiency / 100) * 384) / volume


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
    utilization = ((1.65 * (0.000125^(og - 1))) *
        ((1 - (math.e^(-0.04 * time))) / (4.15)))
    if (type == 'Hop pellets'):
        utilization = utilization + (utilization * 0.1)

    return utilization * alpha / 100 * weight * 1000 / volume



def calculate_ibu_rager(og, time, type, alpha, weight, volume):
    """
    Hop IBU FORMULA - Rager method
    * Hop IBU calculation using Ranger formula
    :param float og:     Gravity of the beer in SG
    :param float time:   Time of boil (minutes)
    :param string type:   Type of hops eg. Hop pellets
    :param float alpha:  Percent of alpha acids (%)
    :param float weight: Weigth of hops in grams
    :param float volume: Volume of the batch in liters
    :return float:        Added IBU for given hop and batch
    """
    utilization = 18.18 + 13.86 * math.tanh((time - 31.32) / 18.27)
    if (type == 'Hop pellets'):
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


def get_hex_color_from_srm(srm):
    """Return HEX converted color from SRM"""
    if (srm <= 1):
        return '#FAFAA0'
    elif (srm <= 2):
        return '#F9FB69'
    elif (srm <= 3):
        return '#F5F531'
    elif (srm <= 4):
        return '#EBE52F'
    elif (srm <= 5):
        return '#E0D032'
    elif (srm <= 6):
        return '#D8BC34'
    elif (srm <= 7):
        return '#CDA836'
    elif (srm <= 8):
        return '#C69539'
    elif (srm <= 9):
        return '#C18837'
    elif (srm <= 10):
        return '#C08038'
    elif (srm <= 11):
        return '#C07937'
    elif (srm <= 12):
        return '#C17239'
    elif (srm <= 13):
        return '#BE6B39'
    elif (srm <= 14):
        return '#B46338'
    elif (srm <= 15):
        return '#A65A36'
    elif (srm <= 16):
        return '#985332'
    elif (srm <= 17):
        return '#8B4B30'
    elif (srm <= 18):
        return '#7D4429'
    elif (srm <= 19):
        return '#6C3D23'
    elif (srm <= 20):
        return '#603417'
    elif (srm <= 21):
        return '#512D0B'
    elif (srm <= 22):
        return '#44260E'
    elif (srm <= 23):
        return '#351311'
    elif (srm <= 24):
        return '#271717'
    elif (srm <= 25):
        return '#211312'
    elif (srm <= 26):
        return '#1B100E'
    elif (srm <= 27):
        return '#170D0B'
    elif (srm <= 28):
        return '#120A08'
    elif (srm <= 29):
        return '#0E0604'
    elif (srm > 29):
        return '#080300'
    else:
        return '#FAFAA0'

