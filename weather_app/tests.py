from django.test import TestCase, Client
from django.contrib.auth.models import User
from django.urls import reverse
from django.core.files.uploadedfile import SimpleUploadedFile
from .models import City, Favorite, WeatherForecast, Profile
from django.utils import timezone
from datetime import timedelta

class ModelTests(TestCase):
    def setUp(self):
        """Настройка тестовых данных"""
        self.user = User.objects.create_user(
            username='testuser', 
            password='testpass123',
            email='test@example.com'
        )
        self.city = City.objects.create(
            name='Test City',
            country='Test Country', 
            latitude=55.7558,
            longitude=37.6173
        )
    
    def test_city_creation(self):
        """Тест создания объекта модели City"""
        self.assertEqual(self.city.name, 'Test City')
        self.assertEqual(self.city.country, 'Test Country')
        self.assertEqual(self.city.latitude, 55.7558)
        self.assertTrue(isinstance(self.city, City))
        self.assertEqual(str(self.city), 'Test City/Test Country')
    
    def test_favorite_creation(self):
        """Тест создания объекта модели Favorite"""
        favorite = Favorite.objects.create(
            user_id=self.user,
            city_id=self.city
        )
        self.assertEqual(favorite.user_id, self.user)
        self.assertEqual(favorite.city_id, self.city)
        self.assertTrue(isinstance(favorite, Favorite))
    
    def test_weather_forecast_creation(self):
        """Тест создания объекта модели WeatherForecast"""
        forecast = WeatherForecast.objects.create(
            city_id=self.city,
            forecast_date=timezone.now() + timedelta(days=1),
            temperature_min=10.5,
            temperature_max=20.5,
            condition='Sunny',
            humidity=65
        )
        self.assertEqual(forecast.city_id, self.city)
        self.assertEqual(forecast.condition, 'Sunny')
        self.assertEqual(forecast.humidity, 65)


class CustomManagerTests(TestCase):
    def setUp(self):
        """Настройка для тестов кастомного менеджера"""
        self.city_with_forecast = City.objects.create(
            name='City With Forecast',
            country='Country1',
            latitude=55.7558,
            longitude=37.6173
        )
        self.city_without_forecast = City.objects.create(
            name='City Without Forecast', 
            country='Country2',
            latitude=59.9343,
            longitude=30.3351
        )
        
        # Создаем прогноз только для одного города
        WeatherForecast.objects.create(
            city_id=self.city_with_forecast,
            forecast_date=timezone.now() + timedelta(days=1),
            temperature_min=15.0,
            temperature_max=25.0,
            condition='Cloudy',
            humidity=70
        )
    
    def test_active_city_manager_returns_only_cities_with_forecasts(self):
        """Тест кастомного менеджера - возвращает только города с прогнозами"""
        active_cities = City.active.all()
        
        # Должен вернуть только город с прогнозом
        self.assertEqual(active_cities.count(), 1)
        self.assertEqual(active_cities.first(), self.city_with_forecast)
        self.assertNotIn(self.city_without_forecast, active_cities)
    
    def test_default_manager_returns_all_cities(self):
        """Тест что стандартный менеджер возвращает все города"""
        all_cities = City.objects.all()
        self.assertEqual(all_cities.count(), 2)
        self.assertIn(self.city_with_forecast, all_cities)
        self.assertIn(self.city_without_forecast, all_cities)


class ViewTests(TestCase):
    def setUp(self):
        self.client = Client()
        self.user = User.objects.create_user(
            username='testuser',
            password='testpass123'
        )
        self.city = City.objects.create(
            name='Test City',
            country='Test Country',
            latitude=55.7558,
            longitude=37.6173
        )
    
    def test_city_list_view_status_200(self):
        """Тест работы view-функции списка городов (код 200)"""
        response = self.client.get(reverse('city_list'))
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'city_list.html')
    
    def test_city_detail_view_status_200(self):
        """Тест работы view-функции деталей города (код 200)"""
        response = self.client.get(reverse('city_detail', args=[self.city.pk]))
        self.assertEqual(response.status_code, 200)
    
    def test_forecast_list_view_status_200(self):
        """Тест работы view-функции списка прогнозов (код 200)"""
        response = self.client.get(reverse('forecast_list'))
        self.assertEqual(response.status_code, 200)


