from django import forms
from .models import Listing

class ListingForm(forms.ModelForm):
    class Meta:
        model = Listing
        fields = ['category', 'title', 'price', 'location', 'condition', 'brand', 'model', 'year', 'mileage', 'fuel_type', 'transmission',
                  'trim', 'color', 'interior_color', 'features', 'chasis_number', 'registered_car', 'exchange_possible', 'body', 'drive_train', 'seats_number',
                  'engine_size', 'horse_power', 'negotiation', 'description', 'phone_number', 'whatsapp_number']
        widgets = {
            'features': forms.CheckboxSelectMultiple(),
        }
        help_texts = {
            'chasis_number': "Optional – Chrandi Motors will not display this to users."
        }
