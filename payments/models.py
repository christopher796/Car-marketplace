from django.db import models
from listings.models import Listing
from django.utils import timezone

class FeaturedPackage(models.Model):
    name = models.CharField(max_length=50)
    price = models.IntegerField() # in KES
    days = models.IntegerField()
    active = models.BooleanField(default=True)


    def __str__(self):
        return f"{self.name} - KES{self.price}"

class ListingFeature(models.Model):
    listing = models.OneToOneField(Listing, on_delete=models.CASCADE, related_name="feature")
    package = models.ForeignKey(FeaturedPackage, on_delete=models.CASCADE)
    start_date = models.DateTimeField(auto_now_add=True)
    end_date = models.DateTimeField()
    active = models.BooleanField(default=False)
    mpesa_receipt =  models.CharField(max_length=100, blank=True, null=True)

    def is_active(self):
        return self.activate and self.end_date > timezone.now()

        