class AuthenticationTests(TestCase):
    def setUp(self):
        self.client = Client()
        self.user = User.objects.create_user(
            username='testuser',
            password='testpass123'
        )
        self.city = City.objects.create(
            name='Test City',
            country='Test Country',
            latitude=55.7558,
            longitude=37.6173
        )
    
    def test_login_page_access_for_anonymous(self):
        """Тест доступа к странице логина для анонимных пользователей"""
        response = self.client.get(reverse('login'))
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'Вход')  # или другой текст из формы
    
    def test_register_page_access_for_anonymous(self):
        """Тест доступа к странице регистрации для анонимных пользователей"""
        response = self.client.get(reverse('register'))
        self.assertEqual(response.status_code, 200)
    
    def test_successful_user_registration(self):
        """Тест успешной регистрации пользователя"""
        response = self.client.post(reverse('register'), {
            'username': 'newuser',
            'password1': 'complexpass123',
            'password2': 'complexpass123'
        })
        self.assertEqual(response.status_code, 302)  # редирект после регистрации
        
        # Проверяем что пользователь создался
        self.assertTrue(User.objects.filter(username='newuser').exists())
    
    def test_login_redirect_for_protected_page(self):
        """Тест редиректа для анонимных пользователей при доступе к защищенной странице"""
        # Предполагаем, что city_add требует авторизации
        response = self.client.get(reverse('city_add'))
        self.assertEqual(response.status_code, 302)  # редирект
        self.assertIn('/accounts/login/', response.url)
    
    def test_access_for_authenticated_user(self):
        """Тест доступа для авторизованных пользователей"""
        self.client.login(username='testuser', password='testpass123')
        response = self.client.get(reverse('city_list'))
        self.assertEqual(response.status_code, 200)
    
    def test_successful_login(self):
        """Тест успешного входа пользователя"""
        response = self.client.post(reverse('login'), {
            'username': 'testuser',
            'password': 'testpass123'
        })
        self.assertEqual(response.status_code, 302)  # редирект после успешного входа
    
    def test_logout_functionality(self):
        """Тест выхода из системы"""
        self.client.login(username='testuser', password='testpass123')
        response = self.client.post('/accounts/logout')
        self.assertIn(response.status_code, [301, 302])  # редирект после выхода


class UserProfileSignalTests(TestCase):
    def test_user_profile_created_via_signal(self):
        """Тест автоматического создания профиля через сигналы при создании пользователя"""
        user = User.objects.create_user(
            username='signaluser',
            password='testpass123'
        )
        
        # Проверяем что профиль создался автоматически
        self.assertTrue(hasattr(user, 'profile'))
        self.assertIsInstance(user.profile, Profile)
        self.assertEqual(user.profile.user, user)
        
        # Проверяем поля профиля
        self.assertTrue(hasattr(user.profile, 'bio'))
        self.assertTrue(hasattr(user.profile, 'location'))  


# Дополнительные тесты для проверки избранного хз надо ли
class FavoriteTests(TestCase):
    def setUp(self):
        self.client = Client()
        self.user1 = User.objects.create_user(username='user1', password='pass1')
        self.user2 = User.objects.create_user(username='user2', password='pass2')
        self.city = City.objects.create(
            name='Test City',
            country='Test Country',
            latitude=55.7558,
            longitude=37.6173
        )
    
    def test_add_city_to_favorites(self):
        """Тест добавления города в избранное"""
        favorite = Favorite.objects.create(user_id=self.user1, city_id=self.city)
        self.assertEqual(Favorite.objects.filter(user_id=self.user1).count(), 1)
        self.assertEqual(favorite.user_id, self.user1)
        self.assertEqual(favorite.city_id, self.city)