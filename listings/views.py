from django.shortcuts import render, redirect, get_object_or_404
from .forms import ListingForm
from django.forms import modelformset_factory
from django.contrib.auth.decorators import login_required
from .models import Listing, ListingImage
from django.db.models import F, Avg, Q, Case, When, IntegerField, Sum
from django.contrib import messages
import re
from django.contrib.auth.models import User
from urllib.parse import quote
from datetime import timedelta
from django.utils import timezone



@login_required
def post_listing(request):
    if request.method == 'POST':
        form = ListingForm(request.POST)

        if form.is_valid():
            listing = form.save(commit=False)
            listing.user = request.user
            listing.save()
            form.save_m2m()   # save ManyToMany (features)

            # Get all images from the request – they are sent under the name "images"
            uploaded_files = request.FILES.getlist('images')

            # Validate count
            if len(uploaded_files) < 5:
                messages.error(request, f'Please upload at least 5 images. You uploaded {len(uploaded_files)}.')
                listing.delete()
                return redirect('post_listing')

            if len(uploaded_files) > 15:
                messages.error(request, f'Maximum 15 images allowed. You uploaded {len(uploaded_files)}.')
                listing.delete()
                return redirect('post_listing')

            valid_types = ['image/jpeg', 'image/png', 'image/webp']
            max_size = 5 * 1024 * 1024   # 5MB
            saved_count = 0
            errors = []

            for img in uploaded_files:
                if img.content_type not in valid_types:
                    errors.append(f'{img.name} is not a valid image format. Use JPG, PNG, or WEBP.')
                    continue
                if img.size > max_size:
                    errors.append(f'{img.name} exceeds 5MB limit.')
                    continue

                ListingImage.objects.create(listing=listing, image=img)
                saved_count += 1

            if saved_count >= 5:
                messages.success(request, f'✅ Your listing "{listing.title}" has been posted! {saved_count} images uploaded.')
                return redirect('browse_listings')
            else:
                messages.error(request, f'❌ Only {saved_count} valid images. At least 5 are required.')
                for err in errors[:3]:
                    messages.error(request, err)
                listing.delete()
                return redirect('post_listing')
        else:
            for field, errors in form.errors.items():
                for err in errors:
                    messages.error(request, f'{field}: {err}')
    else:
        form = ListingForm()

    return render(request, 'listings/post_listing.html', {'form': form})

