# Create your models here.
from django.db import models
from django.conf import settings

class Student(models.Model):
    user = models.OneToOneField(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name="student_profile")
    grade = models.CharField(max_length=50, blank=True)
    major = models.CharField(max_length=100, blank=True)

    def __str__(self):
        return f"Student<{self.user.username}>"
