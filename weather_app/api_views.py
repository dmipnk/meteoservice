from rest_framework import viewsets, permissions
from django.contrib.auth.models import User
from .models import City, Favorite, WeatherForecast
from .serializers import UserSerializer, CitySerializer, WeatherForecastSerializer, FavoriteSerializer

class UserViewSet(viewsets.ModelViewSet):
    queryset = User.objects.all()
    serializer_class = UserSerializer
    permission_classes = [permissions.IsAuthenticatedOrReadOnly]

class CityViewSet(viewsets.ModelViewSet):
    queryset = City.objects.all()
    serializer_class = CitySerializer
    permission_classes = [permissions.IsAuthenticatedOrReadOnly]

class WeatherForecastViewSet(viewsets.ModelViewSet):
    queryset = WeatherForecast.objects.all()
    serializer_class = WeatherForecastSerializer
    permission_classes = [permissions.IsAuthenticatedOrReadOnly]

class FavoriteViewSet(viewsets.ModelViewSet):
    serializer_class = FavoriteSerializer
    permission_classes = [permissions.IsAuthenticated]
    
    def get_queryset(self):
        return Favorite.objects.filter(user_id=self.request.user)
    
    def perform_create(self, serializer):
        serializer.save(user_id=self.request.user)