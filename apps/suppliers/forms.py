from django import forms
from django.forms import modelformset_factory
from .models import Supplier

class SupplierForm(forms.ModelForm):
    class Meta:
        model = Supplier
        fields = ['name', 'article_number', 'priority', 'visual_priority']
