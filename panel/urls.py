# panel/urls.py
from django.urls import path
from . import views

urlpatterns = [
    path('',                            views.home,           name='home'),
    path('login/',                      views.staff_login,    name='staff-login'),
    path('logout/',                     views.staff_logout,   name='staff-logout'),
    path('refer/<uuid:referral_code>/', views.track_referral, name='track-referral'),
    path('signup/',                     views.signup_view,    name='signup'),
    path('dashboard/',                  views.dashboard,      name='dashboard'),
    path('export/',                     views.export_data,    name='export'),
    path('ai-categorize/',              views.ai_categorize,  name='ai-categorize'),
    path('update-stage/<int:pk>/',      views.update_stage,   name='update-stage'),
    path('add-respondent/',             views.add_respondent, name='add-respondent'),
]