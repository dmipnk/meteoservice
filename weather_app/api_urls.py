# weather_app/api_urls.py
from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .api_views import UserViewSet, CityViewSet, WeatherForecastViewSet, FavoriteViewSet

router = DefaultRouter()
router.register(r'users', UserViewSet, basename='user')
router.register(r'cities', CityViewSet, basename='city')
router.register(r'forecasts', WeatherForecastViewSet, basename='weatherforecast')
router.register(r'favorites', FavoriteViewSet, basename='favorite')  # ← basename обязательно!

urlpatterns = [
    path('', include(router.urls)),
]