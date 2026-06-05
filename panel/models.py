import uuid
from datetime import timedelta
from django.db import models

# Create your models here.

class Survey(models.Model):
    title = models.CharField(max_length=255)
    description = models.TextField(blank=True, null=True)
    launch_date = models.DateTimeField(auto_now_add=True)
    is_active = models.BooleanField(default=True)

@property
def deadline(self):
    return self.launch_date + timedelta(days=15)

def __str__(self):
    return f"{self.title} (Deadline: {self.deadline})"

class Respondent(models.Model):
    STATUS_CHOICES = [
        ('active', 'Active'),
        ('cooloff', 'Cooloff'),
        ('inactive', 'Inactive'),
    ]

    unique_id =models.CharField(max_length=255, unique=True, blank=True)
    name=models.CharField(max_length=255)
    email=models.EmailField(unique=True)
    phone=models.CharField(max_length=10)
    city=models.CharField(max_length=100)
    category=models.CharField(max_length=100, blank=True)
    status=models.CharField(max_length=20, choices=STATUS_CHOICES, default='active')

    # self-referential foreignKey to track who referred who
    referred_by = models.ForeignKey('self', on_delete=models.SET_NULL, null=True, blank=True, related_name='referrals')
    referral_code = models.UUIDField(default=uuid.uuid4, editable=False, unique=True)
    cool_off_until = models.DateTimeField(null=True, blank=True)

    def save(self, *args, **kwargs):
        super().save(*args, **kwargs)
        #Automatically generate the concave insigts unique_id format
        if not self.unique_id:
            self.unique_id = f"CI-{self.id:04d}"
            self.save(update_fields=['unique_id'])

    def __str__(self):
        return f"{self.name} ({self.unique_id})"        