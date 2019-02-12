from datetime import datetime

from django.contrib.auth.models import User, Group
from django.core.validators import MinValueValidator, MaxValueValidator
from django.db import models

# Create your models here.

class UserComapny(models.Model):
    user_id = models.ForeignKey(User,on_delete=models.CASCADE)
    company_id =  models.TextField(max_length=50)

class User_Group(models.Model):
    user_id=models.ForeignKey(User, on_delete=models.CASCADE)
    Group_id=models.ForeignKey(Group, on_delete=models.CASCADE)


class Expert(models.Model):
    COLOR_CHOICES = (
        ('management', 'MANAGEMENT'),
        ('engineering', 'ENGINEERING'),
        ('pharamacy', 'PHARAMACY'),
        ('other', 'OTHER')
    )
    name=models.CharField(max_length=50)
    Designation=models.CharField(max_length=70)
    Company_Name= models.CharField(max_length=200)
    Field_of_Experience=models.IntegerField(default=7, validators=[MinValueValidator(7), MaxValueValidator(100)])
    Skill=models.CharField(max_length=200,null=True)
    Department = models.CharField(max_length=100,choices=COLOR_CHOICES, default='other')
    Personal_Email=models.EmailField(max_length=100)
    mobile=models.IntegerField()
    Profile_piture=models.FileField(upload_to='profile_images/',blank=True, null=True)
    about=models.TextField(max_length=3000)
    password=models.CharField(max_length=20)
    Icard_Picture=models.FileField(upload_to='profile_images/',blank=True, null=True)

    def __str__(self):
        return self.name

    def company_name(self):
        return self.Company_Name


class Student(models.Model):
    name = models.CharField(max_length=50)
    Collage=models.CharField(max_length=100)
    Year_Experience=models.IntegerField()
    Qualification=models.CharField(max_length=200)
    Personal_Email=models.EmailField(max_length=100)
    mobile=models.IntegerField()
    Profile_piture=models.FileField(upload_to='profile_images/',blank=True, null=True)
    password=models.CharField(max_length=20)


class Expert_Student_Block(models.Model):
    Expert_id=models.ForeignKey(Expert, on_delete=models.CASCADE)
    Student_id=models.ForeignKey(Student, on_delete=models.CASCADE)
    is_block=models.TextField()


class Student_block_count(models.Model):
    Student_id = models.ForeignKey(Student, on_delete=models.CASCADE)
    block_count=models.IntegerField()


class Expert_Following(models.Model):
    Student_id=models.ForeignKey(Student, on_delete=models.CASCADE)
    Expert_id=models.ForeignKey(Expert, on_delete=models.CASCADE)
    Is_follow=models.TextField(max_length=20)
    Is_follow_accepted=models.TextField(max_length=20)


class AddLecture(models.Model):
    title = models.CharField(max_length=200)
    description = models.TextField()
    date = models.DateField()
    time = models.TimeField()
    expert_id = models.ForeignKey(Expert, on_delete=models.CASCADE,null=True)
    update_timestamp = models.DateTimeField(default=datetime.now())


class StudentLectureAttended(models.Model):
    student_id = models.ForeignKey(Student, on_delete=models.CASCADE)
    expert_id = models.ForeignKey(Expert, on_delete=models.CASCADE)
    lecture_id = models.ForeignKey(AddLecture, on_delete=models.CASCADE)


class LectureHistory(models.Model):
    lecture_id = models.ForeignKey(AddLecture, on_delete=models.CASCADE)
    student_count = models.IntegerField()
    student_list = models.TextField()
    expert_id = models.ForeignKey(Expert, on_delete=models.CASCADE)



class CommonNews(models.Model):
    news = models.TextField(null=True)
    student_id = models.IntegerField(null=True)

class CommonExpertNews(models.Model):
    news = models.TextField(null=True)
    expert_id = models.IntegerField(null=True)
    is_available  = models.BooleanField(default=False)

class ExpertOnlineStatus(models.Model):
    expert = models.ForeignKey(Expert, on_delete=models.CASCADE)
    is_online = models.BooleanField(default=False)

class NewsFeed(models.Model):
    news = models.TextField()
    expert_id = models.IntegerField(null=True)
    is_available = models.BooleanField(default=False)


class ExpertReview(models.Model):
    as_boss = models.IntegerField()
    student = models.ForeignKey(Student, on_delete=models.CASCADE)
    expert = models.ForeignKey(Expert, on_delete=models.CASCADE)


class StudentReview(models.Model):
    communication_skill = models.IntegerField()
    domain_knowledge = models.IntegerField()
    team_skill = models.IntegerField()
    open_for_learning = models.IntegerField()
    behaviour = models.IntegerField()
    overall = models.IntegerField()
    student = models.ForeignKey(Student, on_delete=models.CASCADE)


class E2E(models.Model):
    expert_sent = models.ForeignKey(Expert, on_delete=models.CASCADE)
    expert_get = models.IntegerField()
    is_connect_request = models.BooleanField(default=False)
    is_connect = models.BooleanField(default=False)


class ExpertEnq(models.Model):
    expert = models.ForeignKey(Expert, on_delete=models.CASCADE)
    student = models.ForeignKey(Student, on_delete=models.CASCADE)


class AdminNews(models.Model):
    news = models.TextField()
    expert = models.ForeignKey(Expert, on_delete=models.CASCADE, null=True)
    student = models.ForeignKey(Student, on_delete=models.CASCADE, null=True)
