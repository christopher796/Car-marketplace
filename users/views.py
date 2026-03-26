from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth import login, logout, authenticate, get_user_model
from .forms import UserRegisterForm, ProfileForm, ReviewForm, VerificationForm
from django.contrib.auth.decorators import login_required
from .models import Profile, Review, Report
from listings.models import Listing
from django.contrib.auth.models import User
from django.contrib import messages
from .models import Profile


# Create your views here.
def register_view(request):
    if request.method == 'POST':
        form = UserRegisterForm(request.POST)

        if form.is_valid():
            user = form.save(commit=False)
            user.set_password(form.cleaned_data['password'])
            user.email = form.cleaned_data['email']
            user.save()

            login(request, user)
            return redirect('browse_listings')

        else:
            return render(request, 'users/register.html', {
                'form': form,
                'error': 'Please correct te errors below'
            })
    else:
        form = UserRegisterForm()
    return render(request, 'users/register.html', {'form': form})



def login_view(request):
    if request.method == 'POST':
        username = request.POST.get('username')
        password = request.POST.get('password')
        remember = request.POST.get('remember')  # Get remember me checkbox value
        
        user = authenticate(request, username=username, password=password)
        
        if user is not None:
            login(request, user)
            
            # Handle Remember Me functionality
            if remember:
                # If remember me is checked, session expires after 2 weeks (1209600 seconds)
                request.session.set_expiry(1209600)  # 2 weeks
            else:
                # If remember me is NOT checked, session expires when browser closes
                request.session.set_expiry(0)
            
            return redirect('browse_listings')
        else:
            return render(request, 'users/login.html', {'error': 'Invalid credentials'})
    
    return render(request, 'users/login.html')

@login_required
def logout_view(request):
    logout(request)
    return redirect('/')

User = get_user_model()    

def seller_profile(request, user_id):
    profile = get_object_or_404(Profile, user_id=user_id)
    ads = Listing.objects.filter(user_id=user_id, is_approved=True, is_active=True)

    # All reviews for this seller
    reviews = profile.user.reviews.all()

    # Calculate average rating
    if reviews.exists():
        avg_rating = sum(r.rating for r in reviews) / reviews.count()
    else:
        avg_rating = 0

    # Calculate total views across all seller's listings
    from django.db.models import Sum
    total_views = ads.aggregate(total=Sum('views_count'))['total'] or 0

    return render(request, 'users/seller_profile.html', {
        'profile': profile, 
        'ads': ads, 
        'reviews': reviews, 
        'avg_rating': avg_rating,
        'total_views': total_views,  # Add total views to context
    })

User = get_user_model()
@login_required
def add_review(request, user_id):
    seller = get_object_or_404(User, id=user_id)

    if request.method == 'POST':
        form = ReviewForm(request.POST)
        if form.is_valid():
            review = form.save(commit=False)
            review.seller = seller
            review.reviewer = request.user
            review.save()

    return redirect('seller_profile', user_id=user_id)

@login_required
def get_verified(request):
    profile = request.user.profile
    if profile.is_verified:
        return redirect('browse_listings') 

    if request.method == 'POST':
        form = VerificationForm(request.POST, request.FILES, instance=profile)
        if form.is_valid():
            # Save profile with verification details
            profile = form.save(commit=False)
            profile.is_verified = False
            profile.save()
            return redirect('browse_listings')
    else:
        form = VerificationForm(instance=profile)
    return render(request, 'users/get_verified.html', {'form': form})

@login_required
def edit_profile(request):
    if request.method == 'POST':
        # Get the profile for the current user
        profile = request.user.profile
        
        # Get form data
        phone = request.POST.get('phone')
        whatsapp = request.POST.get('whatsapp')
        location = request.POST.get('location')
        bio = request.POST.get('bio')
        
        # Update profile fields
        if phone:
            profile.phone = phone
        if whatsapp:
            profile.whatsapp = whatsapp
        if location:
            profile.location = location
        if bio:
            profile.bio = bio
        
        # Handle profile picture upload
        if request.FILES.get('profile_pic'):
            profile.profile_pic = request.FILES['profile_pic']
        
        profile.save()
        
        messages.success(request, 'Profile updated successfully!')
        return redirect('seller_profile', user_id=request.user.id)
    
    # GET request - show the edit form
    return render(request, 'users/edit_profile.html', {'user': request.user})