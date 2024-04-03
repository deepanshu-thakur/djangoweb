from django import forms
from payingguest.models import Payingguest
from django.core.files.uploadedfile import InMemoryUploadedFile
from payingguest.humanize import naturalsize

#=====================================
from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth.models import User
# Create the form class.
class PGCreateForm(forms.ModelForm):
    max_upload_limit = 2 * 1024 * 1024
    max_upload_limit_text = naturalsize(max_upload_limit)

    # Call this 'picture' so it gets copied from the form to the in-memory model
    # It will not be the "bytes", it will be the "InMemoryUploadedFile"
    # because we need to pull out things like content_type
    image = forms.FileField(required=False, label='File to Upload <= '+max_upload_limit_text)
    upload_field_name = 'image'

    # Hint: this will need to be changed for use in the ads application :)
    class Meta:
        model = Payingguest
        fields = ['City', 'rent','user_address','pg_address', 'condition','image']  # Picture is manual

    # Validate the size of the picture
    def clean(self):
        cleaned_data = super().clean()
        pic = cleaned_data.get('image')
        if pic is None:
            return
        if len(pic) > self.max_upload_limit:
            self.add_error('image', "File must be < "+self.max_upload_limit_text+" bytes")

    # Convert uploaded File object to a picture
    def save(self, commit=True):
        instance = super(PGCreateForm, self).save(commit=False)

        # We only need to adjust picture if it is a freshly uploaded file
        f = instance.image   # Make a copy
        if isinstance(f, InMemoryUploadedFile):  # Extract data from the form to the model
            bytearr = f.read()
            instance.content_type = f.content_type
            instance.image = bytearr  # Overwrite with the actual image data

        if commit:
            instance.save()

        return instance

class PGCommentForm(forms.Form):
    comment = forms.CharField(required=True, max_length=500, min_length=3, strip=True)
# https://docs.djangoproject.com/en/3.0/toads/http/file-uploads/
# https://stackoverflow.com/questions/2472422/django-file-upload-size-limit
# https://stackoverflow.com/questions/32007311/how-to-change-data-in-django-modelform
# https://docs.djangoproject.com/en/3.0/ref/forms/validation/#cleaning-and-validating-fields-that-depend-on-each-other
class PGSignUpForm(UserCreationForm):
    first_name = forms.CharField(max_length=30, required=False)
    last_name = forms.CharField(max_length=30, required=False)
    email = forms.EmailField(max_length=254)

    class Meta:
        model = User
        fields = ('username', 'first_name', 'last_name', 'email', 'password1', 'password2',)

