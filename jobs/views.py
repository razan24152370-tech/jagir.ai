from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.db.models import Count
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
from django.views.decorators.http import require_http_methods
import json
import logging
from .models import Job, JobApplication, JobView, JobPreference
from .forms import JobForm, JobApplicationForm
from .ai_service import get_job_recommendations, rank_applications

logger = logging.getLogger('jobs')


def get_user_profile(request):
    """
    Helper function to safely get user profile.
    Returns profile if exists, None otherwise.
    """
    try:
        return request.user.profile
    except:
        return None


def ensure_profile_exists(request, redirect_url='accounts:home'):
    """
    Check if user has a profile. If not, redirect to home with a message.
    Returns (profile, redirect_response) tuple.
    If profile exists: (profile, None)
    If no profile: (None, redirect_response)
    """
    profile = get_user_profile(request)
    if profile is None:
        messages.warning(request, 'Your account setup is incomplete. Please complete your registration.')
        from django.contrib.auth import logout
        logout(request)
        return None, redirect('accounts:home')
    return profile, None


# ============== JOB SEEKER / USER PANEL ==============

@login_required
def user_dashboard(request):
    """User/Job Seeker Dashboard"""
    profile, redirect_response = ensure_profile_exists(request)
    if redirect_response:
        return redirect_response
    
    if profile.user_type != 'jobseeker':
        return redirect('recruiter_dashboard')
    
    # Get user's applications
    my_applications = JobApplication.objects.filter(applicant=request.user).select_related('job')
    
    # Get active jobs for recommendations (exclude already applied)
    active_jobs = Job.objects.filter(is_active=True).exclude(
        applications__applicant=request.user
    )
    
    # Get AI recommendations
    recommendations = get_job_recommendations(profile, active_jobs)[:5]
    
    # Calculate profile completion
    profile_fields = [profile.headline, profile.bio, profile.skills, profile.experience_years, 
                      profile.education, profile.phone, profile.location]
    filled = sum(1 for f in profile_fields if f)
    profile_completion = int((filled / len(profile_fields)) * 100)
    
    context = {
        'profile': profile,
        'recent_applications': my_applications[:5],
        'recommended_jobs': recommendations,
        'total_applications': my_applications.count(),
        'profile_completion': profile_completion,
    }
    return render(request, 'jobs/user_dashboard.html', context)


@login_required
def browse_jobs(request):
    """Browse all available jobs"""
    profile = get_user_profile(request)
    
    jobs = Job.objects.filter(is_active=True)
    
    # Simple search
    query = request.GET.get('q', '')
    if query:
        jobs = jobs.filter(title__icontains=query) | jobs.filter(description__icontains=query)
    
    # Filter by job type
    job_type = request.GET.get('type', '')
    if job_type:
        jobs = jobs.filter(job_type=job_type)
    
    # Get recommendations if user is a job seeker with profile
    recommended_jobs = []
    other_jobs = []
    
    if profile and profile.user_type == 'jobseeker':
        recommendations = get_job_recommendations(profile, jobs, use_personalization=True)
        recommended_jobs = [rec for rec in recommendations if rec['score'] >= 50]
        other_jobs = [rec for rec in recommendations if rec['score'] < 50]
    else:
        other_jobs = [{'job': job, 'score': 0, 'reason': '', 'personalized': False} for job in jobs]
    
    context = {
        'recommended_jobs': recommended_jobs,
        'other_jobs': other_jobs,
        'query': query,
        'job_type': job_type,
        'job_types': Job.JOB_TYPE_CHOICES,
        'has_profile': profile and profile.user_type == 'jobseeker',
    }
    return render(request, 'jobs/browse_jobs.html', context)


@login_required
def job_detail(request, job_id):
    """View job details"""
    job = get_object_or_404(Job, id=job_id)
    has_applied = JobApplication.objects.filter(job=job, applicant=request.user).exists()
    
    # Track job view (create or update)
    if hasattr(request.user, 'profile') and request.user.profile.user_type == 'jobseeker':
        JobView.objects.create(
            user=request.user,
            job=job,
            source=request.GET.get('source', 'direct')
        )
    
    match_score = None
    match_reason = None
    match_improvements = []
    if hasattr(request.user, 'profile') and request.user.profile.user_type == 'jobseeker':
        recommendations = get_job_recommendations(request.user.profile, [job], use_personalization=True)
        if recommendations:
            match_score = recommendations[0]['score']
            match_reason = recommendations[0]['reason']
            match_improvements = recommendations[0].get('improvements', [])
    
    context = {
        'job': job,
        'has_applied': has_applied,
        'match_score': match_score,
        'match_reason': match_reason,
        'match_improvements': match_improvements,
    }
    return render(request, 'jobs/job_detail.html', context)


