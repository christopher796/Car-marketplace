from django.urls import path
from .views import manage_ads, post_listing, edit_listing, delete_listing, listing_detail, browse_listings, seller_listings

urlpatterns = [
    path('post/', post_listing, name='post_listing'),
    path('listings/<int:listing_id>/', listing_detail, name='listing_detail'),
    path('', browse_listings, name='browse_listings'),
    path('<int:listing_id>/edit/', edit_listing, name='edit_listing'),
    path('<int:listing_id>/delete/', delete_listing, name='delete_listing'),
    path('manage/', manage_ads, name='manage_ads'),
    path('seller/<int:user_id>/listings/', seller_listings, name='seller_listings')
]