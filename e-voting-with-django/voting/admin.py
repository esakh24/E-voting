from django.contrib import admin

# Register your models here.
from .models import Dicty, KeyVal

# Register your models here.
admin.site.register(Dicty)
admin.site.register(KeyVal)