@login_required
def apply_job(request, job_id):
    """Apply for a job"""
    job = get_object_or_404(Job, id=job_id, is_active=True)
    
    if JobApplication.objects.filter(job=job, applicant=request.user).exists():
        messages.warning(request, 'You have already applied for this job.')
        return redirect('job_detail', job_id=job_id)
    
    if request.method == 'POST':
        form = JobApplicationForm(request.POST, request.FILES)
        if form.is_valid():
            application = form.save(commit=False)
            application.job = job
            application.applicant = request.user
            application.save()
            
            # Track as positive preference
            JobPreference.objects.get_or_create(
                user=request.user,
                job=job,
                preference_type='applied'
            )
            
            messages.success(request, 'Application submitted successfully!')
            return redirect('user_dashboard')
    else:
        form = JobApplicationForm()
    
    return render(request, 'jobs/apply_job.html', {'form': form, 'job': job})


@login_required
def my_applications(request):
    """View all user's job applications"""
    applications = JobApplication.objects.filter(applicant=request.user).select_related('job')
    return render(request, 'jobs/my_applications.html', {'applications': applications})


# ============== RECRUITER PANEL ==============

@login_required
def recruiter_dashboard(request):
    """Recruiter Dashboard"""
    profile, redirect_response = ensure_profile_exists(request)
    if redirect_response:
        return redirect_response
    
    if profile.user_type != 'recruiter':
        return redirect('user_dashboard')
    
    my_jobs = Job.objects.filter(posted_by=request.user).annotate(
        application_count=Count('applications')
    )
    
    # Get recent applications across all jobs
    recent_applications = JobApplication.objects.filter(
        job__posted_by=request.user
    ).select_related('job', 'applicant', 'applicant__profile').order_by('-applied_at')[:10]
    
    # Count stats
    total_applications = JobApplication.objects.filter(job__posted_by=request.user).count()
    pending_applications = JobApplication.objects.filter(job__posted_by=request.user, status='pending').count()
    shortlisted = JobApplication.objects.filter(job__posted_by=request.user, status='shortlisted').count()
    
    context = {
        'profile': profile,
        'jobs': my_jobs[:5],
        'active_jobs': my_jobs.filter(is_active=True).count(),
        'total_applications': total_applications,
        'pending_applications': pending_applications,
        'top_candidates': shortlisted,
        'recent_applications': recent_applications,
    }
    return render(request, 'jobs/recruiter_dashboard.html', context)


@login_required
def recruiter_jobs(request):
    """List all jobs posted by recruiter"""
    profile = get_user_profile(request)
    if not profile or profile.user_type != 'recruiter':
        messages.error(request, 'Please log in as a recruiter to access this page.')
        return redirect('accounts:recruiter_login')
    
    jobs = Job.objects.filter(posted_by=request.user).annotate(
        application_count=Count('applications')
    )
    return render(request, 'jobs/recruiter_jobs.html', {'jobs': jobs})


@login_required
def post_job(request):
    """Post a new job"""
    profile = get_user_profile(request)
    if not profile or profile.user_type != 'recruiter':
        messages.error(request, 'Please log in as a recruiter to post jobs.')
        return redirect('accounts:recruiter_login')
    
    if request.method == 'POST':
        form = JobForm(request.POST)
        if form.is_valid():
            job = form.save(commit=False)
            job.posted_by = request.user
            job.save()
            messages.success(request, 'Job posted successfully!')
            return redirect('recruiter_dashboard')
    else:
        form = JobForm()
    
    return render(request, 'jobs/post_job.html', {'form': form})


@login_required
def edit_job(request, job_id):
    """Edit an existing job"""
    profile = get_user_profile(request)
    if not profile or profile.user_type != 'recruiter':
        messages.error(request, 'Please log in as a recruiter to edit jobs.')
        return redirect('accounts:recruiter_login')
    
    job = get_object_or_404(Job, id=job_id, posted_by=request.user)
    
    if request.method == 'POST':
        form = JobForm(request.POST, instance=job)
        if form.is_valid():
            form.save()
            messages.success(request, 'Job updated successfully!')
            return redirect('recruiter_jobs')
    else:
        form = JobForm(instance=job)
    
    return render(request, 'jobs/edit_job.html', {'form': form, 'job': job})


