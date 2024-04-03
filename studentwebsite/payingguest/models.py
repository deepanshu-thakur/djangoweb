from django.db import models

# Create your models here.
from django.core.validators import MinLengthValidator
from django.contrib.auth.models import User
from django.conf import settings

class Payingguest(models.Model) :
    City = models.CharField(
            max_length=200,
            validators=[MinLengthValidator(2, "Type of PG must be greater than 2 characters")]
    )
    user_address =models.CharField(
            max_length=200,
            validators=[MinLengthValidator(2, "Type of PG must be greater than 2 characters")], null=True
    )
    pg_address = models.CharField(
            max_length=200,
            validators=[MinLengthValidator(2, "Type of PG must be greater than 2 characters")], null=True
    )
    rent = models.DecimalField(max_digits=7, decimal_places=2, null=True)    
    condition = models.TextField()
    owner = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    comments = models.ManyToManyField(settings.AUTH_USER_MODEL,
        through='PGComment', related_name='pgcomments_owned')
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    #picture
    image = models.BinaryField(null=True, editable=True)
    content_type = models.CharField(max_length=256, null=True, help_text='The MIMEType of the file')
    # Favorites
    favorites = models.ManyToManyField(settings.AUTH_USER_MODEL,
        through='PGFav', related_name='favorite_payingguest')

    # Shows up in the admin list
    def __str__(self):
        return self.City

class PGComment(models.Model) :
    text = models.TextField(
        validators=[MinLengthValidator(3, "Comment must be greater than 3 characters")]
    )

    payingguest = models.ForeignKey(Payingguest, on_delete=models.CASCADE)
    owner = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    # Shows up in the admin list
    def __str__(self):
        if len(self.text) < 15 : return self.text
        return self.text[:11] + ' ...'

class PGFav(models.Model) :
    payingguest = models.ForeignKey(Payingguest, on_delete=models.CASCADE)
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)

    # https://docs.djangoproject.com/en/3.0/ref/models/options/#unique-together
    class Meta:
        unique_together = ('payingguest', 'user')

    def __str__(self) :
        return '%s likes %s'%(self.user.username, self.payingguest.City[:10])