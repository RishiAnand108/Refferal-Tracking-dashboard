# panel/admin.py
from django.contrib import admin
from .models import Respondent, Survey, ReferralStatus


@admin.register(Respondent)
class RespondentAdmin(admin.ModelAdmin):
    list_display    = ['unique_id', 'name', 'email', 'phone',
                       'city', 'category', 'status',
                       'referred_by', 'cool_off_until', 'date_joined']
    list_filter     = ['status', 'category', 'city']
    search_fields   = ['name', 'email', 'phone', 'unique_id', 'city']
    ordering        = ['-date_joined']
    readonly_fields = ['unique_id', 'referral_code', 'date_joined']
    date_hierarchy  = 'date_joined'

    fieldsets = (
        ('Basic Info', {
            'fields': ('unique_id', 'name', 'email', 'phone')
        }),
        ('Classification', {
            'fields': ('city', 'category', 'status')
        }),
        ('Referral', {
            'fields': ('referred_by', 'referral_code', 'cool_off_until')
        }),
        ('AI', {
            'fields': ('notes', 'ai_category')
        }),
    )


@admin.register(Survey)
class SurveyAdmin(admin.ModelAdmin):
    list_display  = ['title', 'start_date', 'end_date',    # ← fixed
                     'is_active', 'days_remaining']
    list_filter   = ['is_active', 'start_date']            # ← fixed
    search_fields = ['title']


@admin.register(ReferralStatus)
class ReferralStatusAdmin(admin.ModelAdmin):
    list_display  = ['referrer', 'referred', 'survey',
                     'stage', 'bonus_amount', 'is_paid', 'created_at']
    list_filter   = ['stage', 'is_paid']
    search_fields = ['referrer__name', 'referred__name']
    ordering      = ['-created_at']