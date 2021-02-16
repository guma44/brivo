import math
import unit_converters as converters

def calculate_bitterness(og, fg, ibu):
    og = converters.to_blg(og)
    fg = converters.to_blg(fg)
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
    * @param  {Number} color  color in SRM
    * @param  {Number} weigth weigth in kilograms
    * @param  {Number} volume volume in liters
    * @return {Number}             MCUs for given ingredient
    """
    return (color * weigth * 2.205) / (volume * 0.264)


def morey_equation(mcu):
    """
    Convert Malt Color Unit to SRM
    * Caclculate color added by ingredient using Moray Equation
    * @param  {Number} MCU Malt Color Units
    * @return {Number}     Added color in SRM
    """
    return 1.4922 * (mcu^0.6859)


def calculate_gravity_points(weigth, extraction, efficiency, volume):
    """
    * Calculate gravity points (GP) added by ingredient to the batch
    * @param  {Number} weigth     weigth in kilograms
    * @param  {Number} extraction ingredient extraction (%) - 0-100
    * @param  {Number} efficiency efficiency of the batch (%) - 0-100
    * @param  {Number} volume     volume of batch in liters
    * @return {Number}            Added gravity points
    """
    return (weigth * (extraction / 100) * (efficiency / 100) * 384) / volume


# =====================
# =   IBU FORMULAS    =
# =====================

def calculate_ibu_tinseth(og, time, type, alpha, weight, volume):
    """
    Hop IBU FORMULA - Tinseth method
    * Hop IBU calculation using Tinseth formula
    * @param  {Number} og     Gravity of the beer in SG
    * @param  {Number} time   Time of boil (minutes)
    * @param  {String} type   Type of hops eg. hopPellets
    * @param  {Number} alpha  Percent of alpha acids (%)
    * @param  {Number} weight Weigth of hops in grams
    * @param  {Number} volume Volume of the batch in liters
    * @return {Number}        Added IBU for given hop and batch
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
    * @param  {Number} og     Gravity of the beer in SG
    * @param  {Number} time   Time of boil (minutes)
    * @param  {String} type   Type of hops eg. Hop pellets
    * @param  {Number} alpha  Percent of alpha acids (%)
    * @param  {Number} weight Weigth of hops in grams
    * @param  {Number} volume Volume of the batch in liters
    * @return {Number}        Added IBU for given hop and batch
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
    * @param  {Number} og Original gravity in SG
    * @param  {Number} fg Final gravity in SG
    * @return {Number}    Alcohol by Volume
    """
    return (og - fg) * 131.25


def calculate_abw(og, fg):
    """
    * Calculate alcohol by weight
    * @param  {Number} og Original gravity in SG
    * @param  {Number} fg Final gravity in SG
    * @return {Number}    Alcohol by Weight
    """
    return 0.79336 * calculate_abv(og, fg)

