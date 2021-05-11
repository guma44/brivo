from django_measurement.models import MeasurementField
from measurement.measures import Volume, Mass, Temperature

from brivo.utils.measures import BeerColor, BeerGravity


__all__ = (
    "BeerColorField",
    "BeerGravityField",
    "VolumeField",
    "MassField",
    "TemperatureField"
)

class BeerColorField(MeasurementField):

    def __init__(self, *args, **kwargs):
        kwargs["measurement"] = BeerColor
        super(BeerColorField, self).__init__(*args, **kwargs)

class BeerGravityField(MeasurementField):

    def __init__(self, *args, **kwargs):
        kwargs["measurement"] = BeerGravity
        super(BeerGravityField, self).__init__(*args, **kwargs)

class VolumeField(MeasurementField):

    def __init__(self, *args, **kwargs):
        kwargs["measurement"] = Volume
        super(VolumeField, self).__init__(*args, **kwargs)

class MassField(MeasurementField):

    def __init__(self, *args, **kwargs):
        kwargs["measurement"] = Mass
        super(MassField, self).__init__(*args, **kwargs)

class TemperatureField(MeasurementField):

    def __init__(self, *args, **kwargs):
        kwargs["measurement"] = Temperature
        super(TemperatureField, self).__init__(*args, **kwargs)