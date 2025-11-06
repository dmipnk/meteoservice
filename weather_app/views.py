from django.shortcuts import render, get_object_or_404, redirect
from .models import City, WeatherForecast, Favorite  # ← ДОБАВИЛ Favorite
from django.views.generic import DetailView, CreateView, ListView, UpdateView, DeleteView
from django.urls import reverse_lazy
from .forms import CityForm, SupportRequestForm, SupportResponseForm
from django.db import models
from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth import login
from django.contrib.auth.decorators import login_required
from django.utils.decorators import method_decorator
from django.core.paginator import Paginator
from django.contrib import messages
from django.contrib.messages.views import SuccessMessageMixin
from .forms import UserUpdateForm, ProfileUpdateForm
from .models import Profile, SupportRequest
from django.core.exceptions import PermissionDenied
from django.contrib.auth.mixins import UserPassesTestMixin
from django.conf import settings
from django.core.mail import send_mail
from django.utils import timezone

class AdminRequiredMixin(UserPassesTestMixin):
    def test_func(self):
        return self.request.user.is_authenticated and self.request.user.is_staff
    
    def handle_no_permission(self):
        messages.error(self.request, "❌ Только администраторы могут выполнять это действие.")
        return redirect('city_list')
# Create your views here.

def city_list(request):
    cities = City.active.all() 
    # фильтр по названию города
    name = request.GET.get("name")
    if name:
        cities = cities.filter(name__icontains=name)

    # фильтр по стране
    country = request.GET.get("country")
    if country:
        cities = cities.filter(country__icontains=country)

    # сортировка
    sort = request.GET.get("sort")
    if sort == "name":
        cities = cities.order_by("name")
    elif sort == "-name":
        cities = cities.order_by("-name")
    elif sort == "country":
        cities = cities.order_by("country")
    elif sort == "-country":
        cities = cities.order_by("-country")
    
    # ПАГИНАЦИЯ
    paginator = Paginator(cities, 10)
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)
    
    return render(request, "city_list.html", {
        "cities": page_obj,
        "page_obj": page_obj
    })

def forecast_list(request):
    forecasts = (
        WeatherForecast.objects
        .select_related("city_id")
        .prefetch_related("city_id__users")
    )
    return render(request, "forecast_list.html", {"forecasts": forecasts})

class CityDetailView(DetailView):
    model = City
    template_name = "city_detail.html"
    context_object_name = "city"

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        # Добавляем прогнозы погоды для выбранного города
        context["forecasts"] = WeatherForecast.objects.filter(city_id=self.object)
        # Проверяем, есть ли город в избранном у текущего пользователя
        if self.request.user.is_authenticated:
            context["is_favorite"] = Favorite.objects.filter(
                user_id=self.request.user, 
                city_id=self.object
            ).exists()
        return context
    
@method_decorator(login_required, name='dispatch')   
class CityCreateView(AdminRequiredMixin, SuccessMessageMixin, CreateView):
    model = City
    form_class = CityForm
    template_name = "city_form.html"
    success_message = "Город успешно добавлен"
    success_url = reverse_lazy("city_list")

class CitySearchView(ListView):
    model = City
    template_name = "city_search.html"
    context_object_name = "cities"

    def get_queryset(self):
        queryset = City.objects.all()
        query = self.request.GET.get("q")
        order = self.request.GET.get("order")

        if query:
            queryset = queryset.filter(
                models.Q(name__icontains=query) | models.Q(country__icontains=query)
            )

        if order == "asc":
            queryset = queryset.order_by("name")
        elif order == "desc":
            queryset = queryset.order_by("-name")

        return queryset

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["query"] = self.request.GET.get("q", "")
        context["order"] = self.request.GET.get("order", "")
        return context

# МИКСИН ДЛЯ ПРОВЕРКИ ПРАВ
class UserIsOwnerMixin:
    """Миксин для проверки что пользователь - владелец объекта"""
    
    def get_object(self, queryset=None):
        obj = super().get_object(queryset)
        if not self.request.user.is_authenticated:
            raise PermissionDenied("Вы должны быть авторизованы")
        # Проверяем, есть ли у пользователя этот город в избранном
        if not Favorite.objects.filter(user_id=self.request.user, city_id=obj).exists():
            raise PermissionDenied("У вас нет прав для редактирования этого города")
        return obj

# ОБНОВЛЕННЫЕ VIEWS С ПРОВЕРКОЙ ПРАВ
@method_decorator(login_required, name='dispatch')   
class CityUpdateView(AdminRequiredMixin,  SuccessMessageMixin, UpdateView):  # ← ДОБАВИЛ UserIsOwnerMixin
    model = City
    fields = ["name", "country", "latitude", "longitude", "photo"]
    template_name = "city_form.html"
    success_url = reverse_lazy("city_list")
    success_message = "✏️ Город успешно обновлен!"

@method_decorator(login_required, name='dispatch')   
class CityDeleteView(AdminRequiredMixin,  SuccessMessageMixin, DeleteView):  # ← ДОБАВИЛ UserIsOwnerMixin
    model = City
    template_name = "city_confirm_delete.html"
    success_message = "🗑️ Город успешно удален"
    success_url = reverse_lazy("city_list")

def register(request):
    if request.method == 'POST':
        form = UserCreationForm(request.POST)
        if form.is_valid():
            user = form.save()
            login(request, user)
            messages.success(request, '🎉 Вы успешно зарегистрировались! Добро пожаловать!')
            return redirect('city_list')
        else:
            messages.error(request, '❌ Пожалуйста, исправьте ошибки в форме.')
    else:
        form = UserCreationForm()
    return render(request, 'registration/register.html', {'form': form})

def home(request):
    return redirect('city_list')

