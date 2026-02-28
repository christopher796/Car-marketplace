from django.contrib import admin
from .models import User, Profile, Report, Review

# Register your models here.
#admin.site.register(User)
class ProfileAdmin(admin.ModelAdmin):
    list_display = ('user', 'phone', 'is_verified', 'location')
    list_editable = ('is_verified',)

admin.site.register(Profile, ProfileAdmin)
admin.site.register(Report)
admin.site.register(Review)

