from django.contrib import admin
from .models import Category, Listing, ListingImage, Feature
# Register your models here.
class ListingAdmin(admin.ModelAdmin):
    list_display = ['title', 'user', 'price', 'is_approved', 'is_active', 'created_at']
    list_filter = ['is_approved', 'is_active', 'condition']
    search_fields = ['title', 'brand', 'model']
    list_editable = ['is_approved']
    actions = ['approve_listings']
    
    def approve_listings(self, request, queryset):
        queryset.update(is_approved=True)
        self.message_user(request, f'{queryset.count()} listings approved.')
    approve_listings.short_description = "Approve selected listing"
admin.site.register(Category)
admin.site.register(Feature)
admin.site.register(Listing, ListingAdmin)
admin.site.register(ListingImage)