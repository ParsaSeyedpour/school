# classes/views.py
from rest_framework import viewsets, permissions, status
from rest_framework.decorators import action
from rest_framework.response import Response
from django.db.models import Q
from .models import Course, Class, Lesson, Enrollment, LessonAttendance
from .serializers import (
    CourseSerializer, ClassSerializer, ClassListSerializer,
    LessonSerializer, EnrollmentSerializer, LessonAttendanceSerializer
)

class IsTeacherOwnerOrAdmin(permissions.BasePermission):
    """Allow access to class owner (teacher) or admin"""
    def has_object_permission(self, request, view, obj):
        if request.user.is_staff:
            return True
        if hasattr(request.user, 'teacher_profile'):
            return obj.teacher == request.user.teacher_profile
        return False

class IsEnrolledStudentOrTeacherOrAdmin(permissions.BasePermission):
    """Allow access to enrolled students, class teacher, or admin"""
    def has_object_permission(self, request, view, obj):
        if request.user.is_staff:
            return True
        if hasattr(request.user, 'teacher_profile'):
            return obj.teacher == request.user.teacher_profile
        if hasattr(request.user, 'student_profile'):
            return obj.enrollments.filter(
                student=request.user.student_profile, 
                is_active=True
            ).exists()
        return False

class CourseViewSet(viewsets.ModelViewSet):
    queryset = Course.objects.all()
    serializer_class = CourseSerializer
    
    def get_permissions(self):
        if self.action in ['create', 'update', 'partial_update', 'destroy']:
            return [permissions.IsAdminUser()]
        return [permissions.IsAuthenticated()]

class ClassViewSet(viewsets.ModelViewSet):
    queryset = Class.objects.select_related('teacher__user', 'course').filter(is_active=True)
    
    def get_serializer_class(self):
        if self.action == 'list':
            return ClassListSerializer
        return ClassSerializer
    
    def get_permissions(self):
        if self.action in ['create', 'update', 'partial_update', 'destroy']:
            return [permissions.IsAuthenticated(), IsTeacherOwnerOrAdmin()]
        elif self.action in ['retrieve', 'lessons', 'enrollments']:
            return [permissions.IsAuthenticated(), IsEnrolledStudentOrTeacherOrAdmin()]
        return [permissions.IsAuthenticated()]
    
    def get_queryset(self):
        user = self.request.user
        queryset = self.queryset
        
        # Filter based on user type
        if hasattr(user, 'teacher_profile') and not user.is_staff:
            # Teachers see only their classes
            queryset = queryset.filter(teacher=user.teacher_profile)
        elif hasattr(user, 'student_profile') and not user.is_staff:
            # Students see all active classes or their enrolled classes
            if self.action == 'list':
                # Show all available classes for enrollment
                pass
            else:
                # For detail views, show only enrolled classes
                queryset = queryset.filter(
                    enrollments__student=user.student_profile,
                    enrollments__is_active=True
                )
        
        return queryset
    
    def perform_create(self, serializer):
        # Auto-assign teacher if not admin
        teacher_profile = getattr(self.request.user, 'teacher_profile', None)
        if teacher_profile and not self.request.user.is_staff:
            serializer.save(teacher=teacher_profile)
        else:
            serializer.save()
    
    @action(detail=True, methods=['get'])
    def lessons(self, request, pk=None):
        """Get all lessons for a class"""
        class_instance = self.get_object()
        lessons = class_instance.lessons.all().order_by('date')
        serializer = LessonSerializer(lessons, many=True)
        return Response(serializer.data)
    
    @action(detail=True, methods=['get'])
    def enrollments(self, request, pk=None):
        """Get all enrollments for a class (teacher/admin only)"""
        class_instance = self.get_object()
        if not (request.user.is_staff or 
                (hasattr(request.user, 'teacher_profile') and 
                 class_instance.teacher == request.user.teacher_profile)):
            return Response({'error': 'Permission denied'}, status=status.HTTP_403_FORBIDDEN)
        
        enrollments = class_instance.enrollments.filter(is_active=True)
        serializer = EnrollmentSerializer(enrollments, many=True)
        return Response(serializer.data)
    
    @action(detail=True, methods=['post'])
    def enroll(self, request, pk=None):
        """Enroll current user (student) in this class"""
        if not hasattr(request.user, 'student_profile'):
            return Response({'error': 'Only students can enroll in classes'}, 
                          status=status.HTTP_403_FORBIDDEN)
        
        class_instance = self.get_object()
        data = {'class_id': class_instance.id}
        serializer = EnrollmentSerializer(data=data, context={'request': request})
        
        if serializer.is_valid():
            serializer.save(student=request.user.student_profile, class_instance=class_instance)
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
    
    @action(detail=True, methods=['post'])
    def unenroll(self, request, pk=None):
        """Unenroll current user from this class"""
        if not hasattr(request.user, 'student_profile'):
            return Response({'error': 'Only students can unenroll from classes'}, 
                          status=status.HTTP_403_FORBIDDEN)
        
        class_instance = self.get_object()
        try:
            enrollment = Enrollment.objects.get(
                student=request.user.student_profile,
                class_instance=class_instance,
                is_active=True
            )
            enrollment.is_active = False
            enrollment.save()
            return Response({'message': 'Successfully unenrolled'})
        except Enrollment.DoesNotExist:
            return Response({'error': 'You are not enrolled in this class'}, 
                          status=status.HTTP_400_BAD_REQUEST)

