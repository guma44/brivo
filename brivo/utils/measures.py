from sympy import S, Symbol
from measurement.base import MeasureBase

class BeerGravity(MeasureBase):
    SU = Symbol('Plato')
    STANDARD_UNIT = 'plato'
    UNITS = {
        'plato': 1.0,
        'sg': (SU / (258.6 - ((SU / 258.2) * 227.1))) + 1
    }
    ALIAS = {
        'Plato': 'plato',
        'Specific Gravity': 'sg',
        'SG': 'sg'
    }


class BeerColor(MeasureBase):
    STANDARD_UNIT = 'ebc'
    UNITS = {
        'ebc': 1.0,
        'srm': 1.968503937007874,
    }
