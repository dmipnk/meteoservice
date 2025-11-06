from django.contrib import admin, messages
from .models import City, Favorite, WeatherForecast, SupportRequest
from .resources import CityResource, WeatherForecastResource
from import_export.admin import ImportExportModelAdmin
import random
import string



class ForecastInline(admin.TabularInline):
    model = WeatherForecast
    extra = 1

class FavoriteInline(admin.TabularInline):
    model = Favorite
    extra = 0
    can_delete = False

@admin.action(description="Массово изменить пароли пользователей (рандом)")
def reset_passwords(modeladmin, request, queryset):
    alphabet = string.ascii_letters + string.digits
    updated = 0
    for user in queryset:
        new_password = ''.join(random.choices(alphabet, k=100))  # простой пароль из 8 символов
        user.password_hash = new_password   # просто строка вместо хэша
        user.save(update_fields=["password_hash"])
        updated += 1
    modeladmin.message_user(request, f"Пароли обновлены у {updated} пользователей.", messages.SUCCESS)


# Register your models here.
@admin.register(City)
class CityAdmin(admin.ModelAdmin):

    resource_class = CityResource

    # какие поля будут показываться в списке
    list_display = ("name", "country", "latitude", "longitude")

    # фильтры справа
    list_filter = ("country",)

    # поля, по которым можно искать
    search_fields = ("name", "country")
    inlines = [ForecastInline, FavoriteInline]


@admin.register(WeatherForecast)
class ForecastAdmin(ImportExportModelAdmin):

    resource_class = WeatherForecastResource

    # какие поля будут показываться в списке
    list_display = ("city_id", "forecast_date", "temperature_min", "temperature_max", "condition", "humidity")

    # фильтры справа
    list_filter = ("city_id", "forecast_date")

    # поля, по которым можно искать
    search_fields = ("city_id", "forecast_date", "condition")

@admin.register(SupportRequest)
class SupportRequestAdmin(admin.ModelAdmin):
    list_display = ['id', 'subject', 'name', 'email', 'status', 'created_at']
    list_filter = ['status', 'created_at']
    search_fields = ['subject', 'name', 'email', 'message']
    readonly_fields = ['created_at', 'updated_at']
