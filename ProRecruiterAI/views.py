from django.shortcuts import render

def project_home(request):
    return render(request, 'project_home.html')

from django.http import JsonResponse
from django.contrib.auth.decorators import user_passes_test
from django.contrib.admin.views.decorators import staff_member_required
from django.contrib.auth.models import User
from accounts.models import Profile
from jobs.models import Job

def is_superuser(user):
    return user.is_superuser

@staff_member_required
def admin_dashboard_stats(request):
    total_users = User.objects.count()
    recruiters_count = Profile.objects.filter(user_type='recruiter').count()
    seekers_count = Profile.objects.filter(user_type='jobseeker').count()
    total_jobs = Job.objects.count()
    
    return JsonResponse({
        'total_users': total_users,
        'recruiters_count': recruiters_count,
        'seekers_count': seekers_count,
        'total_jobs': total_jobs,
    })

def about_us(request):
    return render(request, 'about.html')

def contact_us(request):
    return render(request, 'contact.html')