from django.contrib import admin

# Register your models here.
from django.contrib.auth.models import User

from bridge.models import Student
from bridge.models import Expert, AddLecture, Student, Expert_Following, Expert_Student_Block, Student_block_count, StudentLectureAttended,\
    CommonNews, CommonExpertNews, ExpertOnlineStatus, NewsFeed

class StudentAdmin(admin.ModelAdmin):
    list_display = ('name',
            'Collage',
            'Year_Experience',
            'Qualification',
            'Personal_Email',
            'mobile',
            'Profile_piture',
            'password')
    list_filter = ['Personal_Email',]


class ExpertAdmin(admin.ModelAdmin):
    list_display = ( 'name',
            'Designation',
            'Company_Name',
            'Skill',
            'Field_of_Experience',
            'Personal_Email',
            'mobile',
            'Profile_piture',
            'about',
            'password',
            'Icard_Picture',)
    list_filter = ['Personal_Email',]


class Expert_FollowingAdmin(admin.ModelAdmin):
    list_display = ('Student_id','Expert_id','Is_follow','Is_follow_accepted',)
    list_filter = ['Student_id','Expert_id','Is_follow','Is_follow_accepted',]


class AddLectureAdmin(admin.ModelAdmin):
    list_display = ('title','description','date','time','expert_id')
    list_filter = ('title','description','date','time','expert_id',)


class Expert_Student_BlockAdmin(admin.ModelAdmin):
    list_display = ('Expert_id', 'Student_id', 'is_block')
    list_filter = ['Expert_id', 'Student_id', 'is_block',]


class Student_block_countkAdmin(admin.ModelAdmin):
    list_display = ('Student_id', 'block_count')
    list_filter = ['Student_id', 'block_count',]


class StudentLectureAttendedAdmin(admin.ModelAdmin):
    list_display = ('student_id', 'expert_id', 'lecture_id')
    list_filter = ['student_id', 'expert_id', 'lecture_id',]


class CommonNewsAdmin(admin.ModelAdmin):
    list_display = ('news', 'student_id')
    list_filter = ['news', 'student_id',]


class CommonExpertNewsAdmin(admin.ModelAdmin):
    list_display = ('news', 'expert_id', 'is_available')
    list_filter = ['news', 'expert_id', 'is_available',]


class ExpertOnlineStatusAdmin(admin.ModelAdmin):
    list_display = ('expert', 'is_online')
    list_filter = ['expert', 'is_online']


class NewsFeedAdmin(admin.ModelAdmin):
    list_display = ('news', 'expert_id', 'is_available')
    list_filter = ['news', 'expert_id', 'is_available',]


admin.site.register(Student,StudentAdmin)
admin.site.register(Expert,ExpertAdmin)
admin.site.register(Expert_Following, Expert_FollowingAdmin)
admin.site.register(AddLecture,AddLectureAdmin)
admin.site.register(Expert_Student_Block,Expert_Student_BlockAdmin)
admin.site.register(Student_block_count,Student_block_countkAdmin)
admin.site.register(StudentLectureAttended,StudentLectureAttendedAdmin)
admin.site.register(CommonNews, CommonNewsAdmin)
admin.site.register(CommonExpertNews, CommonExpertNewsAdmin)
admin.site.register(ExpertOnlineStatus, ExpertOnlineStatusAdmin)
admin.site.register(NewsFeed, NewsFeedAdmin)

