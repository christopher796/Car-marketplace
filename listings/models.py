from django.db import models
from django.conf import settings
from django.utils import timezone

# Create your models here.
class Category(models.Model):
    name = models.CharField(max_length=50)

    def __str__(self):
        return self.name

class Feature(models.Model):
    name = models.CharField(max_length=100)

    def __str__(self):
        return self.name

class Listing(models.Model):
    CONDITION_CHOICES = [
        ('new', 'New'),
        ('used', 'Used')
    ]
    TRANSMISSION_CHOICES = [
        ('manual', 'Manual'),
        ('auto', 'Auto')
    ]
    FUEL_CHOICES = [
        ('petrol', 'Petrol'),
        ('diesel', 'Diesel'),
        ('electric', 'Electric'),
        ('hybrid', 'Hybrid')
    ]
    REGISTER_CHOICES = [
        ('yes', 'Yes'),
        ('no', 'No')
    ]
    EXCHANGE_CHOICES = [
        ('yes', 'Yes'),
        ('no', 'No')
    ]
    BODY_CHOICES = [
        ('saloon', 'Saloon'),
        ('hatchback', 'Hatchback'),
        ('station wagon', 'Station wagon'),
        ('suv', 'SUV'),
        ('crossover', 'Crossover'),
        ('coupe', 'Coupe'),
        ('coupe', 'Coupe'),
        ('convertible', 'Convertible'),
        ('pickup', 'Pickup'),
        ('van', 'Van'),
        ('microcar', 'Microcar'),
        ('liftback', 'Liftback'),
        ('limousine', 'Limousine')
    ]
    DRIVE_CHOICES = [
        ('FWD', 'FWD'),
        ('RWD', 'RWD'),
        ('AWD', 'AWD'),
        ('4WD', '4WD'),
        ('Part-Time 4WD', 'Part-Time 4WD'),
        ('Full-Time 4WD', 'Full-Time 4WD'),
        ('Hybrid AWD', 'Hybrid AWD'),
        ('Electric FWD', 'Electric FWD'),
        ('Electric RWD', 'Electric RWD'),
        ('Electric AWD', 'Electric AWD')
    ]
    NEGOTIATION_CHOICES = [
        ('yes', 'Yes'),
        ('no', 'No')
    ]



    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    category = models.ForeignKey(Category, on_delete=models.CASCADE)
    title = models.CharField(max_length=100)
    description = models.TextField()
    price = models.IntegerField()
    location = models.CharField(max_length=100)
    condition = models.CharField(max_length=10, choices=CONDITION_CHOICES)
    brand = models.CharField(max_length=50)
    model = models.CharField(max_length=50)
    year = models.IntegerField()
    mileage = models.IntegerField()
    fuel_type = models.CharField(max_length=10, choices=FUEL_CHOICES)
    transmission = models.CharField(max_length=10, choices=TRANSMISSION_CHOICES)
    trim = models.CharField(max_length=50)
    color = models.CharField(max_length=50)
    interior_color = models.CharField(max_length=50)
    features = models.ManyToManyField(Feature, blank=True)
    chasis_number = models.CharField(max_length=100, blank=True, null=True, help_text="VroomHub will not display this to users")
    registered_car = models.CharField(max_length=10, choices=REGISTER_CHOICES)
    exchange_possible = models.CharField(max_length=10, choices=EXCHANGE_CHOICES)
    body = models.CharField(max_length=50, choices=BODY_CHOICES)
    drive_train = models.CharField(max_length=50, choices=DRIVE_CHOICES)
    seats_number = models.IntegerField()
    engine_size = models.CharField(max_length=50)
    horse_power = models.CharField(max_length=50)
    negotiation = models.CharField(max_length=50, choices=NEGOTIATION_CHOICES)
    phone_number = models.CharField(max_length=20)
    whatsapp_number = models.CharField(max_length=20)
    is_approved = models.BooleanField(default=False)
    is_active = models.BooleanField(default=True)
    views_count = models.IntegerField(default=0)
    created_at = models.DateTimeField(default=timezone.now)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"{self.brand} {self.model} ({self.year})"

    def get_absolute_url(self):
        from django.urls import reverse
        return reverse('listing_detail', args=[self.id])

class ListingImage(models.Model):
    listing = models.ForeignKey(Listing, on_delete=models.CASCADE, related_name='images')
    image = models.ImageField(upload_to='listing_images/')

    def __str__(self):
        return f"Image for {self.listing.title} image"