from django.urls import path
from . import views
from .views import CityCreateView, CityDetailView, CitySearchView, CityUpdateView, CityDeleteView

urlpatterns = [
    path('cities/', views.city_list, name="city_list"),
    path('forecasts/', views.forecast_list, name="forecast_list"),
    path("cities/<int:pk>/", CityDetailView.as_view(), name="city_detail"),
    path("cities/add/", CityCreateView.as_view(), name="city_add"),
    path("cities/search/", CitySearchView.as_view(), name="city_search"),
    path("cities/<int:pk>/edit/", CityUpdateView.as_view(), name="city_update"),
    path("cities/<int:pk>/delete/", CityDeleteView.as_view(), name="city_delete"),
    path('my-favorites/', views.my_favorites, name='my_favorites'),
    
    # ✅ ДОБАВЛЯЕМ URLS ДЛЯ ИЗБРАННОГО
    path("cities/<int:pk>/favorite/add/", views.add_favorite, name="add_favorite"),
    path("cities/<int:pk>/favorite/remove/", views.remove_favorite, name="remove_favorite"),

    # support URLs
    path('support/', views.support_request, name='support_request'),
    path('support/dashboard/', views.support_dashboard, name='support_dashboard'),
    path('support/<int:pk>/', views.support_request_detail, name='support_request_detail'),
]