@login_required
def profile(request):
    # Создаем профиль если его нет
    #if not hasattr(request.user, 'profile'):
    #    Profile.objects.create(user=request.user)
    profile, created = Profile.objects.get_or_create(user=request.user)
    if request.method == 'POST':
        user_form = UserUpdateForm(request.POST, instance=request.user)
        profile_form = ProfileUpdateForm(
            request.POST, 
            request.FILES, 
            instance=request.user.profile
        )
        
        if user_form.is_valid() and profile_form.is_valid():
            user_form.save()
            profile_form.save()
            messages.success(request, '✅ Ваш профиль успешно обновлен!')
            return redirect('profile')
        else:
            messages.error(request, '❌ Пожалуйста, исправьте ошибки в форме.')
    else:
        user_form = UserUpdateForm(instance=request.user)
        profile_form = ProfileUpdateForm(instance=request.user.profile)
    
    context = {
        'user_form': user_form,
        'profile_form': profile_form
    }
    
    return render(request, 'profile.html', context)

# ДОБАВЬТЕ ЭТИ ФУНКЦИИ В ВАШ views.py

@login_required
def add_favorite(request, pk):
    """Добавить город в избранное"""
    city = get_object_or_404(City, pk=pk)
    favorite, created = Favorite.objects.get_or_create(
        user_id=request.user,
        city_id=city
    )
    if created:
        messages.success(request, f'⭐ Город {city.name} добавлен в избранное!')
    else:
        messages.info(request, f'ℹ️ Город {city.name} уже в избранном')
    return redirect('city_detail', pk=pk)

@login_required
def remove_favorite(request, pk):
    """Удалить город из избранного"""
    city = get_object_or_404(City, pk=pk)
    Favorite.objects.filter(user_id=request.user, city_id=city).delete()
    messages.success(request, f'🗑️ Город {city.name} удален из избранного')
    return redirect('city_detail', pk=pk)

@login_required
def my_favorites(request):
    """Страница с избранными городами пользователя"""
    # Получаем только города из избранного текущего пользователя
    favorite_cities = City.objects.filter(
        favorite__user_id=request.user  # используем ваши названия полей
    ).distinct()
    
    return render(request, 'my_favorites.html', {
        'favorite_cities': favorite_cities
    })

def support_request(request):
    if request.method == 'POST':
        form = SupportRequestForm(request.POST)
        if form.is_valid():
            support_request = form.save(commit=False)
            # Если пользователь авторизован, связываем заявку с ним
            if request.user.is_authenticated:
                support_request.user = request.user
                support_request.email = request.user.email  # используем email пользователя
            
            support_request.save()
            
            # Отправляем email уведомление
            try:
                send_mail(
                    f'Новая заявка в поддержку: {support_request.subject}',
                    f'''Поступила новая заявка в поддержку:
                    
Имя: {support_request.name}
Email: {support_request.email}
Тема: {support_request.subject}
Сообщение: {support_request.message}

Для ответа перейдите в админ-панель.
                    ''',
                    settings.DEFAULT_FROM_EMAIL,
                    [settings.SUPPORT_EMAIL],  # email сотрудника
                    fail_silently=False,
                )
            except Exception as e:
                # Если отправка email не удалась, просто логируем ошибку
                print(f"Ошибка отправки email: {e}")
            
            messages.success(request, '✅ Ваше сообщение отправлено! Мы ответим вам в ближайшее время.')
            return redirect('support_request')
    else:
        # Если пользователь авторизован, предзаполняем данные
        initial_data = {}
        if request.user.is_authenticated:
            initial_data = {
                'name': request.user.get_full_name() or request.user.username,
                'email': request.user.email,
            }
        form = SupportRequestForm(initial=initial_data)
    
    return render(request, 'support/request.html', {'form': form})

@login_required
def support_dashboard(request):
    """Панель управления заявками для сотрудников"""
    if not request.user.is_staff:
        messages.error(request, '❌ У вас нет доступа к этой странице.')
        return redirect('city_list')
    
    requests = SupportRequest.objects.all()
    
    # Фильтрация по статусу
    status_filter = request.GET.get('status')
    if status_filter:
        requests = requests.filter(status=status_filter)
    
    return render(request, 'support/dashboard.html', {
        'requests': requests,
        'status_choices': SupportRequest.STATUS_CHOICES,
        'current_status': status_filter
    })

@login_required
def support_request_detail(request, pk):
    """Детальная страница заявки для ответа"""
    if not request.user.is_staff:
        messages.error(request, '❌ У вас нет доступа к этой странице.')
        return redirect('city_list')
    
    support_request = get_object_or_404(SupportRequest, pk=pk)
    
    if request.method == 'POST':
        form = SupportResponseForm(request.POST, instance=support_request)
        if form.is_valid():
            response = form.save(commit=False)
            response.responded_by = request.user
            response.responded_at = timezone.now()
            response.save()
            
            # Отправляем ответ пользователю
            try:
                send_mail(
                    f'Ответ на вашу заявку: {response.subject}',
                    f'''Здравствуйте, {response.name}!

Спасибо за ваше обращение в поддержку.

Наш ответ:
{response.admin_response}

С уважением,
Служба поддержки Метеосервиса
                    ''',
                    settings.DEFAULT_FROM_EMAIL,
                    [response.email],
                    fail_silently=False,
                )
                messages.success(request, '✅ Ответ отправлен пользователю!')
            except Exception as e:
                messages.error(request, f'❌ Ошибка отправки email: {e}')
            
            return redirect('support_dashboard')
    else:
        form = SupportResponseForm(instance=support_request)
    
    return render(request, 'support/detail.html', {
        'support_request': support_request,
        'form': form
    })
