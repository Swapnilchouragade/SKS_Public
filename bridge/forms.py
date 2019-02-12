from django import forms
from django.forms.models import ModelForm

from bridge.models import Expert, Student, AddLecture


class NameForm(forms.Form):
    your_name = forms.CharField(label='Your name', max_length=100)


class ExpertForm(ModelForm):
    class Meta:
        model = Expert
        widgets = {
            'password': forms.PasswordInput(),
            'about': forms.Textarea(attrs={'style':'resize:none;height:100px'}),
        }
        fields = (
            'name',
            'Designation',
            'Company_Name',
            'Skill',
            'Field_of_Experience',
            'Personal_Email',
            'mobile',
            'Profile_piture',
            'about',
            'password',
            'Icard_Picture',
            'Department',

        )


class StudentForm(ModelForm):
    class Meta:
        model = Student
        widgets = {
            'password': forms.PasswordInput(),
        }
        fields = (
            'name',
            'Collage',
            'Year_Experience',
            'Qualification',
            'Personal_Email',
            'mobile',
            'Profile_piture',
            'password',
        )


class AddLectureForm(ModelForm):
    class Meta:
        model = AddLecture
        fields = (
            'title',
            'description',
            'date',
            'time',
            'expert_id'
        )

class ContactForm(forms.Form):
    contact_name = forms.CharField(required=True)
    contact_email = forms.EmailField(required=True)
    content = forms.CharField(
        required=True,
        widget=forms.Textarea
    )

    # the new bit we're adding
    def __init__(self, *args, **kwargs):
        super(ContactForm, self).__init__(*args, **kwargs)
        self.fields['contact_name'].label = "Your name:"
        self.fields['contact_email'].label = "Your email:"
        self.fields['content'].label = "What do you want to say?"
