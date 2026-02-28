from django.shortcuts import render, redirect, get_object_or_404
from .forms import ListingForm, ListingImageForm
from django.forms import modelformset_factory
from django.contrib.auth.decorators import login_required
from  .models import Listing, ListingImage
from django.db.models import F
import re
from django.db.models import Q, Case, When, IntegerField
from django.contrib.auth.models import User
from urllib.parse import quote



# Post a new listing
"""@login_required
def post_listing(request):
    ImageFormSet = modelformset_factory(ListingImage, form=ListingImageForm, extra=3)
    
    if request.method == 'POST':
        form = ListingForm(request.POST)
        formset = ImageFormSet(request.POST, request.FILES, queryset=ListingImage.objects.none())
        
        if form.is_valid() and formset.is_valid():
            listing = form.save(commit=False)
            listing.user = request.user
            listing.is_approved = False
            listing.save()
            
            for f in formset.cleaned_data:
                if f:
                    image = f['image']
                    photo = ListingImage(listing=listing, image=image)
                    photo.save()
            return redirect('home')
    else:
        form = ListingForm()
        formset = ImageFormSet(queryset=ListingImage.objects.none())
    
    return render(request, 'listings/post_listing.html', {'form': form, 'formset': formset})"""

@login_required
def post_listing(request):
    if request.method == 'POST':
        form = ListingForm(request.POST)
        image_form = ListingImageForm(request.POST, request.FILES)
        if form.is_valid() and image_form.is_valid():

            listing = form.save(commit=False)
            listing.user = request.user
            listing.save()
            form.save_m2m() # Required for features

            # Loop through uploaded images
            for i in range(1, 16):
                img = image_form.cleaned_data.get(f"image{i}")
                if img:
                    ListingImage.objects.create(listing=listing, image=img)

            return redirect('browse_listings')
    else:
        form = ListingForm()
        image_form = ListingImageForm()
    return render(request, 'listings/post_listing.html', {
        'form': form,
        'image_form': image_form
    })


# Browse approved listings
def browse_listings(request):
    # Start with approved & active listings
    listings = Listing.objects.filter(is_approved=True, is_active=True)

    # Annotate with 'featured_order: 0 if featured & active, 1 otherwise
    listings = listings.annotate(featured_order=Case(
        When(feature__active=True, then=0),
        default=1,
        output_field=IntegerField()
    )).order_by('featured_order', '-created_at') # Featured first, then newest
    
    query = request.GET.get('q')

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

        # Price Under 
        match = re.search(r'under\s?(\d+)', q)
        if match:
            max_price = int(match.group(1))
            filters &= Q(price__lte=max_price)

        # Price over
        match = re.search(r'over\s?(\d)', q)
        if match:
            min_price = int(match.group(1))
            filters &= Q(price__gte=min_price)

        # Year detection
        year_match = re.search(r'(20\d{2})', q)
        if year_match:
            year = int(year_match.group(1))
            filters &= Q(year=year)

        # Location Detection
        locations = ['mombasa', 'kwale', 'kilifi', 'tana river', 'lamu', 'taita-taveta', 'garissa', 'wajir', 'mandera', 'marsabit', 'isiolo', 
        'meru', 'tharaka-nithi', 'embu', 'kitui', 'machakos', 'makueni', 'nyandarua', 'nyeri', 'kirinyaga', 'muranga', 'kiambu', 'turkana', 'west pokot', 'samburu', 
        'trans-nzoia', 'Uasin gishu', 'elgeyo marakwet', 'nandi', 'baringo', 'laikipia', 'nakuru', 'narok', 'kajiado', 'kericho', 'bomet', 'kakamega', 'vihiga', 'bungoma', 
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
            filters &= Q(condition= 'Used')

        listings = listings.filter(filters)
    return render(request, 'listings/browse.html', {'listings': listings})


# View listing detail
def listing_detail(request, listing_id):
    listing = get_object_or_404(Listing, id=listing_id, is_active=True, is_approved=True)

    Listing.objects.filter(id=listing.id).update(
        views_count=F('views_count') + 1
    )

    # Prepare Whatasapp Message Safely
    message = (
        f"Hi, I saw your car on VroomHub.\n "
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

    return render(request, 'listings/detail.html', {'listing': listing, 'whatsapp_link': whatsapp_link, 'whatsapp_share': whatsapp_share, 'current_url': current_url})

# Edit listing
@login_required
def edit_listing(request, listing_id):
    listing = get_object_or_404(Listing, id=listing_id, user=request.user)
    if request.method == 'POST':
        form = ListingForm(request.POST, instance=listing)
        if form.is_valid():
            form.save()
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
    return redirect('browse_listings')

# Seller manage ads
@login_required
def manage_ads(request):
    listings = Listing.objects.filter(user=request.user)
    return render(request, 'listings/manage_ads.html', {'listings': listings})
    
def seller_listings(request, user_id):
    seller = get_object_or_404(User, id=user_id)
    listings = Listing.objects.filter(user=seller, is_approved=True, is_active=True)
    return render(request, 'listings/seller_listings.html', {
        'seller': seller,
        'listings': listings
    })

    