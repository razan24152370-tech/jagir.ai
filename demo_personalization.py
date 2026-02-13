"""
Quick Demo: Netflix-Style Personalized Job Feed
Shows how the system learns from user behavior
"""
import os
import sys
import django
from datetime import timedelta
from django.utils import timezone

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'ProRecruiterAI.settings')
django.setup()

from django.contrib.auth.models import User
from jobs.models import Job, JobView, JobPreference
from jobs.ai_service import get_job_recommendations
from accounts.models import Profile

print("=" * 70)
print("NETFLIX-STYLE PERSONALIZATION DEMO")
print("=" * 70)

# Get or create test user
try:
    user = User.objects.get(username='demo_jobseeker')
    profile = user.profile
    print(f"\n✓ Using existing user: {user.username}")
except User.DoesNotExist:
    print("\n⚙ Creating demo user...")
    user = User.objects.create_user(
        username='demo_jobseeker',
        email='demo@example.com',
        password='demo123',
        first_name='Demo',
        last_name='User'
    )
    profile = Profile.objects.create(
        user=user,
        user_type='jobseeker',
        headline='Software Developer',
        skills='Python, Django, JavaScript, SQL',
        experience_years=3
    )
    print(f"✓ Created demo user: {user.username} (password: demo123)")
except AttributeError:
    print("\n⚙ User exists but no profile. Creating profile...")
    user = User.objects.get(username='demo_jobseeker')
    profile = Profile.objects.create(
        user=user,
        user_type='jobseeker',
        headline='Software Developer',
        skills='Python, Django, JavaScript, SQL',
        experience_years=3
    )
    print(f"✓ Created profile for: {user.username}")

# Get available jobs
jobs = Job.objects.filter(is_active=True)[:10]
if not jobs:
    print("\n⚠ No active jobs found. Creating sample jobs...")
    
    # Create sample jobs for demo
    sample_jobs = [
        {
            'title': 'Senior Python Developer',
            'company': 'TechCorp Inc',
            'description': 'Looking for experienced Python developer with Django expertise',
            'skills_required': 'Python, Django, PostgreSQL, REST APIs',
            'experience_required': 5,
            'location': 'Remote',
            'job_type': 'full_time'
        },
        {
            'title': 'Machine Learning Engineer',
            'company': 'AI Solutions',
            'description': 'Build ML models and deploy them at scale',
            'skills_required': 'Python, TensorFlow, PyTorch, Scikit-learn',
            'experience_required': 3,
            'location': 'San Francisco',
            'job_type': 'full_time'
        },
        {
            'title': 'Full Stack Developer',
            'company': 'StartupXYZ',
            'description': 'Join our fast-growing startup as a full stack engineer',
            'skills_required': 'JavaScript, React, Node.js, MongoDB',
            'experience_required': 2,
            'location': 'New York',
            'job_type': 'full_time'
        },
        {
            'title': 'Data Analyst',
            'company': 'DataCo',
            'description': 'Analyze data and create insights for business decisions',
            'skills_required': 'SQL, Excel, Tableau, Python',
            'experience_required': 2,
            'location': 'Remote',
            'job_type': 'full_time'
        },
        {
            'title': 'DevOps Engineer',
            'company': 'CloudTech',
            'description': 'Manage cloud infrastructure and CI/CD pipelines',
            'skills_required': 'AWS, Docker, Kubernetes, Jenkins',
            'experience_required': 4,
            'location': 'Austin',
            'job_type': 'full_time'
        }
    ]
    
    # Need a recruiter user to post jobs
    try:
        recruiter = User.objects.filter(profile__user_type='recruiter').first()
        if not recruiter:
            recruiter = User.objects.create_user(
                username='demo_recruiter',
                email='recruiter@example.com',
                password='demo123'
            )
            Profile.objects.create(
                user=recruiter,
                user_type='recruiter',
                company_name='Demo Company'
            )
    except:
        recruiter = User.objects.first()
    
    for job_data in sample_jobs:
        Job.objects.create(posted_by=recruiter, **job_data)
    
    jobs = Job.objects.filter(is_active=True)[:10]
    print(f"✓ Created {len(jobs)} sample jobs")

print(f"\n✓ Found {len(jobs)} active jobs")

