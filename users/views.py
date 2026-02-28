from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth import login, logout, authenticate, get_user_model
from .forms import UserRegisterForm, ProfileForm, ReviewForm, VerificationForm
from django.contrib.auth.decorators import login_required
from .models import Profile, Review, Report
from listings.models import Listing
from django.contrib.auth.models import User
from django.contrib import messages


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
        user = authenticate(request, username=username, password=password)
        if user is not None:
            login(request, user)
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
    profile= get_object_or_404(Profile, user_id=user_id)
    ads= Listing.objects.filter(user_id=user_id, is_approved=True)

    # All reviews for this seller
    reviews = profile.user.reviews.all()

    # Calculate average rating
    if reviews.exists():
        avg_rating = sum(r.rating for r in reviews) / reviews.count()
    else:
        avg_rating = 0
    return render(request, 'users/seller_profile.html', {'profile': profile, 'ads': ads, 'reviews': reviews, 'avg_rating': avg_rating})

User = get_user_model()
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