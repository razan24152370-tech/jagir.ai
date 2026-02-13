from django import forms
from .models import Job, JobApplication


class JobForm(forms.ModelForm):
    class Meta:
        model = Job
        fields = [
            'title', 'company', 'description', 'requirements', 'skills_required',
            'location', 'salary_min', 'salary_max', 'job_type',
            'experience_required', 'deadline', 'is_active'
        ]
        widgets = {
            'title': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Job Title'}),
            'company': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Company Name'}),
            'description': forms.Textarea(attrs={'class': 'form-control', 'rows': 4, 'placeholder': 'Describe the role...'}),
            'requirements': forms.Textarea(attrs={'class': 'form-control', 'rows': 3, 'placeholder': 'List the requirements...'}),
            'skills_required': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Python, Django, SQL, etc.'}),
            'location': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'City, Country or Remote'}),
            'salary_min': forms.NumberInput(attrs={'class': 'form-control', 'placeholder': 'Min salary'}),
            'salary_max': forms.NumberInput(attrs={'class': 'form-control', 'placeholder': 'Max salary'}),
            'job_type': forms.Select(attrs={'class': 'form-control'}),
            'experience_required': forms.NumberInput(attrs={'class': 'form-control', 'min': 0}),
            'deadline': forms.DateInput(attrs={'class': 'form-control', 'type': 'date'}),
            'is_active': forms.CheckboxInput(attrs={'class': 'form-check-input'}),
        }


class JobApplicationForm(forms.ModelForm):
    class Meta:
        model = JobApplication
        fields = ['resume', 'cover_letter']
        widgets = {
            'resume': forms.FileInput(attrs={'class': 'form-control'}),
            'cover_letter': forms.Textarea(attrs={
                'class': 'form-control',
                'rows': 4,
                'placeholder': 'Why are you a good fit for this role? Share your motivation and relevant experience...'
            }),
        }
