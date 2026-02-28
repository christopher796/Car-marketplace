from django.shortcuts import render
from django.contrib.admin.views.decorators import staff_member_required
from django.contrib.auth import get_user_model
from listings.models import Listing
from django.db.models import Count

# Create your views here.
def home(request):
    return render(request, 'home.html')
    
@staff_member_required
def dashboard(request):
    User = get_user_model()
    total_users = User.objects.count()
    total_ads = Listing.objects.count()
    approved_ads = Listing.objects.filter(is_approved=True).count()
    pending_ads = Listing.objects.filter(is_approved=False).count()
    top_brands = {
        Listing.objects
        .values('brand')
        .annotate(total=Count('id'))
        .order_by('-total')[:5]
    }
    most_viewed = Listing.objects.order_by('-views_count')[:5]
    context = {
        'total_users': total_users,
        'total_ads': total_ads,
        'approved_ads': approved_ads,
        'pending_ads': pending_ads,
        'top_brands': top_brands,
        'most_viewed': most_viewed
    }
    return render(request, 'dashboard.html', context)
    