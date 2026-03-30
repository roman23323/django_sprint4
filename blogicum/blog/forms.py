from django import forms
from .models import User, Comment, Post


class EditProfileForm(forms.ModelForm):
    class Meta:
        model = User
        fields = ('first_name', 'last_name', 'username', 'email')


class CommentForm(forms.ModelForm):
    class Meta:
        model = Comment
        fields = ('text',)


class CreatePostForm(forms.ModelForm):
    class Meta:
        model = Post
        fields = ('title', 'text', 'location', 'category', 'pub_date', 'image')
        widgets = {
            'pub_date': forms.DateInput(attrs={'type': 'date'})
        }