@login_required
def delete_job(request, job_id):
    """Delete a job posting"""
    profile = get_user_profile(request)
    if not profile or profile.user_type != 'recruiter':
        messages.error(request, 'Please log in as a recruiter to delete jobs.')
        return redirect('accounts:recruiter_login')
    
    job = get_object_or_404(Job, id=job_id, posted_by=request.user)
    if request.method == 'POST':
        job.delete()
        messages.success(request, 'Job deleted successfully!')
        return redirect('recruiter_jobs')
    return render(request, 'jobs/delete_job.html', {'job': job})


@login_required
def view_all_applications(request):
    """View all applications across all jobs grouped by job with AI ranking"""
    profile = get_user_profile(request)
    if not profile or profile.user_type != 'recruiter':
        messages.error(request, 'Please log in as a recruiter to view applications.')
        return redirect('accounts:recruiter_login')
    
    # Get all recruiter's jobs
    jobs = Job.objects.filter(posted_by=request.user).prefetch_related(
        'applications__applicant__profile'
    ).order_by('-created_at')
    
    # Filter by job if specified
    job_filter = request.GET.get('job')
    if job_filter:
        jobs = jobs.filter(id=job_filter)
    
    # Filter by status if specified
    status_filter = request.GET.get('status')
    
    # Group applications by job
    jobs_with_applications = []
    total_applications = 0
    
    for job in jobs:
        applications = job.applications.select_related('applicant', 'applicant__profile').order_by('-applied_at')
        
        # Filter by status if specified
        if status_filter:
            applications = applications.filter(status=status_filter)
        
        if applications.exists() or not job_filter:  # Show all jobs if no filter, or only jobs with apps if filtered
            ranked_applications = rank_applications(job, applications)
            jobs_with_applications.append({
                'job': job,
                'applications': ranked_applications,
                'count': len(ranked_applications),
            })
            total_applications += len(ranked_applications)
    
    context = {
        'jobs_with_applications': jobs_with_applications,
        'jobs': Job.objects.filter(posted_by=request.user),
        'selected_job': int(job_filter) if job_filter else None,
        'selected_status': status_filter,
        'total_applications': total_applications,
    }
    return render(request, 'jobs/view_applications.html', context)


@login_required
def view_applications(request, job_id):
    """View and rank applications for a job"""
    profile = get_user_profile(request)
    if not profile or profile.user_type != 'recruiter':
        messages.error(request, 'Please log in as a recruiter to view applications.')
        return redirect('accounts:recruiter_login')
    
    job = get_object_or_404(Job, id=job_id, posted_by=request.user)
    applications = JobApplication.objects.filter(job=job).select_related('applicant')
    
    # Rank applications using AI
    ranked_applications = rank_applications(job, applications)
    
    context = {
        'job': job,
        'applications': ranked_applications,
        'top_candidates': ranked_applications[:3] if len(ranked_applications) >= 3 else ranked_applications,
    }
    return render(request, 'jobs/view_applications.html', context)


@login_required
def update_application_status(request, application_id):
    """Update application status"""
    profile = get_user_profile(request)
    if not profile or profile.user_type != 'recruiter':
        messages.error(request, 'Please log in as a recruiter to update applications.')
        return redirect('accounts:recruiter_login')
    
    application = get_object_or_404(JobApplication, id=application_id, job__posted_by=request.user)
    
    if request.method == 'POST':
        new_status = request.POST.get('status')
        if new_status in dict(JobApplication.STATUS_CHOICES):
            application.status = new_status
            application.save()
            messages.success(request, f'Application status updated to {new_status}.')
    
    return redirect('view_applications', job_id=application.job.id)


