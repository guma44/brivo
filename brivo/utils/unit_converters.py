# =========================
# =   UNITS CONVERTING    =
# =     - brewing -       =
# =========================
def to_calories(og, fg):
    """Calories in 100 ml -
    og & fg in sg
    calories per 12 oz beer = [(6.9 × ABW) + 4.0 × (RE - 0.1)] × fg × 3.55
    to 100ml = ((calories / 12) / 29.573529564) * 100"""
    calories = ((6.9 * toABW(og, fg)) + 4.0 * (toRealExtract(og, fg) - 0.1)) * fg * 3.55
    return ((calories / 12) / 29.573529564) * 100


def to_real_extract(og, fg):
    """Real Extract -
    og & fg in sg
    Attenuation = 100 * (og-fg) / og - 1
    """
    return (0.1808 * toblg(og)) + (0.8192 * toblg(fg))


def to_attenuation(og, fg):
    """Attenuation -
    og & fg in sg
    Attenuation = 100 * (og-fg) / og - 1"""
    return 100 * (og - fg) / (og - 1.0)


def to_abw(og, fg):
    """Alcohol by Weight -
    og & fg in sg
    ABW = ABV * 0.79336"""
    return 0.79336 * toABV(og, fg)


def to_abv(og, fg):
    """Alcohol by Volume -
    og & fg in sg
    ABV = (og - fg) * 131.25"""
    return (og - fg) * 131.25


def to_blg(sg):
    """Convert SG to BLG"""
    return (((182.4601 * sg - 775.6821) * sg + 1262.7794) * sg - 669.5622)


def to_sg(blg):
    """Convert BLG to SG"""
    return (blg / (258.6 - ((blg / 258.2) * 227.1))) + 1


# =========================
# =   UNITS CONVERTING    =
# =      - weight -       =
# =========================


def ounces_to_grams(ounces):
    """Convert ounces to grams"""
    return ounces * 28.3495231


def ounces_to_kilograms(ounces):
    """Convert ounces to kilograms"""
    return ounces / 35.274


def ounces_to_pounds(ounces):
    """Convert ounces to kilograms"""
    return ounces * 0.062500


def grams_to_ounces(grams):
    """Convert grams to ounces"""
    return grams * 0.035274


def grams_to_kilograms(grams):
    """Convert grams to kilograms"""
    return grams / 1000


def grams_to_pounds(grams):
    """Convert grams to pounds"""
    return grams * 0.0022046


def kilograms_to_grams(kilograms):
    """Convert kilograms to grams"""
    return kilograms / 0.001


def kilograms_to_ounces(kilograms):
    """Convert kilograms to ounces"""
    return kilograms * 35.274


def kilograms_to_pounds(kilograms):
    """Convert kilograms to pounds"""
    return kilograms * 2.2046


def pounds_to_grams(pounds):
    """Convert pounds to grams"""
    return pounds / 0.0022046


def pounds_to_kilograms(pounds):
    """Convert pounds to grams"""
    return pounds / 2.2046


def pounds_to_ounces(pounds):
    """Convert pounds to grams"""
    return pounds * 16


# =========================
# =   UNITS CONVERTING    =
# =      - volume -       =
# =========================
def gallons_to_liters(gallons):
    """Convert gallons to liters"""
    return gallons * 3.78541178


def liters_to_milliliters(liters):
    """Convert liters to milliliters"""
    return liters / 0.001


def liters_to_us_pints(liters):
    """Convert liters to US Pints"""
    return liters * 2.1134


def liters_to_us_gallons(liters):
    """Convert liters to US gallons"""
    return liters * 0.26417


def liters_to_uk_pints(liters):
    """Convert liters to UK Pints"""
    return liters * 1.7598


def liters_to_uk_gallons(liters):
    """Convert liters to UK gallons"""
    return liters * 0.21997


def milliliters_to_liters(milliliters):
    """Convert milliliters to liters"""
    return milliliters / 1000


