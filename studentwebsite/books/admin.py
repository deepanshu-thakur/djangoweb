from django.contrib import admin
from books.models import Book,Fav,Comment
from books.forms import SignUpForm
from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth.models import User
# Register your models here.
admin.site.register(Comment)

# Define the PicAdmin class
class PicAdmin(admin.ModelAdmin):
    exclude = ('image', 'content_type')






# Register the admin class with the associated model
admin.site.register(Book, PicAdmin)

admin.site.register(Fav)