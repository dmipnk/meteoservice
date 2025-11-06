# weather_app/serializers.py
from rest_framework import serializers
from django.contrib.auth.models import User
from .models import City, Favorite, WeatherForecast

class UserSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ['id', 'username', 'email', 'date_joined']
        read_only_fields = ['id', 'date_joined']

class CitySerializer(serializers.ModelSerializer):
    class Meta:
        model = City
        fields = [
            'id', 'name', 'country', 'latitude', 'longitude', 
            'photo', 'users'
        ]
        read_only_fields = ['id']

class WeatherForecastSerializer(serializers.ModelSerializer):
    city_name = serializers.CharField(source='city_id.name', read_only=True)
    city_country = serializers.CharField(source='city_id.country', read_only=True)
    
    class Meta:
        model = WeatherForecast
        fields = [
            'id', 'city_id', 'city_name', 'city_country', 
            'forecast_date', 'temperature_min', 'temperature_max', 
            'condition', 'humidity', 'created_at'
        ]
        read_only_fields = ['id', 'created_at']

class FavoriteSerializer(serializers.ModelSerializer):
    city_name = serializers.CharField(source='city_id.name', read_only=True)
    city_country = serializers.CharField(source='city_id.country', read_only=True)
    user_username = serializers.CharField(source='user_id.username', read_only=True)
    
    class Meta:
        model = Favorite
        fields = [
            'id', 'user_id', 'user_username', 'city_id', 
            'city_name', 'city_country', 'added_at'
        ]
        read_only_fields = ['id', 'user_id', 'added_at']