def milliliters_to_us_pints(milliliters):
    """Convert milliliters to US Pints"""
    return milliliters * 0.0021134


def milliliters_to_us_gallons(milliliters):
    """Convert milliliters to US gallons"""
    return milliliters * 0.00026417


def milliliters_to_uk_pints(milliliters):
    """Convert milliliters to UK Pints"""
    return milliliters * 0.0017598


def milliliters_to_uk_gallons(milliliters):
    """Convert milliliters to UK gallons"""
    return milliliters * 0.00021997


def us_pints_to_milliliters(us_pints):
    """Convert US Pints to milliliters"""
    return us_pints / 0.0021134


def us_pints_to_liters(us_pints):
    """Convert US Pints to liters"""
    return us_pints / 2.1134


def us_pints_to_us_gallons(us_pints):
    """Convert US Pints to US gallons"""
    return us_pints * 0.10408


def us_pints_to_uk_pints(us_pints):
    """Convert US Pints to UK Pints"""
    return us_pints * 0.83267


def us_pints_to_uk_gallons(us_pints):
    """Convert US Pints to UK gallons"""
    return us_pints * 0.10408


def us_gallons_to_milliliters(us_gallons):
    """Convert US gallons to milliliters"""
    return us_gallons / 0.00026417


def us_gallons_to_liters(us_gallons):
    """Convert US gallons to liters"""
    return us_gallons / 0.26417


def us_gallons_to_us_pints(us_gallons):
    """Convert US gallons to US Pints"""
    return us_gallons * 8


def us_gallons_to_uk_pints(us_gallons):
    """Convert US gallons to UK Pints"""
    return us_gallons * 6.6614


def us_gallons_to_uk_gallons(us_gallons):
    """Convert US gallons to UK gallons"""
    return us_gallons * 0.83267


def uk_pints_to_milliliters(uk_pints):
    """Convert UK Pints to milliliters"""
    return uk_pints / 0.0017598


def uk_pints_to_liters(uk_pints):
    """Convert UK Pints to liters"""
    return uk_pints / 1.7598


def uk_pints_to_us_gallons(uk_pints):
    """Convert UK Pints to US gallons"""
    return uk_pints * 0.15012


def uk_pints_to_us_pints(uk_pints):
    """Convert UK Pints to US Pints"""
    return uk_pints * 1.2009


def uk_pints_to_uk_gallons(uk_pints):
    """Convert UK Pints to UK gallons"""
    return uk_pints * 0.125


def uk_gallons_to_milliliters(uk_gallons):
    """Convert UK gallons to milliliters"""
    return uk_gallons / 0.00021997


def uk_gallons_to_liters(uk_gallons):
    """Convert UK gallons to liters"""
    return uk_gallons / 0.21997


def uk_gallons_to_us_pints(uk_gallons):
    """Convert UK gallons to US Pints"""
    return uk_gallons * 9.6076


def uk_gallons_to_uk_pints(uk_gallons):
    """Convert UK gallons to UK Pints"""
    return uk_gallons * 8


def uk_gallons_to_us_gallons(uk_gallons):
    """Convert UK gallons to US gallons"""
    return uk_gallons * 1.2009


# ========================
# =   UNITS CONVERTING   =
# =    - temperature -   =
# ========================
def celsius_to_fahrenheit(celsius):
    """Convert celsius to fahrenheit"""
    return parseFloat(celsius) * 1.8 + 32


def celsius_to_kelvin(celsius):
    """Convert celsius to kelvin"""
    return parseFloat(celsius) + 273.15


def fahrenheit_to_celsius(fahrenheit):
    """Convert fahrenheit to celsius"""
    return (parseFloat(fahrenheit) - 32) / 1.8


def kelvin_to_celsius(kelvin):
    """Convert kelvin to celsius"""
    return parseFloat(kelvin) - 273.15


# ========================
# =   COLOR CONVERTER    =
# ========================
def return_hex_color_from_srm(srm):
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

