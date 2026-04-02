from django.urls import path
from .views import home
from . import views

urlpatterns = [
    path('', home, name='home'),
    path('dashboard/', views.dashboard, name='dashboard'),
    path('google46505a87f900d8a9.html', views.google_verification, name='google_verification')
]
