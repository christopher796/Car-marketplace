from django.urls import path
from . import views
from django.contrib.auth import views as auth_views

urlpatterns = [
    path('register/', views.register_view, name='register'),
    path('login/', views.login_view, name='login'),
    path('logout/', views.logout_view, name='logout'),
    path('seller/<int:user_id>/', views.seller_profile, name='seller_profile'),
    path('review/<int:user_id>/', views.add_review, name='add_review'),
    path('get_verified/', views.get_verified, name='get_verified')
]
