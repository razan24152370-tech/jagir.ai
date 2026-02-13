from django import forms
from django.contrib.auth.forms import UserCreationForm, AuthenticationForm
from django.contrib.auth.models import User
from .models import Profile, TeamMember


class JobSeekerSignupForm(UserCreationForm):
    """Signup form specifically for Job Seekers"""
    email = forms.EmailField(
        required=True, 
        label='Email Address',
        widget=forms.EmailInput(attrs={'class': 'form-control', 'placeholder': 'Enter your email'})
    )
    
    class Meta:
        model = User
        fields = ('username', 'email', 'password1', 'password2')
    
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['username'].widget.attrs.update({'class': 'form-control', 'placeholder': 'Choose a username'})
        self.fields['password1'].widget.attrs.update({'class': 'form-control', 'placeholder': 'Create a password'})
        self.fields['password2'].widget.attrs.update({'class': 'form-control', 'placeholder': 'Confirm password'})


class RecruiterSignupForm(UserCreationForm):
    """Signup form specifically for Recruiters"""
    email = forms.EmailField(
        required=True, 
        label='Email Address',
        widget=forms.EmailInput(attrs={'class': 'form-control', 'placeholder': 'Enter your work email'})
    )
    company_name = forms.CharField(
        max_length=200,
        required=True,
        label='Company Name',
        widget=forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Your company name'})
    )
    
    class Meta:
        model = User
        fields = ('username', 'email', 'company_name', 'password1', 'password2')
    
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['username'].widget.attrs.update({'class': 'form-control', 'placeholder': 'Choose a username'})
        self.fields['password1'].widget.attrs.update({'class': 'form-control', 'placeholder': 'Create a password'})
        self.fields['password2'].widget.attrs.update({'class': 'form-control', 'placeholder': 'Confirm password'})


class JobSeekerLoginForm(AuthenticationForm):
    """Login form for Job Seekers"""
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['username'].widget.attrs.update({'class': 'form-control', 'placeholder': 'Username'})
        self.fields['password'].widget.attrs.update({'class': 'form-control', 'placeholder': 'Password'})


class RecruiterLoginForm(AuthenticationForm):
    """Login form for Recruiters"""
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['username'].widget.attrs.update({'class': 'form-control', 'placeholder': 'Username'})
        self.fields['password'].widget.attrs.update({'class': 'form-control', 'placeholder': 'Password'})


class ProfileForm(forms.ModelForm):
    """Form for Job Seeker profile"""
    class Meta:
        model = Profile
        fields = [
            'headline', 'bio', 'skills', 'experience_years',
            'education', 'resume', 'phone', 'location', 'linkedin_url'
        ]
        widgets = {
            'headline': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'e.g., Senior Python Developer'}),
            'bio': forms.Textarea(attrs={'class': 'form-control', 'rows': 3, 'placeholder': 'Tell us about yourself...'}),
            'skills': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Python, Django, JavaScript, SQL'}),
            'experience_years': forms.NumberInput(attrs={'class': 'form-control', 'min': 0}),
            'education': forms.Textarea(attrs={'class': 'form-control', 'rows': 2, 'placeholder': 'Your educational background...'}),
            'resume': forms.FileInput(attrs={'class': 'form-control'}),
            'phone': forms.TextInput(attrs={'class': 'form-control', 'placeholder': '+1234567890'}),
            'location': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'City, Country'}),
            'linkedin_url': forms.URLInput(attrs={'class': 'form-control', 'placeholder': 'https://linkedin.com/in/yourprofile'}),
        }


class RecruiterProfileForm(forms.ModelForm):
    """Form for Recruiter profile"""
    class Meta:
        model = Profile
        fields = ['company_name', 'company_website', 'company_description', 'phone', 'location']
        widgets = {
            'company_name': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Company Name'}),
            'company_website': forms.URLInput(attrs={'class': 'form-control', 'placeholder': 'https://company.com'}),
            'company_description': forms.Textarea(attrs={'class': 'form-control', 'rows': 3, 'placeholder': 'About your company...'}),
            'phone': forms.TextInput(attrs={'class': 'form-control', 'placeholder': '+1234567890'}),
            'location': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'City, Country'}),
        }


class TeamMemberForm(forms.ModelForm):
    """Form for adding/editing team members"""
    class Meta:
        model = TeamMember
        fields = ['first_name', 'last_name', 'email', 'role', 'permissions', 'is_active']
        widgets = {
            'first_name': forms.TextInput(attrs={
                'class': 'form-control', 
                'placeholder': 'First Name'
            }),
            'last_name': forms.TextInput(attrs={
                'class': 'form-control', 
                'placeholder': 'Last Name'
            }),
            'email': forms.EmailInput(attrs={
                'class': 'form-control', 
                'placeholder': 'work@email.com'
            }),
            'role': forms.Select(attrs={'class': 'form-control'}),
            'permissions': forms.Select(attrs={'class': 'form-control'}),
            'is_active': forms.CheckboxInput(attrs={'class': 'form-check-input'}),
        }
        help_texts = {
            'email': 'This email will be used to invite the team member.',
            'role': 'The role/title of this team member in your organization.',
            'permissions': 'What this team member can do in the recruitment system.',
        }
