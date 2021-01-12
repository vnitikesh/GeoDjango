from django import forms
from .models import *

class MeasurementModelForm(forms.ModelForm):
    class Meta:
        model = Measurement
        fields = ('destination',)
        widgets = {
        'destination': forms.TextInput(attrs = {'placeholder': 'Enter the destination city'})
        }
        labels = {
        'destination': 'City name'
        }
