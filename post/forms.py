from django import forms
from ckeditor.widgets import CKEditorWidget
from dal import autocomplete
from .models import *

class PostForm(forms.ModelForm):
    title = forms.CharField(widget=forms.TextInput(attrs={'class': 'form-control'}))
    content = forms.CharField(widget=CKEditorWidget())
    class Meta:
        model = Question
        fields = ['title','content','tags']
        widgets = {
            'tags': autocomplete.TaggitSelect2(
                'tag-autocomplete',attrs={'class': 'form-control'}
            )
        }

class AnswerForm(forms.ModelForm):
    content = forms.CharField(widget=CKEditorWidget(attrs={'width':'70%'}))
    class Meta:
        model = Answer
        fields = ['content']

class ReplyForm(forms.ModelForm):
    content = forms.CharField(widget=CKEditorWidget(attrs={'width':'70%'}))
    class Meta:
        model = Reply
        fields = ['content']
