from django.core.exceptions import ValidationError


def validate_latitude(value):
    if value < -90 or value > 90:
        raise ValidationError("Широта должна быть в диапазоне от -90 до 90.")


def validate_longitude(value):
    if value < -180 or value > 180:
        raise ValidationError("Долгота должна быть в диапазоне от -180 до 180.")
