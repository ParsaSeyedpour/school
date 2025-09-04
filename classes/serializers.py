# classes/serializers.py
from rest_framework import serializers
from .models import Course, Class, Lesson, Enrollment, LessonAttendance
from students.serializers import StudentSerializer
from teachers.serializers import TeacherSerializer

class CourseSerializer(serializers.ModelSerializer):
    class Meta:
        model = Course
        fields = ['id', 'name', 'code', 'description', 'credits']

class LessonSerializer(serializers.ModelSerializer):
    class Meta:
        model = Lesson
        fields = ['id', 'title', 'description', 'date', 'duration_minutes', 
                 'lesson_type', 'materials', 'is_cancelled']

class ClassSerializer(serializers.ModelSerializer):
    teacher = TeacherSerializer(read_only=True)
    course = CourseSerializer(read_only=True)
    enrolled_count = serializers.ReadOnlyField()
    available_spots = serializers.ReadOnlyField()
    lessons = LessonSerializer(many=True, read_only=True)
    
    # Write fields for creation/updates
    teacher_id = serializers.IntegerField(write_only=True)
    course_id = serializers.IntegerField(write_only=True)
    
    class Meta:
        model = Class
        fields = ['id', 'name', 'semester', 'max_students', 'schedule', 'room', 
                 'is_active', 'created_at', 'teacher', 'course', 'enrolled_count', 
                 'available_spots', 'lessons', 'teacher_id', 'course_id']
        read_only_fields = ['id', 'created_at']

class ClassListSerializer(serializers.ModelSerializer):
    """Simplified serializer for list views"""
    teacher_name = serializers.CharField(source='teacher.user.get_full_name', read_only=True)
    course_name = serializers.CharField(source='course.name', read_only=True)
    course_code = serializers.CharField(source='course.code', read_only=True)
    enrolled_count = serializers.ReadOnlyField()
    available_spots = serializers.ReadOnlyField()
    
    class Meta:
        model = Class
        fields = ['id', 'name', 'semester', 'teacher_name', 'course_name', 
                 'course_code', 'enrolled_count', 'available_spots', 'is_active']

class EnrollmentSerializer(serializers.ModelSerializer):
    student = StudentSerializer(read_only=True)
    class_instance = ClassListSerializer(read_only=True)
    
    # Write fields
    student_id = serializers.IntegerField(write_only=True, required=False)
    class_id = serializers.IntegerField(write_only=True)
    
    class Meta:
        model = Enrollment
        fields = ['id', 'enrolled_at', 'is_active', 'grade', 'student', 
                 'class_instance', 'student_id', 'class_id']
        read_only_fields = ['id', 'enrolled_at']
    
    def validate(self, data):
        class_instance = Class.objects.get(id=data['class_id'])
        
        # Check if class is full
        if class_instance.available_spots <= 0:
            raise serializers.ValidationError("This class is full.")
        
        # Check if already enrolled
        student_id = data.get('student_id') or self.context['request'].user.student_profile.id
        if Enrollment.objects.filter(
            student_id=student_id, 
            class_instance=class_instance, 
            is_active=True
        ).exists():
            raise serializers.ValidationError("Student is already enrolled in this class.")
        
        return data

class LessonAttendanceSerializer(serializers.ModelSerializer):
    student_name = serializers.CharField(source='student.user.get_full_name', read_only=True)
    lesson_title = serializers.CharField(source='lesson.title', read_only=True)
    
    class Meta:
        model = LessonAttendance
        fields = ['id', 'status', 'notes', 'recorded_at', 'student_name', 
                 'lesson_title', 'lesson', 'student']
        read_only_fields = ['id', 'recorded_at']