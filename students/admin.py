from django.contrib import admin

# Register your models here.
from django.contrib import admin
from .models import Student

@admin.register(Student)
class StudentAdmin(admin.ModelAdmin):
    list_display = ("id", "user", "grade", "major")
    search_fields = ("user__username", "user__email", "grade", "major")
    raw_id_fields = ("user",)