@login_required
def view_candidate(request, application_id):
    """View detailed candidate profile"""
    recruiter_profile = get_user_profile(request)
    if not recruiter_profile or recruiter_profile.user_type != 'recruiter':
        messages.error(request, 'Please log in as a recruiter to view candidates.')
        return redirect('accounts:recruiter_login')
    
    application = get_object_or_404(JobApplication, id=application_id, job__posted_by=request.user)
    
    # Handle status update
    if request.method == 'POST':
        new_status = request.POST.get('status')
        if new_status in dict(JobApplication.STATUS_CHOICES):
            application.status = new_status
            
            # Handle rejection reason
            if new_status == 'rejected':
                rejection_reason = request.POST.get('rejection_reason', '').strip()
                if rejection_reason:
                    application.rejection_reason = rejection_reason
                    messages.success(request, f'Application rejected with feedback sent to candidate.')
                else:
                    messages.warning(request, 'Application rejected. Consider providing feedback to help the candidate.')
            else:
                # Clear rejection reason if status is changed from rejected to something else
                application.rejection_reason = ''
            
            application.save()
            if new_status != 'rejected':
                messages.success(request, f'Application status updated to {application.get_status_display()}.')
    
    try:
        profile = application.applicant.profile
    except:
        profile = None
    
    # Generate fresh XAI data for AI Analysis
    from .ai_service import _build_xai, _build_resume_text, _build_job_text, _calculate_feature_importance
    from .ai_service import ranker
    from sklearn.metrics.pairwise import cosine_similarity
    
    xai_data = None
    feature_importance = None
    similarity_score = 0.0
    skill_score = 0.0
    exp_score = 0.0
    
    # Build resume text
    resume_text, source = _build_resume_text(application)
    
    if resume_text and hasattr(ranker, 'model') and ranker.model is not None:
        try:
            # Generate XAI data
            xai_data = _build_xai(
                application.job,
                resume_text,
                candidate_id=application.applicant.id,
                job_description=application.job.description
            )
            
            # Calculate scores
            job_text = _build_job_text(application.job, application.job.description)
            if job_text:
                job_emb = ranker.model.encode(job_text)
                resume_emb = ranker.model.encode(resume_text)
                similarity_score = float(cosine_similarity([resume_emb], [job_emb])[0][0] * 100)
            
            # Calculate skill score
            from .ai_service import _split_skills
            job_skills = _split_skills(application.job.skills_required)
            if job_skills and xai_data:
                skill_score = (len(xai_data['matched_skills']) / len(job_skills)) * 100
            
            # Calculate experience score
            if application.job.experience_required and xai_data and xai_data['experience_years'] is not None:
                exp_score = min(100.0, (xai_data['experience_years'] / application.job.experience_required) * 100)
            
            # Calculate feature importance
            weights = {
                'similarity': 0.7,
                'skills': 0.2 if job_skills else 0.0,
                'experience': 0.1 if exp_score else 0.0,
            }
            total_weight = sum(weights.values()) or 1.0
            
            feature_importance = _calculate_feature_importance(
                [similarity_score, skill_score, exp_score],
                [weights['similarity'], weights['skills'], weights['experience']]
            )
        except Exception as e:
            import logging
            logger = logging.getLogger(__name__)
            logger.error(f"Error generating XAI data: {e}")
    
    context = {
        'application': application,
        'candidate': application.applicant,
        'profile': profile,
        'xai_data': xai_data,
        'similarity_score': round(similarity_score, 1),
        'skill_score': round(skill_score, 1),
        'exp_score': round(exp_score, 1),
        'feature_importance': feature_importance,
    }
    return render(request, 'jobs/view_candidate.html', context)


# Legacy view
def job_list(request):
    jobs = Job.objects.filter(is_active=True)
    return render(request, 'jobs/job_list.html', {'jobs': jobs})


# ============== API ENDPOINTS ==============

