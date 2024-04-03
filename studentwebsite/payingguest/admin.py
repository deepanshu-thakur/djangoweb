from django.contrib import admin
from payingguest.models import Payingguest,PGFav,PGComment

# Register your models here.
admin.site.register(PGComment)

# Define the PicAdmin class
class PicAdmin(admin.ModelAdmin):
    exclude = ('image', 'content_type')


# Register the admin class with the associated model
admin.site.register(Payingguest, PicAdmin)

admin.site.register(PGFav)