def browse_listings(request):
    # Start with approved & active listings that are available (not sold)
    listings = Listing.objects.filter(is_approved=True, is_active=True, status='available')

    # Annotate with 'featured_order: 0 if featured & active, 1 otherwise
    listings = listings.annotate(featured_order=Case(
        When(feature__active=True, then=0),
        default=1,
        output_field=IntegerField()
    ))
    
    # Get all filter parameters from URL
    query = request.GET.get('q')
    price_min = request.GET.get('price_min')
    price_max = request.GET.get('price_max')
    condition = request.GET.get('condition')
    featured = request.GET.get('featured')
    sort = request.GET.get('sort')
    
    # ==================== 1. BUDGET FILTER ====================
    if price_min:
        try:
            price_min = int(price_min)
            listings = listings.filter(price__gte=price_min)
        except (ValueError, TypeError):
            pass
    
    if price_max:
        try:
            price_max = int(price_max)
            # If price_max is 999999999 (our "Above 10M" marker), don't filter by max
            if price_max != 999999999:
                listings = listings.filter(price__lte=price_max)
        except (ValueError, TypeError):
            pass
    
    # ==================== 2. NEW ARRIVALS FILTER ====================
    if condition == 'new':
        days_limit = timezone.now() - timedelta(days=30)
        listings = listings.filter(created_at__gte=days_limit)
    
    # ==================== 3. FEATURED FILTER ====================
    if featured == 'true':
        listings = listings.filter(feature__active=True)
    
    # ==================== 4. SEARCH & SMART FILTERS ====================
    if query:
        q = query.lower()
        filters = Q()

        # Text Search (brand/model/title)
        filters &= (
            Q(brand__icontains=q) |
            Q(model__icontains=q) |
            Q(title__icontains=q) |
            Q(description__icontains=q)
        )

        # Price Under (e.g., "under 500000")
        match = re.search(r'under\s?(\d+)', q)
        if match:
            max_price = int(match.group(1))
            filters &= Q(price__lte=max_price)

        # Price Over (e.g., "over 1000000")
        match = re.search(r'over\s?(\d+)', q)
        if match:
            min_price = int(match.group(1))
            filters &= Q(price__gte=min_price)

        # Year detection (e.g., "2020")
        year_match = re.search(r'(20\d{2})', q)
        if year_match:
            year = int(year_match.group(1))
            filters &= Q(year=year)

        # Location Detection (Kenyan counties)
        locations = ['mombasa', 'kwale', 'kilifi', 'tana river', 'lamu', 'taita-taveta', 'garissa', 'wajir', 'mandera', 'marsabit', 'isiolo', 
        'meru', 'tharaka-nithi', 'embu', 'kitui', 'machakos', 'makueni', 'nyandarua', 'nyeri', 'kirinyaga', 'muranga', 'kiambu', 'turkana', 'west pokot', 'samburu', 
        'trans-nzoia', 'uasin gishu', 'elgeyo marakwet', 'nandi', 'baringo', 'laikipia', 'nakuru', 'narok', 'kajiado', 'kericho', 'bomet', 'kakamega', 'vihiga', 'bungoma', 
        'busia', 'siaya', 'kisumu', 'homa bay', 'migori', 'kisii', 'nyamira', 'nairobi']
        
        for loc in locations:
            if loc in q:
                filters &= Q(location__icontains=loc)

        # Transmission Detection
        if 'automatic' in q:
            filters &= Q(transmission='Automatic')
        if 'manual' in q:
            filters &= Q(transmission='Manual')

        # Condition Detection
        if 'new' in q:
            filters &= Q(condition='New')
        if 'used' in q:
            filters &= Q(condition='Used')

        listings = listings.filter(filters)
    
    # ==================== 5. SORTING ====================
    if sort == 'price_asc':
        # Price low to high (but keep featured at top)
        listings = listings.order_by('price', 'featured_order', '-created_at')
    elif sort == 'price_desc':
        # Price high to low (but keep featured at top)
        listings = listings.order_by('-price', 'featured_order', '-created_at')
    else:
        # Default sorting: Featured first, then newest
        listings = listings.order_by('featured_order', '-created_at')
    
    return render(request, 'listings/browse.html', {'listings': listings})

# View listing detail
def listing_detail(request, listing_id):
    listing = get_object_or_404(Listing, id=listing_id, is_active=True, is_approved=True)

    Listing.objects.filter(id=listing.id).update(
        views_count=F('views_count') + 1
    )
    
    # Get seller information
    seller = listing.user
    
    # Get total listings count for this seller (approved and active)
    user_listings_count = Listing.objects.filter(
        user=seller, 
        is_active=True, 
        is_approved=True
    ).count()
    
    # Try to import Review model from users app
    try:
        from users.models import Review  # Update 'users' to your actual app name
        seller_reviews = Review.objects.filter(seller=seller)
        total_reviews_count = seller_reviews.count()
        
        if total_reviews_count > 0:
            seller_rating = seller_reviews.aggregate(Avg('rating'))['rating__avg']
        else:
            seller_rating = 5.0
    except ImportError:
        # If Review model doesn't exist or can't be imported, use defaults
        total_reviews_count = 0
        seller_rating = 5.0

    # Prepare WhatsApp Message Safely
    message = (
        f"Hi, I saw your car on Chrandi Motors.\n "
        f"Brand: {listing.brand}\n "
        f"Model: {listing.model}\n "
        f"Year: {listing.year}\n"
        f"Price: KES {listing.price}\n"
        f"Link: {request.build_absolute_uri()}"
    )
    encoded_message = quote(message)

    # Prepare whatsapp number in international format
    phone = str(listing.whatsapp_number)
    if phone.startswith('0'):
        phone = '254' + phone[1:]
    if phone.startswith('+'):
        phone = phone[1:]

    whatsapp_link = f"https://wa.me/{phone}?text={encoded_message}"

    current_url = request.build_absolute_uri()
    share_message = (
        f"{listing.brand} {listing.model} ({listing.year})\n"
        f"Price: KES {listing.price}\n"
        f"Location: {listing.location}\n"
        f"Condition: {listing.condition}\n"
        f"Transmission: {listing.transmission}\n\n"
        f"View more: {request.build_absolute_uri()}"
    )
    whatsapp_share = f"https://wa.me/?text={quote(share_message)}"

    return render(request, 'listings/detail.html', {
        'listing': listing, 
        'whatsapp_link': whatsapp_link, 
        'whatsapp_share': whatsapp_share, 
        'current_url': current_url,
        'user_listings_count': user_listings_count,
        'seller_rating': seller_rating,
        'total_reviews_count': total_reviews_count,
    })

