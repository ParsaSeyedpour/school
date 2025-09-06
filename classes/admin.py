from django.contrib import admin

# Register your models here.
from django.contrib import admin
from .models import Course, Class, Lesson, Enrollment, LessonAttendance

@admin.register(Course)
class CourseAdmin(admin.ModelAdmin):
    list_display = ("id", "code", "name", "credits")
    search_fields = ("code", "name")
    list_filter = ("credits",)

@admin.register(Class)
class ClassAdmin(admin.ModelAdmin):
    list_display = ("id","name","course","teacher","semester","max_students","enrolled_count","available_spots","is_active")
    list_filter  = ("semester","is_active")
    search_fields = ("name","course__name","course__code","teacher__user__username")
    raw_id_fields = ("course","teacher")
    readonly_fields = ("created_at",)

@admin.register(Lesson)
class LessonAdmin(admin.ModelAdmin):
    list_display = ("id","title","class_instance","lesson_type","date","duration_minutes","is_cancelled")
    list_filter  = ("lesson_type","is_cancelled")
    search_fields = ("title","class_instance__name")
    date_hierarchy = "date"
    raw_id_fields = ("class_instance",)

@admin.register(Enrollment)
class EnrollmentAdmin(admin.ModelAdmin):
    list_display = ("id","student","class_instance","is_active","grade","enrolled_at")
    list_filter  = ("is_active",)
    search_fields = ("student__user__username","class_instance__name","grade")
    raw_id_fields = ("student","class_instance")
    date_hierarchy = "enrolled_at"

@admin.register(LessonAttendance)
class LessonAttendanceAdmin(admin.ModelAdmin):
    list_display = ("id","lesson","student","status","recorded_at")
    list_filter  = ("status",)
    search_fields = ("lesson__title","student__user__username")
    raw_id_fields = ("lesson","student")
    date_hierarchy = "recorded_at"
