from django import forms
from .models import City
from django.contrib.auth.models import User
from .models import Profile, SupportRequest

class CityForm(forms.ModelForm):
    class Meta:
        model = City
        fields = ['name', 'country', 'latitude', 'longitude', 'photo']
        widgets = {
            "name": forms.TextInput(attrs={"class": "form-control", "placeholder": "Название города"}),
            "country": forms.TextInput(attrs={"class": "form-control", "placeholder": "Страна"}),
            "latitude": forms.NumberInput(attrs={"class": "form-control", "step": "any"}),
            "longitude": forms.NumberInput(attrs={"class": "form-control", "step": "any"}),
        }

class UserUpdateForm(forms.ModelForm):
    email = forms.EmailField(
        label="Электронная почта",
        required=False,  # ← ДОБАВЬТЕ ЭТО
        help_text="Необязательное поле"  # ← опционально, для подсказки
    )
    
    class Meta:
        model = User
        fields = ['username', 'email', 'first_name', 'last_name']

class ProfileUpdateForm(forms.ModelForm):
    class Meta:
        model = Profile
        fields = ['avatar', 'bio', 'location', 'birth_date']
        widgets = {
            'bio': forms.Textarea(attrs={'rows': 4}),
            'birth_date': forms.DateInput(attrs={'type': 'date'})
        }

class SupportRequestForm(forms.ModelForm):
    class Meta:
        model = SupportRequest
        fields = ['name', 'email', 'subject', 'message']
        widgets = {
            'name': forms.TextInput(attrs={'placeholder': 'Ваше имя'}),
            'email': forms.EmailInput(attrs={'placeholder': 'Ваш email'}),
            'subject': forms.TextInput(attrs={'placeholder': 'Тема сообщения'}),
            'message': forms.Textarea(attrs={
                'placeholder': 'Опишите вашу проблему или вопрос',
                'rows': 5
            }),
        }
        labels = {
            'name': 'Имя',
            'email': 'Email',
            'subject': 'Тема',
            'message': 'Сообщение',
        }

class SupportResponseForm(forms.ModelForm):
    class Meta:
        model = SupportRequest
        fields = ['admin_response', 'status']
        widgets = {
            'admin_response': forms.Textarea(attrs={'rows': 5}),
        }
        labels = {
            'admin_response': 'Ответ пользователю',
            'status': 'Статус заявки',
        }