# Get recommendations WITHOUT personalization
print("\n" + "=" * 70)
print("RECOMMENDATIONS WITHOUT PERSONALIZATION (Cold Start)")
print("=" * 70)

if not profile.resume:
    print("\n⚠ Note: No resume uploaded. Using profile data only.")

recs_cold = get_job_recommendations(profile, jobs, use_personalization=False)
for i, rec in enumerate(recs_cold[:5], 1):
    print(f"{i}. {rec['job'].title:<40} Score: {rec['score']}%")

# Simulate user behavior
print("\n" + "=" * 70)
print("SIMULATING USER BEHAVIOR...")
print("=" * 70)

if len(jobs) >= 3:
    # User views job 1 for 2 minutes (strong interest)
    job1 = jobs[0]
    JobView.objects.create(
        user=user,
        job=job1,
        time_spent_seconds=120,
        source='recommendations'
    )
    print(f"✓ Viewed '{job1.title}' for 120 seconds")
    
    # User saves job 2
    job2 = jobs[1]
    JobPreference.objects.get_or_create(
        user=user,
        job=job2,
        preference_type='saved'
    )
    print(f"✓ Saved '{job2.title}'")
    
    # User rejects job 3
    job3 = jobs[2]
    JobPreference.objects.get_or_create(
        user=user,
        job=job3,
        preference_type='rejected'
    )
    print(f"✓ Rejected '{job3.title}'")

# Get recommendations WITH personalization
print("\n" + "=" * 70)
print("RECOMMENDATIONS WITH PERSONALIZATION (After Behavior)")
print("=" * 70)
recs_personalized = get_job_recommendations(profile, jobs, use_personalization=True)
for i, rec in enumerate(recs_personalized[:5], 1):
    personalized_marker = "🎯" if rec.get('personalized') else "  "
    print(f"{i}. {personalized_marker} {rec['job'].title:<40} Score: {rec['score']}%")

# Show what changed
print("\n" + "=" * 70)
print("WHAT CHANGED?")
print("=" * 70)

cold_scores = {rec['job'].id: rec['score'] for rec in recs_cold}
personalized_scores = {rec['job'].id: rec['score'] for rec in recs_personalized}

print("\nScore Changes:")
changes_found = False
for job_id in cold_scores:
    if job_id in personalized_scores:
        cold = cold_scores[job_id]
        pers = personalized_scores[job_id]
        diff = pers - cold
        if diff != 0:
            changes_found = True
            job_title = Job.objects.get(id=job_id).title
            symbol = "↑" if diff > 0 else "↓"
            print(f"{symbol} {job_title:<40} {cold}% → {pers}% ({diff:+d})")

if not changes_found:
    print("No score changes (may need resume for personalization to work)")

# Show filtered jobs
rejected_ids = set(JobPreference.objects.filter(
    user=user, preference_type='rejected'
).values_list('job_id', flat=True))

if rejected_ids:
    print(f"\n✓ Filtered out {len(rejected_ids)} rejected jobs")

# Show engagement stats
total_views = JobView.objects.filter(user=user).count()

print(f"\n" + "=" * 70)
print("USER ENGAGEMENT STATS")
print("=" * 70)
print(f"Total job views: {total_views}")
print(f"Saved jobs: {JobPreference.objects.filter(user=user, preference_type='saved').count()}")
print(f"Rejected jobs: {len(rejected_ids)}")

print("\n" + "=" * 70)
print("✓ DEMO COMPLETE")
print("=" * 70)
print("\nKey Takeaways:")
print("1. Feed adapts based on user behavior")
print("2. Rejected jobs are automatically filtered out")
print("3. Scores boost for jobs similar to ones user engaged with")
print("4. System learns preferences over time")
print("\nDemo Credentials:")
print("  Username: demo_jobseeker")
print("  Password: demo123")
print("\nNext Steps:")
print("1. Login: python manage.py runserver → /accounts/jobseeker/login/")
print("2. View personalized feed: /jobs/browse/")
print("3. Interact with jobs to see real-time adaptation!")
print("\nClean Up (optional):")
print("  python manage.py shell")
print("  >>> from django.contrib.auth.models import User")
print("  >>> User.objects.filter(username='demo_jobseeker').delete()")
print("  >>> User.objects.filter(username='demo_recruiter').delete()")