class LessonViewSet(viewsets.ModelViewSet):
    serializer_class = LessonSerializer
    
    def get_queryset(self):
        user = self.request.user
        if hasattr(user, 'teacher_profile') and not user.is_staff:
            # Teachers see lessons from their classes
            return Lesson.objects.filter(class_instance__teacher=user.teacher_profile)
        elif hasattr(user, 'student_profile') and not user.is_staff:
            # Students see lessons from their enrolled classes
            return Lesson.objects.filter(
                class_instance__enrollments__student=user.student_profile,
                class_instance__enrollments__is_active=True
            )
        return Lesson.objects.all()
    
    def get_permissions(self):
        if self.action in ['create', 'update', 'partial_update', 'destroy']:
            return [permissions.IsAuthenticated(), IsTeacherOwnerOrAdmin()]
        return [permissions.IsAuthenticated()]
    
    @action(detail=True, methods=['get', 'post'])
    def attendance(self, request, pk=None):
        """Get or record attendance for a lesson"""
        lesson = self.get_object()
        
        if request.method == 'GET':
            # Get attendance records
            attendance = lesson.attendance.all()
            serializer = LessonAttendanceSerializer(attendance, many=True)
            return Response(serializer.data)
        
        elif request.method == 'POST':
            # Record attendance (teacher only)
            if not (request.user.is_staff or 
                    (hasattr(request.user, 'teacher_profile') and 
                     lesson.class_instance.teacher == request.user.teacher_profile)):
                return Response({'error': 'Permission denied'}, status=status.HTTP_403_FORBIDDEN)
            
            # Bulk create/update attendance
            attendance_data = request.data.get('attendance', [])
            for item in attendance_data:
                item['lesson'] = lesson.id
                serializer = LessonAttendanceSerializer(data=item)
                if serializer.is_valid():
                    LessonAttendance.objects.update_or_create(
                        lesson=lesson,
                        student_id=item['student'],
                        defaults={
                            'status': item['status'],
                            'notes': item.get('notes', '')
                        }
                    )
            
            return Response({'message': 'Attendance recorded successfully'})

class EnrollmentViewSet(viewsets.ModelViewSet):
    serializer_class = EnrollmentSerializer
    
    def get_queryset(self):
        user = self.request.user
        if hasattr(user, 'student_profile') and not user.is_staff:
            # Students see only their enrollments
            return Enrollment.objects.filter(student=user.student_profile, is_active=True)
        elif hasattr(user, 'teacher_profile') and not user.is_staff:
            # Teachers see enrollments in their classes
            return Enrollment.objects.filter(
                class_instance__teacher=user.teacher_profile,
                is_active=True
            )
        return Enrollment.objects.filter(is_active=True)
    
    def get_permissions(self):
        if self.action in ['create']:
            return [permissions.IsAuthenticated()]  # Students can enroll themselves
        elif self.action in ['destroy', 'update', 'partial_update']:
            return [permissions.IsAdminUser()]  # Only admins can modify enrollments directly
        return [permissions.IsAuthenticated()]
    
    def perform_create(self, serializer):
        # Students can only enroll themselves
        if hasattr(self.request.user, 'student_profile') and not self.request.user.is_staff:
            serializer.save(student=self.request.user.student_profile)
        else:
            serializer.save()