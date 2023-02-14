from django import forms
from .models import User
from dal import autocomplete

class TagForm(forms.ModelForm):
    class Meta:
        model = User
        fields = ['tags']
        widgets = {
            'tags': autocomplete.TaggitSelect2(
                'tag-auto',attrs={'class': 'form-control'}
            )
        }