from django.contrib import admin

# Register your models here.
from django.contrib import admin
from django.contrib.auth.admin import UserAdmin as DjangoUserAdmin
from django.utils.translation import gettext_lazy as _
from .models import User
from students.models import Student
from teachers.models import Teacher
from parents.models import Parent

class StudentInline(admin.StackedInline):
    model = Student
    extra = 0

class TeacherInline(admin.StackedInline):
    model = Teacher
    extra = 0

class ParentInline(admin.StackedInline):
    model = Parent
    extra = 0

@admin.register(User)
class UserAdmin(DjangoUserAdmin):
    list_display = ("id", "username", "email", "role", "is_staff", "is_superuser")
    list_filter  = ("role", "is_staff", "is_superuser", "is_active")
    search_fields = ("username", "email", "first_name", "last_name")
    ordering = ("id",)

    fieldsets = (
        (None, {"fields": ("username", "password")}),
        (_("Personal info"), {"fields": ("first_name", "last_name", "email")}),
        (_("Role"), {"fields": ("role",)}),
        (_("Permissions"), {"fields": ("is_active","is_staff","is_superuser","groups","user_permissions")}),
        (_("Important dates"), {"fields": ("last_login","date_joined")}),
    )
    add_fieldsets = (
        (None, {
            "classes": ("wide",),
            "fields": ("username", "password1", "password2", "role", "email", "first_name", "last_name"),
        }),
    )

    inlines = [StudentInline, TeacherInline, ParentInline]
