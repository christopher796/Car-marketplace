from django.shortcuts import render, redirect
from django.contrib.auth.decorators import login_required
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
from django.utils import timezone
from datetime import timedelta
import json

from listings.models import Listing
from .models import FeaturedPackage, ListingFeature
from .utils import stk_push


@login_required
def feature_listing(request, listing_id):
    listing = Listing.objects.get(id=listing_id, user=request.user)
    packages = FeaturedPackage.objects.filter(active=True)

    if request.method == "POST":
        package_id = request.POST.get("package")
        phone = request.POST.get("phone")

        package = FeaturedPackage.objects.get(id=package_id)
        stk_push(phone, package.price, listing.id)

        return render(request, "payments/waiting.html")  # show "Processing payment" page

    return render(request, "payments/feature_listing.html", {
        "listing": listing,
        "packages": packages
    })


@csrf_exempt
def mpesa_callback(request):
    data = json.loads(request.body)
    metadata = data["Body"]["stkCallback"]["CallbackMetadata"]["Item"]

    receipt = metadata[1]["Value"]
    reference = metadata[4]["Value"]

    listing = Listing.objects.get(id=reference)
    package = FeaturedPackage.objects.first()

    ListingFeature.objects.update_or_create(
        listing=listing,
        defaults={
            "package": package,
            "active": True,
            "end_date": timezone.now() + timedelta(days=package.days),
            "mpesa_receipt": receipt
        }
    )

    return JsonResponse({"ResultCode": 0})