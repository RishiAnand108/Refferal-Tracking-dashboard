# users/models.py
from django.contrib.auth.models import AbstractUser
from django.db import models


class CustomUser(AbstractUser):
    CITY_CHOICES = [
        ('Mumbai',    'Mumbai'),
        ('Delhi',     'Delhi'),
        ('Bangalore', 'Bangalore'),
        ('Pune',      'Pune'),
        ('Chennai',   'Chennai'),
        ('Hyderabad', 'Hyderabad'),
        ('Kolkata',   'Kolkata'),
    ]
    ROLE_CHOICES = [
        ('staff',        'Staff'),
        ('respondent',   'Respondent'),
        ('admin',        'Admin'),
    ]

    phone = models.CharField(max_length=15, blank=True)
    city  = models.CharField(max_length=50, choices=CITY_CHOICES, blank=True)
    role  = models.CharField(max_length=20, choices=ROLE_CHOICES, default='staff')

    def __str__(self):
        return f"{self.username} ({self.role})"