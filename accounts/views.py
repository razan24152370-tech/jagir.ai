from django.shortcuts import render, redirect
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.forms import AuthenticationForm
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.http import HttpResponse
from django.urls import reverse
from django.utils import timezone

from .forms import (
    JobSeekerSignupForm, RecruiterSignupForm, 
    JobSeekerLoginForm, RecruiterLoginForm,
    ProfileForm, RecruiterProfileForm, TeamMemberForm
)
from .models import Profile, TeamMember
from .email_utils import (
    send_team_member_invitation, 
    send_access_update_notification,
    send_account_deactivation_notification,
    send_welcome_email
)


def home(request):
    return render(request, 'accounts/home.html')


# ============ JOB SEEKER AUTH ============

def jobseeker_signup_view(request):
    """Signup view for Job Seekers"""
    if request.method == 'POST':
        form = JobSeekerSignupForm(request.POST)
        if form.is_valid():
            user = form.save()
            # Create profile with jobseeker type
            Profile.objects.create(user=user, user_type='jobseeker')
            login(request, user)
            messages.success(request, 'Welcome! Your job seeker account has been created.')
            return redirect('jobs:user_dashboard')
        else:
            messages.error(request, 'Signup failed. Please correct the errors below.')
    else:
        form = JobSeekerSignupForm()
    return render(request, 'accounts/jobseeker_signup.html', {'form': form})


def jobseeker_login_view(request):
    """Login view for Job Seekers"""
    if request.method == 'POST':
        form = JobSeekerLoginForm(request, data=request.POST)
        if form.is_valid():
            user = form.get_user()
            try:
                if user.profile.user_type != 'jobseeker':
                    messages.error(request, 'This account is registered as a recruiter. Please use the recruiter login.')
                    return render(request, 'accounts/jobseeker_login.html', {'form': form})
            except Profile.DoesNotExist:
                pass
            login(request, user)
            messages.success(request, f'Welcome back, {user.username}!')
            return redirect('jobs:user_dashboard')
        else:
            messages.error(request, 'Login failed. Please check your credentials.')
    else:
        form = JobSeekerLoginForm()
    return render(request, 'accounts/jobseeker_login.html', {'form': form})


# ============ RECRUITER AUTH ============

def recruiter_signup_view(request):
    """Signup view for Recruiters"""
    if request.method == 'POST':
        form = RecruiterSignupForm(request.POST)
        if form.is_valid():
            user = form.save()
            company_name = form.cleaned_data.get('company_name', '')
            # Create profile with recruiter type
            Profile.objects.create(
                user=user, 
                user_type='recruiter',
                company_name=company_name
            )
            login(request, user)
            messages.success(request, 'Welcome! Your recruiter account has been created.')
            return redirect('jobs:recruiter_dashboard')
        else:
            messages.error(request, 'Signup failed. Please correct the errors below.')
    else:
        form = RecruiterSignupForm()
    return render(request, 'accounts/recruiter_signup.html', {'form': form})


def recruiter_login_view(request):
    """Login view for Recruiters"""
    if request.method == 'POST':
        form = RecruiterLoginForm(request, data=request.POST)
        if form.is_valid():
            user = form.get_user()
            try:
                if user.profile.user_type != 'recruiter':
                    messages.error(request, 'This account is registered as a job seeker. Please use the job seeker login.')
                    return render(request, 'accounts/recruiter_login.html', {'form': form})
            except Profile.DoesNotExist:
                pass
            login(request, user)
            messages.success(request, f'Welcome back, {user.username}!')
            return redirect('jobs:recruiter_dashboard')
        else:
            messages.error(request, 'Login failed. Please check your credentials.')
    else:
        form = RecruiterLoginForm()
    return render(request, 'accounts/recruiter_login.html', {'form': form})


def logout_view(request):
    logout(request)
    messages.info(request, 'You have been logged out successfully.')
    return redirect('project_home')


def get_user_profile_safe(request):
    """Safely get user profile, return None if not exists"""
    try:
        return request.user.profile
    except:
        return None


