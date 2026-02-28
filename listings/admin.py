from django.contrib import admin
from .models import Category, Listing, ListingImage, Feature
# Register your models here.

class ListingAdmin(admin.ModelAdmin):
    list_display = ('title', 'user', 'is_approved', 'views_count')
    list_editable = ('is_approved',)
admin.site.register(Category)
admin.site.register(Feature)
admin.site.register(Listing, ListingAdmin)
admin.site.register(ListingImage)