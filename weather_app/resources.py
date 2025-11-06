from import_export import resources, fields
from import_export.widgets import ForeignKeyWidget
from .models import City, WeatherForecast


class CityResource(resources.ModelResource):
    class Meta:
        model = City
        fields = ("id", "name", "country", "latitude", "longitude")

class WeatherForecastResource(resources.ModelResource):
    city_id = fields.Field(
        column_name='city',
        attribute='city_id',
        widget=ForeignKeyWidget(City, 'name')
    )

    class Meta:
        model = WeatherForecast
        fields = (
            "id",
            "city_id",
            "forecast_date",
            "temperature_min",
            "temperature_max",
            "condition",
            "humidity",
        )
        export_order = fields