@login_required
def profile_view(request):
    """View user profile"""
    profile = get_user_profile_safe(request)
    if profile is None:
        messages.warning(request, 'Your account setup is incomplete. Please complete your registration.')
        logout(request)
        return redirect('project_home')
    
    # Get additional stats for recruiter profile
    context = {'profile': profile}
    if profile.user_type == 'recruiter':
        from jobs.models import Job, JobApplication
        
        # Get job statistics
        total_jobs = Job.objects.filter(posted_by=request.user).count()
        active_jobs = Job.objects.filter(posted_by=request.user, is_active=True).count()
        total_applications = JobApplication.objects.filter(job__posted_by=request.user).count()
        
        # Get team member count
        team_count = TeamMember.objects.filter(company_owner=request.user, is_active=True).count()
        
        # Recent applications with candidates
        recent_applications = JobApplication.objects.filter(
            job__posted_by=request.user
        ).select_related('applicant', 'job').order_by('-applied_at')[:5]
        
        # Profile completion percentage
        fields = [
            profile.company_name,
            profile.company_description,
            profile.company_website,
            profile.phone,
            profile.location
        ]
        completed_fields = sum(1 for f in fields if f)
        profile_completion = int((completed_fields / len(fields)) * 100)
        
        context.update({
            'total_jobs': total_jobs,
            'active_jobs': active_jobs,
            'total_applications': total_applications,
            'team_count': team_count,
            'recent_applications': recent_applications,
            'profile_completion': profile_completion,
        })
    else:
        # Job seeker profile completion
        fields = [
            profile.headline,
            profile.resume,
            profile.skills,
            profile.experience_years,
            profile.education,
            profile.phone,
            profile.location
        ]
        completed_fields = sum(1 for f in fields if f)
        profile_completion = int((completed_fields / len(fields)) * 100)
        
        context.update({
            'profile_completion': profile_completion,
        })
    
    return render(request, 'accounts/profile.html', context)


@login_required
def edit_profile(request):
    """Edit user profile"""
    profile = get_user_profile_safe(request)
    if profile is None:
        messages.warning(request, 'Your account setup is incomplete. Please complete your registration.')
        logout(request)
        return redirect('accounts:home')
    
    if profile.user_type == 'recruiter':
        FormClass = RecruiterProfileForm
    else:
        FormClass = ProfileForm
    
    if request.method == 'POST':
        form = FormClass(request.POST, request.FILES, instance=profile)
        if form.is_valid():
            form.save()
            messages.success(request, 'Profile updated successfully!')
            return redirect('accounts:profile')
    else:
        form = FormClass(instance=profile)
    
    return render(request, 'accounts/edit_profile.html', {'form': form, 'profile': profile})


# ============ TEAM MEMBER MANAGEMENT ============

@login_required
def team_members_view(request):
    """View and manage team members (Recruiter only)"""
    profile = get_user_profile_safe(request)
    if profile is None or profile.user_type != 'recruiter':
        messages.error(request, 'Only recruiters can manage team members.')
        return redirect('accounts:home')
    
    team_members = TeamMember.objects.filter(company_owner=request.user)
    context = {
        'team_members': team_members,
        'profile': profile,
    }
    return render(request, 'accounts/team_members.html', context)


@login_required
def add_team_member(request):
    """Add a new team member (Recruiter only)"""
    profile = get_user_profile_safe(request)
    if profile is None or profile.user_type != 'recruiter':
        messages.error(request, 'Only recruiters can add team members.')
        return redirect('accounts:home')
    
    if request.method == 'POST':
        form = TeamMemberForm(request.POST)
        if form.is_valid():
            # Get the name from form data before saving
            member_name = f"{form.cleaned_data['first_name']} {form.cleaned_data['last_name']}"
            
            # Create the team member instance
            team_member = form.save(commit=False)
            team_member.company_owner = request.user
            
            try:
                # Save the team member
                team_member.save()
                
                # Generate invitation URL
                invitation_url = request.build_absolute_uri(
                    reverse('accept_team_invitation', kwargs={'token': str(team_member.invitation_token)})
                )
                
                # Send invitation email
                email_sent = send_team_member_invitation(team_member, invitation_url, profile)
                
                if email_sent:
                    messages.success(request, f'Team member {member_name} added successfully! Invitation email sent.')
                else:
                    messages.warning(request, f'Team member {member_name} added, but invitation email failed to send. You can resend it later.')
                
                return redirect('team_members')
            except Exception as e:
                messages.error(request, f'Error adding team member: {str(e)}')
        else:
            messages.error(request, 'Please correct the errors below.')
    else:
        form = TeamMemberForm()
    
    return render(request, 'accounts/add_team_member.html', {'form': form, 'profile': profile})