@require_http_methods(["POST"])
@login_required
def rank_applications_api(request, job_id=None):
    """API endpoint for ranking candidates using AI"""
    try:
        profile = get_user_profile(request)
        if not profile or profile.user_type != 'recruiter':
            return JsonResponse({'error': 'Recruiter access required'}, status=403)
        
        # Parse request body
        data = json.loads(request.body)
        job_description = data.get('job_description', '')
        
        if not job_description:
            return JsonResponse({'error': 'Job description required'}, status=400)
        
        # Get applications based on job_id or filtered applications
        if job_id:
            # Rank for specific job
            job = get_object_or_404(Job, id=job_id, posted_by=request.user)
            applications = JobApplication.objects.filter(job=job).select_related('applicant', 'applicant__profile')
        else:
            # Rank all applications (from applications page)
            job_filter = data.get('job_id')
            applications = JobApplication.objects.filter(
                job__posted_by=request.user
            ).select_related('job', 'applicant', 'applicant__profile')
            
            if job_filter:
                applications = applications.filter(job_id=job_filter)
                job = get_object_or_404(Job, id=job_filter, posted_by=request.user)
            else:
                job = None
        
        if not applications.exists():
            return JsonResponse({
                'success': True,
                'candidates': [],
                'total': 0,
                'message': 'No applications found'
            })
        
        # Rank applications using AI
        ranked_applications = rank_applications(
            job,
            applications,
            job_description=job_description,
        )
        
        # Format response
        candidates = []
        for app in ranked_applications[:10]:  # Top 10 candidates
            try:
                xai_data = getattr(app, 'xai_data', None)
                explanation = app.ranking_notes or ''
                matched_skills = []
                missing_skills = []
                experience_years = 0
                similar_role = False
                similar_role_success = None

                if xai_data:
                    explanation = xai_data.get('explanation', explanation)
                    matched_skills = xai_data.get('matched_skills', [])
                    missing_skills = xai_data.get('missing_skills', [])
                    experience_years = xai_data.get('experience_years') or 0
                    similar_role = bool(xai_data.get('similar_role'))
                    similar_role_success = xai_data.get('similar_role_success')

                candidates.append({
                    'id': app.id,
                    'name': app.applicant.get_full_name() or app.applicant.username,
                    'email': app.applicant.email,
                    'rank_score': round(app.match_score, 1),
                    'skills_list': matched_skills,
                    'missing_skills': missing_skills,
                    'experience_years': experience_years,
                    'similar_role': similar_role,
                    'explanation': explanation,
                    'similar_role_success': similar_role_success,
                })
            except Exception as e:
                logger.warning(f"Error formatting candidate {app.id}: {str(e)}")
                continue
        
        logger.info(f"Ranked {len(candidates)} candidates")
        
        return JsonResponse({
            'success': True,
            'candidates': candidates,
            'total': len(candidates)
        })
    
    except json.JSONDecodeError:
        return JsonResponse({'error': 'Invalid JSON request'}, status=400)
    except Exception as e:
        logger.error(f"Error ranking applications: {str(e)}")
        return JsonResponse({'error': str(e)}, status=500)


# ============== BEHAVIORAL TRACKING APIs ==============

@login_required
@require_http_methods(["POST"])
def track_job_view(request):
    """
    API endpoint to track how long a user spent viewing a job.
    Called via JavaScript when user leaves the job detail page.
    """
    try:
        data = json.loads(request.body)
        job_id = data.get('job_id')
        time_spent = data.get('time_spent_seconds', 0)
        source = data.get('source', 'direct')
        
        if not job_id or time_spent < 0:
            return JsonResponse({'error': 'Invalid data'}, status=400)
        
        job = get_object_or_404(Job, id=job_id)
        
        # Update the most recent JobView for this user/job
        recent_view = JobView.objects.filter(
            user=request.user,
            job=job
        ).order_by('-viewed_at').first()
        
        if recent_view:
            recent_view.time_spent_seconds = max(recent_view.time_spent_seconds, time_spent)
            recent_view.save()
        else:
            JobView.objects.create(
                user=request.user,
                job=job,
                time_spent_seconds=time_spent,
                source=source
            )
        
        return JsonResponse({'success': True})
    
    except json.JSONDecodeError:
        return JsonResponse({'error': 'Invalid JSON'}, status=400)
    except Exception as e:
        logger.error(f"Error tracking job view: {e}")
        return JsonResponse({'error': str(e)}, status=500)


@login_required
@require_http_methods(["POST"])
def track_job_preference(request):
    """
    API endpoint to track user preferences (saved, rejected, ignored).
    """
    try:
        data = json.loads(request.body)
        job_id = data.get('job_id')
        preference_type = data.get('preference_type')
        
        if not job_id or preference_type not in ['saved', 'rejected', 'ignored']:
            return JsonResponse({'error': 'Invalid data'}, status=400)
        
        job = get_object_or_404(Job, id=job_id)
        
        # Create or update preference
        preference, created = JobPreference.objects.get_or_create(
            user=request.user,
            job=job,
            preference_type=preference_type
        )
        
        action = 'created' if created else 'updated'
        return JsonResponse({
            'success': True,
            'action': action,
            'preference_type': preference_type
        })
    
    except json.JSONDecodeError:
        return JsonResponse({'error': 'Invalid JSON'}, status=400)
    except Exception as e:
        logger.error(f"Error tracking preference: {e}")
        return JsonResponse({'error': str(e)}, status=500)
