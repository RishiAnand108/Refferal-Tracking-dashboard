# panel/models.py
import uuid
from django.db import models
from django.contrib.auth.models import User
from django.utils import timezone
from datetime import timedelta


def generate_unique_id():
    import random
    year = timezone.now().year
    num  = random.randint(1000, 9999)
    return f"CI-{year}-{num}"


class Respondent(models.Model):
    CITY_CHOICES = [
        ('Mumbai',    'Mumbai'),
        ('Delhi',     'Delhi'),
        ('Bangalore', 'Bangalore'),
        ('Pune',      'Pune'),
        ('Chennai',   'Chennai'),
        ('Hyderabad', 'Hyderabad'),
        ('Kolkata',   'Kolkata'),
    ]
    CATEGORY_CHOICES = [
        ('Healthcare',  'Healthcare'),
        ('Finance',     'Finance'),
        ('Retail',      'Retail'),
        ('FMCG',        'FMCG'),
        ('Technology',  'Technology'),
        ('Other',       'Other'),
    ]
    STATUS_CHOICES = [
        ('active',   'Active'),
        ('cooloff',  'Cool-off'),
        ('inactive', 'Inactive'),
    ]

    unique_id      = models.CharField(max_length=20, unique=True,
                                      default=generate_unique_id)
    name           = models.CharField(max_length=100)
    email          = models.EmailField(unique=True)
    phone          = models.CharField(max_length=15)
    city           = models.CharField(max_length=50, choices=CITY_CHOICES)
    category       = models.CharField(max_length=50, choices=CATEGORY_CHOICES,
                                      default='Other')
    status         = models.CharField(max_length=20, choices=STATUS_CHOICES,
                                      default='active')
    referred_by    = models.ForeignKey('self', null=True, blank=True,
                                       on_delete=models.SET_NULL,
                                       related_name='referrals')
    referral_code  = models.UUIDField(default=uuid.uuid4, unique=True,
                                      editable=False)
    cool_off_until = models.DateField(null=True, blank=True)
    date_joined    = models.DateTimeField(default=timezone.now)
    notes          = models.TextField(blank=True)
    ai_category    = models.CharField(max_length=50, blank=True)

    def __str__(self):
        return f"{self.name} ({self.unique_id})"

    def is_in_cooloff(self):
        if self.cool_off_until:
            return timezone.now().date() <= self.cool_off_until
        return False

    def set_cooloff(self):
        self.cool_off_until = timezone.now().date() + timedelta(days=90)
        self.status = 'cooloff'
        self.save()

    class Meta:
        ordering = ['-date_joined']


class Survey(models.Model):
    title      = models.CharField(max_length=200)
    start_date = models.DateField()
    end_date   = models.DateField()
    is_active  = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.title

    def days_remaining(self):
        remaining = (self.end_date - timezone.now().date()).days
        return max(0, remaining)

    class Meta:
        ordering = ['-created_at']


class ReferralStatus(models.Model):
    STAGE_CHOICES = [
        ('lead',       'Lead'),
        ('fit',        'Fit'),
        ('completion', 'Completion'),
    ]

    referrer     = models.ForeignKey(Respondent, on_delete=models.CASCADE,
                                     related_name='referrals_made')
    referred     = models.ForeignKey(Respondent, on_delete=models.CASCADE,
                                     related_name='referral_received')
    survey       = models.ForeignKey(Survey, on_delete=models.CASCADE,
                                     null=True, blank=True)
    stage        = models.CharField(max_length=20, choices=STAGE_CHOICES,
                                    default='lead')
    bonus_amount = models.DecimalField(max_digits=8, decimal_places=2,
                                       default=0.00)
    is_paid      = models.BooleanField(default=False)
    created_at   = models.DateTimeField(auto_now_add=True)
    updated_at   = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"{self.referrer} → {self.referred} ({self.stage})"

    class Meta:
        ordering = ['-created_at']
        unique_together = ['referrer', 'referred']