from django import forms
from .models import CommentModel

class EmailPostForm(forms.Form):
    name = forms.CharField(label='Name', max_length=100)
    email = forms.EmailField(label='Email')
    to = forms.EmailField(label='To')
    comments = forms.CharField(widget=forms.Textarea,required=False)

class CommentForm(forms.ModelForm):
    class Meta:
        model = CommentModel
        fields = ('name', 'email', 'body')


class SearchForm(forms.Form):
    query = forms.CharField()

