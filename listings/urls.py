from django.urls import path
from .views import (
    manage_ads, post_listing, edit_listing, delete_listing, 
    listing_detail, browse_listings, seller_listings,
    mark_as_sold, mark_as_available
)

urlpatterns = [
    # Post a new listing
    path('post/', post_listing, name='post_listing'),
    
    # Listing detail view
    path('listings/<int:listing_id>/', listing_detail, name='listing_detail'),
    
    # Browse all listings (home page)
    path('', browse_listings, name='browse_listings'),
    
    # Edit and delete listing
    path('<int:listing_id>/edit/', edit_listing, name='edit_listing'),
    path('<int:listing_id>/delete/', delete_listing, name='delete_listing'),
    
    # Manage user's ads
    path('manage/', manage_ads, name='manage_ads'),
    
    # View all listings by a specific seller
    path('seller/<int:user_id>/listings/', seller_listings, name='seller_listings'),
    
    # NEW: Mark listing as sold
    path('<int:listing_id>/mark-sold/', mark_as_sold, name='mark_as_sold'),
    
    # NEW: Mark listing as available (optional - to revert sold status)
    path('<int:listing_id>/mark-available/', mark_as_available, name='mark_as_available'),
]