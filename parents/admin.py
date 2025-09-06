from django.contrib import admin

# Register your models here.
from django.contrib import admin
from .models import Parent

@admin.register(Parent)
class ParentAdmin(admin.ModelAdmin):
    list_display = ("id", "user", "phone", "address")
    search_fields = ("user__username", "user__email", "phone", "address")
    raw_id_fields = ("user",)
