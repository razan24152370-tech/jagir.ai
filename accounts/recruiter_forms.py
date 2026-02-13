from django import forms
from django.contrib.auth.forms import AuthenticationForm
from .models import Profile

class RecruiterLoginForm(AuthenticationForm):
    def confirm_login_allowed(self, user):
        super().confirm_login_allowed(user)
        try:
            if user.profile.user_type != 'recruiter':
                raise forms.ValidationError('This login is only for recruiters.', code='invalid_login')
        except Profile.DoesNotExist:
            raise forms.ValidationError('Profile not found for this user.', code='invalid_login')
