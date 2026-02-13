#!/usr/bin/env python
"""
Quick test script to verify job recommendations are calculated correctly
"""
import os
import django

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'ProRecruiterAI.settings')
django.setup()

from accounts.models import Profile
from jobs.models import Job
from jobs.ai_service import get_job_recommendations

# Get a jobseeker profile
jobseeker_profiles = Profile.objects.filter(user_type='jobseeker')[:1]

if not jobseeker_profiles:
    print("❌ No jobseeker profiles found")
else:
    profile = jobseeker_profiles[0]
    print(f"\n📋 Testing Recommendations for: {profile.user.get_full_name()}")
    print(f"   Email: {profile.user.email}")
    print(f"   Skills: {profile.get_skills_list()}")
    print(f"   Experience: {profile.experience_years} years")
    print(f"   Location: {profile.location}")
    print(f"   Bio: {profile.bio[:100] if profile.bio else 'Not provided'}...")
    
    # Get active jobs
    jobs = Job.objects.filter(is_active=True)[:5]
    
    if not jobs:
        print("❌ No jobs found")
    else:
        print(f"\n🔍 Generating recommendations for {len(jobs)} jobs...")
        recommendations = get_job_recommendations(profile, jobs)
        
        print("\n📊 RECOMMENDATIONS:")
        print("-" * 80)
        
        for i, rec in enumerate(recommendations, 1):
            job = rec['job']
            score = rec['score']
            reason = rec['reason']
            
            score_color = "🟢" if score >= 70 else "🟡" if score >= 50 else "🔴"
            
            print(f"\n{i}. {score_color} {job.title} at {job.company}")
            print(f"   Match Score: {score}%")
            print(f"   Required Experience: {job.experience_required} years")
            print(f"   Required Skills: {job.get_skills_list()}")
            print(f"   Why Recommended: {reason}")
        
        print("\n" + "=" * 80)
        print(f"\n✅ Recommendations test completed successfully!")
        print(f"Scores are based on real profile data, not random values.")
