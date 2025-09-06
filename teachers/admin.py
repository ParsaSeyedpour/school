from django.contrib import admin

# Register your models here.
from django.contrib import admin
from .models import Teacher

@admin.register(Teacher)
class TeacherAdmin(admin.ModelAdmin):
    list_display = ("id", "user", "department")
    search_fields = ("user__username", "user__email", "department")
    raw_id_fields = ("user",)
