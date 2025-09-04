from django.shortcuts import render

# Create your views here.
from rest_framework import viewsets, permissions
from .models import Student
from .serializers import StudentSerializer

class IsOwnerOrAdmin(permissions.BasePermission):
    def has_object_permission(self, request, view, obj):
        if request.user.is_staff:
            return True
        return getattr(obj, "user_id", None) == request.user.id

class StudentViewSet(viewsets.ModelViewSet):
    queryset = Student.objects.select_related("user").all()
    serializer_class = StudentSerializer

    def get_permissions(self):
        if self.action in ["list", "destroy"]:
            return [permissions.IsAdminUser()]
        return [permissions.IsAuthenticated(), IsOwnerOrAdmin()]

    def perform_create(self, serializer):
        # Allow admin to create for any user; others only for themselves
        user = self.request.user if not self.request.user.is_staff else serializer.validated_data.get("user", self.request.user)
        serializer.save(user=user)
