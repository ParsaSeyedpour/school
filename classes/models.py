# classes/models.py
from django.db import models
from django.conf import settings
from django.core.exceptions import ValidationError

class Course(models.Model):
    """Represents a course/subject like 'Mathematics', 'Physics', etc."""
    name = models.CharField(max_length=100)
    code = models.CharField(max_length=20, unique=True)  # e.g., 'MATH101'
    description = models.TextField(blank=True)
    credits = models.PositiveIntegerField(default=3)
    
    def __str__(self):
        return f"{self.code} - {self.name}"

class Class(models.Model):
    """Represents a specific class instance of a course taught by a teacher"""
    course = models.ForeignKey(Course, on_delete=models.CASCADE, related_name='classes')
    teacher = models.ForeignKey('teachers.Teacher', on_delete=models.CASCADE, related_name='classes')
    name = models.CharField(max_length=100)  # e.g., 'Math 101 - Section A'
    semester = models.CharField(max_length=50)  # e.g., 'Fall 2024'
    max_students = models.PositiveIntegerField(default=30)
    schedule = models.TextField(help_text="Class schedule details")
    room = models.CharField(max_length=50, blank=True)
    is_active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        verbose_name_plural = "Classes"
    
    def __str__(self):
        return f"{self.name} - {self.teacher.user.get_full_name()}"
    
    @property
    def enrolled_count(self):
        return self.enrollments.filter(is_active=True).count()
    
    @property
    def available_spots(self):
        return self.max_students - self.enrolled_count

class Lesson(models.Model):
    """Individual lesson within a class"""
    class_instance = models.ForeignKey(Class, on_delete=models.CASCADE, related_name='lessons')
    title = models.CharField(max_length=200)
    description = models.TextField(blank=True)
    date = models.DateTimeField()
    duration_minutes = models.PositiveIntegerField(default=60)
    lesson_type = models.CharField(
        max_length=20,
        choices=[
            ('lecture', 'Lecture'),
            ('lab', 'Laboratory'),
            ('seminar', 'Seminar'),
            ('exam', 'Exam'),
            ('review', 'Review Session'),
        ],
        default='lecture'
    )
    materials = models.TextField(blank=True, help_text="Links to materials, readings, etc.")
    is_cancelled = models.BooleanField(default=False)
    
    class Meta:
        ordering = ['date']
    
    def __str__(self):
        return f"{self.title} - {self.class_instance.name}"

class Enrollment(models.Model):
    """Student enrollment in a class"""
    student = models.ForeignKey('students.Student', on_delete=models.CASCADE, related_name='enrollments')
    class_instance = models.ForeignKey(Class, on_delete=models.CASCADE, related_name='enrollments')
    enrolled_at = models.DateTimeField(auto_now_add=True)
    is_active = models.BooleanField(default=True)
    grade = models.CharField(max_length=5, blank=True)  # Final grade
    
    class Meta:
        unique_together = ['student', 'class_instance']
    
    def __str__(self):
        return f"{self.student.user.get_full_name()} enrolled in {self.class_instance.name}"
    
    def clean(self):
        # Check if class is full
        if self.class_instance.available_spots <= 0 and not self.pk:
            raise ValidationError("This class is full.")
    
    def save(self, *args, **kwargs):
        self.clean()
        super().save(*args, **kwargs)

class LessonAttendance(models.Model):
    """Track student attendance for individual lessons"""
    lesson = models.ForeignKey(Lesson, on_delete=models.CASCADE, related_name='attendance')
    student = models.ForeignKey('students.Student', on_delete=models.CASCADE, related_name='lesson_attendance')
    status = models.CharField(
        max_length=10,
        choices=[
            ('present', 'Present'),
            ('absent', 'Absent'),
            ('late', 'Late'),
            ('excused', 'Excused'),
        ],
        default='absent'
    )
    notes = models.TextField(blank=True)
    recorded_at = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        unique_together = ['lesson', 'student']
    
    def __str__(self):
        return f"{self.student.user.get_full_name()} - {self.lesson.title} ({self.status})"