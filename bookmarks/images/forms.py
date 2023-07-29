from django import forms
from .models import Image
from django.utils.text import slugify
from django.core.files.base import ContentFile
from urllib import request


class ImageCreateFrom(forms.ModelForm):

    class Meta:
        model = Image
        fields = ('title', 'url', 'description')
        widgets = {'url': forms.HiddenInput}

    def clean_url(self):
        url = self.cleaned_data['url']
        vaild_extensions = ['jpg', 'jpeg']
        extension = url.rsplit('.', 1)[1].lower()
        if extension not in vaild_extensions:
            raise forms.ValidationError('This given URL does not match valid image extension.')
        return url

    def save(self, force_insert=False, force_update=False, commit=True):
        image = super().save(commit=False)
        image_url = self.cleaned_data['url']
        name = slugify(image.title)
        image_extension = image_url.rsplit('.', 1)[1].lower()
        image_name = f'{name}.{image_extension}'
        respones = request.urlopen(image_url)
        image.image.save(image_name, ContentFile(respones.read()), save=False)
        if commit:
            image.save()
        return image
