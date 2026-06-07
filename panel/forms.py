# panel/forms.py
from django import forms
from django.utils import timezone
from .models import Respondent


class SignupForm(forms.ModelForm):
    class Meta:
        model  = Respondent
        fields = ['name', 'email', 'phone', 'city', 'category']
        widgets = {
            'name': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'Full Name'
            }),
            'email': forms.EmailInput(attrs={
                'class': 'form-control',
                'placeholder': 'Email Address'
            }),
            'phone': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': '10-digit mobile number'
            }),
            'city': forms.Select(attrs={
                'class': 'form-select'
            }),
            'category': forms.Select(attrs={
                'class': 'form-select'
            }),
        }

    def clean_email(self):
        email = self.cleaned_data.get('email')
        if Respondent.objects.filter(email=email).exists():
            raise forms.ValidationError(
                'This email is already registered in our panel.'
            )
        return email

    def clean_phone(self):
        phone = self.cleaned_data.get('phone')
        digits = ''.join(filter(str.isdigit, phone))
        if len(digits) != 10:
            raise forms.ValidationError(
                'Phone number must be exactly 10 digits.'
            )
        return digits

    def clean(self):
        cleaned = super().clean()
        email   = cleaned.get('email')
        if email:
            existing = Respondent.objects.filter(
                email=email
            ).first()
            if existing and existing.is_in_cooloff():
                raise forms.ValidationError(
                    f'You are in a 3-month cool-off period '
                    f'until {existing.cool_off_until}. '
                    f'You cannot join a new survey until then.'
                )
        return cleaned