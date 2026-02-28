from django.urls import path
from . import views

urlpatterns = [
    path('feature/<int:listing_id>/', views.feature_listing, name='feature_listing'),
    path('callback/', views.mpesa_callback, name='mpesa_callback'),   
]
