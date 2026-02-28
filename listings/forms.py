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
            'chasis_number': "Optional – VroomHub will not display this to users."
        }

class ListingImageForm(forms.Form):
    # first 5 required
    image1 = forms.ImageField(required=True)
    image2 = forms.ImageField(required=True)
    image3 = forms.ImageField(required=True)
    image4 = forms.ImageField(required=True)
    image5 = forms.ImageField(required=True)

    # next 10 optional
    image6 = forms.ImageField(required=False)
    image7 = forms.ImageField(required=False)
    image8 = forms.ImageField(required=False)
    image9 = forms.ImageField(required=False)
    image10 = forms.ImageField(required=False)
    image11 = forms.ImageField(required=False)
    image12 = forms.ImageField(required=False)
    image13 = forms.ImageField(required=False)
    image14 = forms.ImageField(required=False)
    image15 = forms.ImageField(required=False)