# Edit listing
@login_required
def edit_listing(request, listing_id):
    listing = get_object_or_404(Listing, id=listing_id, user=request.user)
    if request.method == 'POST':
        form = ListingForm(request.POST, instance=listing)
        if form.is_valid():
            form.save()
            messages.success(request, 'Listing updated successfully!')
            return redirect('listing_detail', listing_id=listing.id)
    else:
        form = ListingForm(instance=listing)
    return render(request, 'listings/edit_listing.html', {'form': form})

# Delete listing
@login_required
def delete_listing(request, listing_id):
    listing = get_object_or_404(Listing, id=listing_id, user=request.user)
    listing.is_active=False
    listing.save()
    messages.success(request, 'Listing deleted successfully!')
    return redirect('browse_listings')

# Seller manage ads
@login_required
def manage_ads(request):
    listings = Listing.objects.filter(user=request.user)
    
    # Calculate counts for stats
    total_listings = listings.count()
    total_views = listings.aggregate(total=Sum('views_count'))['total'] or 0
    approved_count = listings.filter(is_approved=True).count()
    pending_count = listings.filter(is_approved=False).count()
    
    # Get filter from URL
    filter_type = request.GET.get('filter', 'all')
    
    if filter_type == 'approved':
        listings = listings.filter(is_approved=True)
    elif filter_type == 'pending':
        listings = listings.filter(is_approved=False)
    elif filter_type == 'sold':
        listings = listings.filter(status='sold')
    else:
        listings = listings  # 'all' - show all listings
    
    return render(request, 'listings/manage_ads.html', {
        'listings': listings,
        'total_views': total_views,
        'approved_count': approved_count,
        'pending_count': pending_count,
        'active_filter': filter_type
    })

# NEW: Mark listing as sold
@login_required
def mark_as_sold(request, listing_id):
    listing = get_object_or_404(Listing, id=listing_id, user=request.user)
    
    # Only allow marking as sold if it's not already sold
    if listing.status == 'sold':
        messages.warning(request, 'This listing is already marked as sold.')
    else:
        listing.status = 'sold'
        listing.save()
        messages.success(request, f'"{listing.title}" has been marked as sold. It will no longer appear in search results.')
    
    return redirect('manage_ads')

# NEW: Mark listing as available (if you want to allow reverting)
@login_required
def mark_as_available(request, listing_id):
    listing = get_object_or_404(Listing, id=listing_id, user=request.user)
    
    listing.status = 'available'
    listing.save()
    messages.success(request, f'"{listing.title}" has been marked as available again.')
    
    return redirect('manage_ads')

def seller_listings(request, user_id):
    seller = get_object_or_404(User, id=user_id)
    listings = Listing.objects.filter(user=seller, is_approved=True, is_active=True, status='available')
    return render(request, 'listings/seller_listings.html', {
        'seller': seller,
        'listings': listings
    })