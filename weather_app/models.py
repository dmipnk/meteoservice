from django.db import models
from django.contrib.auth.models import User
from .validators import validate_latitude, validate_longitude
from django.db.models.signals import post_save
from django.dispatch import receiver

class Profile(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE, verbose_name="Пользователь")
    avatar = models.ImageField("Аватар", upload_to='avatars/', blank=True, null=True)
    bio = models.TextField("Биография", max_length=500, blank=True)
    location = models.CharField("Местоположение", max_length=100, blank=True)
    birth_date = models.DateField("Дата рождения", null=True, blank=True)
    
    def __str__(self):
        return f"Профиль {self.user.username}"

class ActiveCityManager(models.Manager):
    """Менеджер, возвращающий только активные города"""
    def get_queryset(self):
        # фильтруем города, например, только с заполненными координатами
        return super().get_queryset().filter(weatherforecast__isnull=False).distinct()
    
class City(models.Model):
    name = models.CharField("Название", max_length=30)
    country = models.CharField("Страна", max_length=30)
    latitude = models.FloatField("Широта", validators=[validate_latitude])
    longitude = models.FloatField("Долгота", validators=[validate_longitude])
    users = models.ManyToManyField(User, through='Favorite', verbose_name="Пользователи")
    photo = models.ImageField("Фото города", upload_to='city_photos/', blank=True, null=True)
    
    class Meta:
        verbose_name_plural = "Cities"
        ordering = ['name']
    objects = models.Manager()          
    active = ActiveCityManager() 

    def __str__(self):
        return self.name + "/" + self.country

class Favorite(models.Model):
    user_id = models.ForeignKey(User, on_delete=models.CASCADE)
    city_id = models.ForeignKey(City, on_delete=models.CASCADE)
    added_at = models.DateTimeField("Дата добавления",auto_now_add=True)
 
    class Meta:
        verbose_name_plural = "Favorite Cities"
        unique_together = ['user_id', 'city_id']
   
    def __str__(self):
         return self.city_id.name + "/" + self.city_id.country

class WeatherForecast(models.Model):
    city_id = models.ForeignKey(City, on_delete=models.CASCADE)
    forecast_date = models.DateTimeField("Дата")
    temperature_min = models.FloatField("Минимальная температура")
    temperature_max = models.FloatField("Maксимальная температура")
    condition = models.CharField("Погодные условия", max_length=30)
    humidity = models.IntegerField("Влажность")
    created_at = models.DateTimeField("Время создания", auto_now_add = True)
    
    def __str__(self):
          return self.city_id.name + "/" + self.city_id.country

class SupportRequest(models.Model):
    STATUS_CHOICES = [
        ('new', 'Новая'),
        ('in_progress', 'В обработке'),
        ('resolved', 'Решена'),
        ('closed', 'Закрыта'),
    ]

    user = models.ForeignKey(User, on_delete=models.CASCADE, verbose_name="Пользователь", null=True, blank=True)
    name = models.CharField("Имя", max_length=100)
    email = models.EmailField("Email")
    subject = models.CharField("Тема", max_length=200)
    message = models.TextField("Сообщение")
    status = models.CharField("Статус", max_length=20, choices=STATUS_CHOICES, default='new')
    created_at = models.DateTimeField("Дата создания", auto_now_add=True)
    updated_at = models.DateTimeField("Дата обновления", auto_now=True)
    
    # Ответ от сотрудника
    admin_response = models.TextField("Ответ администратора", blank=True)
    responded_at = models.DateTimeField("Дата ответа", null=True, blank=True)
    responded_by = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, blank=True, 
                                   related_name='responded_requests', verbose_name="Ответил")

    class Meta:
        verbose_name = "Заявка в поддержку"
        verbose_name_plural = "Заявки в поддержку"
        ordering = ['-created_at']

    def __str__(self):
        return f"{self.subject} ({self.get_status_display()})"

# Сигналы для автоматического создания профиля при создании пользователя
@receiver(post_save, sender=User)
def create_user_profile(sender, instance, created, **kwargs):
    if created:
        Profile.objects.create(user=instance)

@receiver(post_save, sender=User)
def save_user_profile(sender, instance, **kwargs):
    if hasattr(instance, 'profile'):
        instance.profile.save()