@login_required
def edit_team_member(request, member_id):
    """Edit a team member (Recruiter only)"""
    profile = get_user_profile_safe(request)
    if profile is None or profile.user_type != 'recruiter':
        messages.error(request, 'Only recruiters can edit team members.')
        return redirect('accounts:home')
    
    from django.shortcuts import get_object_or_404
    team_member = get_object_or_404(TeamMember, id=member_id, company_owner=request.user)
    
    if request.method == 'POST':
        form = TeamMemberForm(request.POST, instance=team_member)
        if form.is_valid():
            # Track changes
            changes = {}
            if form.has_changed():
                for field in form.changed_data:
                    if field in ['role', 'permissions', 'is_active']:
                        old_value = getattr(team_member, field)
                        new_value = form.cleaned_data[field]
                        if field == 'role':
                            changes['Role'] = f"{dict(TeamMember.ROLE_CHOICES).get(old_value)} → {dict(TeamMember.ROLE_CHOICES).get(new_value)}"
                        elif field == 'permissions':
                            changes['Permissions'] = f"{dict(TeamMember.PERMISSION_CHOICES).get(old_value)} → {dict(TeamMember.PERMISSION_CHOICES).get(new_value)}"
                        elif field == 'is_active':
                            changes['Status'] = f"{'Active' if old_value else 'Inactive'} → {'Active' if new_value else 'Inactive'}"
            
            updated_member = form.save()
            member_name = updated_member.get_full_name()
            
            # Send notification email if significant changes were made
            if changes:
                send_access_update_notification(updated_member, request.user, changes)
            
            messages.success(request, f'Team member {member_name} updated successfully!')
            return redirect('team_members')
    else:
        form = TeamMemberForm(instance=team_member)
    
    return render(request, 'accounts/edit_team_member.html', {
        'form': form, 
        'team_member': team_member,
        'profile': profile
    })


@login_required
def delete_team_member(request, member_id):
    """Delete a team member (Recruiter only)"""
    profile = get_user_profile_safe(request)
    if profile is None or profile.user_type != 'recruiter':
        messages.error(request, 'Only recruiters can delete team members.')
        return redirect('accounts:home')
    
    from django.shortcuts import get_object_or_404
    team_member = get_object_or_404(TeamMember, id=member_id, company_owner=request.user)
    
    if request.method == 'POST':
        name = team_member.get_full_name()
        team_member.delete()
        messages.success(request, f'Team member {name} removed successfully!')
        return redirect('team_members')
    
    return render(request, 'accounts/delete_team_member.html', {
        'team_member': team_member,
        'profile': profile
    })


@login_required
def toggle_team_member_status(request, member_id):
    """Activate/Deactivate a team member (Recruiter only)"""
    profile = get_user_profile_safe(request)
    if profile is None or profile.user_type != 'recruiter':
        messages.error(request, 'Only recruiters can manage team members.')
        return redirect('accounts:home')
    
    from django.shortcuts import get_object_or_404
    team_member = get_object_or_404(TeamMember, id=member_id, company_owner=request.user)
    
    # Toggle status
    was_active = team_member.is_active
    team_member.is_active = not team_member.is_active
    team_member.save()
    
    status = 'activated' if team_member.is_active else 'deactivated'
    
    # Send notification email
    if not team_member.is_active and was_active:
        send_account_deactivation_notification(team_member, request.user)
    elif team_member.is_active and not was_active:
        changes = {'Status': 'Inactive → Active'}
        send_access_update_notification(team_member, request.user, changes)
    
    messages.success(request, f'Team member {team_member.get_full_name()} {status}!')
    return redirect('team_members')


