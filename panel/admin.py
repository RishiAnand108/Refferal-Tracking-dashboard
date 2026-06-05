from django.contrib import admin
from .models import Respondent, Survey

# Register your models here.

@admin.register(Survey)
class SurveyAdmin(admin.ModelAdmin):
    list_display = ['title', 'launch_date', 'is_active', 'deadline']
    list_filter = ['is_active', 'launch_date']
    search_fields = ['title']


@admin.register(Respondent)
class RespondentAdmin(admin.ModelAdmin):
    list_display=('unique_id', 'name','city','category','status','cool_off_until')
    search_fields = ['name','unique_id','city','email','phone']
    list_filter = ['status','city','category']
    readonly_fields = ['unique_id','referral_code']

    