@login_required
def resend_team_invitation(request, member_id):
    """Resend invitation email to a team member (Recruiter only)"""
    profile = get_user_profile_safe(request)
    if profile is None or profile.user_type != 'recruiter':
        messages.error(request, 'Only recruiters can resend invitations.')
        return redirect('accounts:home')
    
    from django.shortcuts import get_object_or_404
    team_member = get_object_or_404(TeamMember, id=member_id, company_owner=request.user)
    
    if team_member.invitation_accepted:
        messages.info(request, f'{team_member.get_full_name()} has already accepted the invitation.')
        return redirect('team_members')
    
    # Regenerate invitation token
    team_member.regenerate_invitation_token()
    
    # Generate new invitation URL
    invitation_url = request.build_absolute_uri(
        reverse('accept_team_invitation', kwargs={'token': str(team_member.invitation_token)})
    )
    
    # Send invitation email
    email_sent = send_team_member_invitation(team_member, invitation_url, profile)
    
    if email_sent:
        messages.success(request, f'Invitation resent to {team_member.get_full_name()}!')
    else:
        messages.error(request, 'Failed to send invitation email.')
    
    return redirect('team_members')


def accept_team_invitation(request, token):
    """Accept a team member invitation and create account"""
    from django.shortcuts import get_object_or_404
    import uuid
    
    try:
        # Find team member by token
        team_member = get_object_or_404(TeamMember, invitation_token=uuid.UUID(token))
        
        # Check if invitation is already accepted
        if team_member.invitation_accepted:
            messages.info(request, 'This invitation has already been accepted.')
            return redirect('accounts:home')
        
        # Check if invitation is still valid
        if not team_member.is_invitation_valid():
            messages.error(request, 'This invitation has expired. Please request a new one from your administrator.')
            return redirect('accounts:home')
        
        # Check if user is already logged in
        if request.user.is_authenticated:
            # If logged in user email matches, link accounts
            if request.user.email == team_member.email:
                team_member.user = request.user
                team_member.invitation_accepted = True
                team_member.invitation_accepted_at = timezone.now()
                team_member.save()
                
                # Send welcome email
                send_welcome_email(team_member, team_member.company_owner.profile)
                
                messages.success(request, f'Welcome to {team_member.company_owner.profile.company_name}!')
                return redirect('recruiter_dashboard')
            else:
                messages.error(request, 'The logged-in account email does not match the invitation email.')
                return redirect('accounts:home')
        
        # Show signup form for new users
        if request.method == 'POST':
            from django.contrib.auth.forms import UserCreationForm
            
            form = UserCreationForm(request.POST)
            if form.is_valid():
                # Create user account
                user = form.save(commit=False)
                user.email = team_member.email
                user.first_name = team_member.first_name
                user.last_name = team_member.last_name
                user.save()
                
                # Create recruiter profile (team members are part of recruitment team)
                Profile.objects.create(
                    user=user,
                    user_type='recruiter',
                    company_name=team_member.company_owner.profile.company_name
                )
                
                # Link team member to user account
                team_member.user = user
                team_member.invitation_accepted = True
                team_member.invitation_accepted_at = timezone.now()
                team_member.save()
                
                # Log in the user
                login(request, user)
                
                # Send welcome email
                send_welcome_email(team_member, team_member.company_owner.profile)
                
                messages.success(request, f'Welcome to {team_member.company_owner.profile.company_name}!')
                return redirect('recruiter_dashboard')
        else:
            from django.contrib.auth.forms import UserCreationForm
            form = UserCreationForm()
        
        context = {
            'form': form,
            'team_member': team_member,
            'company_name': team_member.company_owner.profile.company_name,
        }
        return render(request, 'accounts/accept_invitation.html', context)
        
    except (ValueError, TeamMember.DoesNotExist):
        messages.error(request, 'Invalid invitation link.')
        return redirect('accounts:home')
