"""
Test script to demonstrate the improved dynamic AI Analysis for applicant viewing.

This script:
1. Creates a test recruiter and jobseeker
2. Creates a job with specific skills
3. Creates an application with a resume
4. Shows the dynamic XAI data that will be displayed
"""
import os
import django

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'ProRecruiterAI.settings')
django.setup()

from django.contrib.auth.models import User
from accounts.models import Profile
from jobs.models import Job, JobApplication
from jobs.ai_service import _build_xai, _build_resume_text, _build_job_text, _calculate_feature_importance, ranker
from sklearn.metrics.pairwise import cosine_similarity

def main():
    print("=" * 70)
    print("TESTING DYNAMIC AI ANALYSIS FOR APPLICANT VIEWING")
    print("=" * 70)
    
    # Clean up existing test data
    User.objects.filter(username__in=['test_recruiter_ai', 'test_jobseeker_ai']).delete()
    
    # Create recruiter
    recruiter = User.objects.create_user(
        username='test_recruiter_ai',
        email='recruiter_ai@test.com',
        password='test123',
        first_name='Test',
        last_name='Recruiter'
    )
    recruiter_profile = Profile.objects.create(
        user=recruiter,
        user_type='recruiter',
        company_name='TechCorp',
    )
    print(f"\n✓ Created recruiter: {recruiter.username}")
    
    # Create jobseeker with skills
    jobseeker = User.objects.create_user(
        username='test_jobseeker_ai',
        email='jobseeker_ai@test.com',
        password='test123',
        first_name='Jane',
        last_name='Developer'
    )
    jobseeker_profile = Profile.objects.create(
        user=jobseeker,
        user_type='jobseeker',
        skills='Python, Django, Machine Learning, SQL, Git',
        experience_years=5,
        education='BS Computer Science',
        bio='Experienced Python developer with 5 years in ML and web development.'
    )
    print(f"✓ Created jobseeker: {jobseeker.username}")
    print(f"  Skills: {jobseeker_profile.skills}")
    print(f"  Experience: {jobseeker_profile.experience_years} years")
    
    # Create job
    job = Job.objects.create(
        title='Senior Python Developer',
        description='We need an experienced Python developer with ML experience.',
        company='TechCorp',
        location='San Francisco, CA',
        salary_min=120000,
        salary_max=150000,
        job_type='full_time',
        skills_required='Python, Django, Machine Learning, AWS',
        experience_required=4,
        posted_by=recruiter,
        is_active=True
    )
    print(f"\n✓ Created job: {job.title}")
    print(f"  Required skills: {job.skills_required}")
    print(f"  Required experience: {job.experience_required} years")
    
    # Create application
    application = JobApplication.objects.create(
        job=job,
        applicant=jobseeker,
        cover_letter='I am excited to apply for this position. I have 5 years of experience with Python, Django, and Machine Learning.'
    )
    print(f"\n✓ Created application for {jobseeker.get_full_name()}")
    
    # Generate XAI data (this is what the view will now do dynamically)
    print("\n" + "=" * 70)
    print("DYNAMIC AI ANALYSIS GENERATION")
    print("=" * 70)
    
    resume_text, source = _build_resume_text(application)
    print(f"\n1. Resume Source: {source}")
    
    if not resume_text:
        print(f"   ⚠️  No PDF resume uploaded - Using profile text as demonstration")
        # Build resume text from profile for demonstration
        profile = jobseeker_profile
        resume_text = f"""
        Name: {jobseeker.get_full_name()}
        Education: {profile.education}
        Experience: {profile.experience_years} years
        Skills: {profile.skills}
        Bio: {profile.bio}
        
        Professional Summary:
        I am an experienced Python developer with {profile.experience_years} years of professional experience.
        My expertise includes {profile.skills}. I have worked on various web development and machine learning
        projects using Python, Django, and modern ML frameworks. I hold a {profile.education} degree and
        have successfully delivered multiple production-level applications.
        """
    
    print(f"   Resume Text Length: {len(resume_text)} characters")
    
    if resume_text and hasattr(ranker, 'model') and ranker.model is not None:
        # Generate XAI data
        xai_data = _build_xai(
            job,
            resume_text,
            candidate_id=jobseeker.id,
            job_description=job.description
        )
        
        print(f"\n2. XAI Data Generated:")
        print(f"   ✓ Matched Skills: {', '.join(xai_data['matched_skills']) if xai_data['matched_skills'] else 'None'}")
        print(f"   ✗ Missing Skills: {', '.join(xai_data['missing_skills']) if xai_data['missing_skills'] else 'None'}")
        print(f"   📅 Experience Years: {xai_data['experience_years']}")
        
        # Calculate similarity score
        job_text = _build_job_text(job, job.description)
        job_emb = ranker.model.encode(job_text)
        resume_emb = ranker.model.encode(resume_text)
        similarity_score = float(cosine_similarity([resume_emb], [job_emb])[0][0] * 100)
        
        # Calculate skill score
        from jobs.ai_service import _split_skills
        job_skills = _split_skills(job.skills_required)
        skill_score = (len(xai_data['matched_skills']) / len(job_skills)) * 100 if job_skills else 0
        
        # Calculate experience score
        exp_score = min(100.0, (xai_data['experience_years'] / job.experience_required) * 100) if xai_data['experience_years'] is not None else 0
        
        print(f"\n3. Score Components:")
        print(f"   📊 Similarity Score: {similarity_score:.1f}%")
        print(f"   🎯 Skills Score: {skill_score:.1f}% ({len(xai_data['matched_skills'])}/{len(job_skills)} skills matched)")
        print(f"   💼 Experience Score: {exp_score:.1f}%")
        
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
        
        # Calculate final score
        final_score = (
            similarity_score * weights['similarity']
            + skill_score * weights['skills']
            + exp_score * weights['experience']
        ) / total_weight
        
        print(f"\n4. Feature Importance:")
        print(f"   📈 Similarity: {feature_importance[0]:.0f}% of total score")
        print(f"   🎯 Skills: {feature_importance[1]:.0f}% of total score")
        print(f"   💼 Experience: {feature_importance[2]:.0f}% of total score")
        
        print(f"\n5. Final Match Score: {final_score:.1f}%")
        
        # Market insights
        if xai_data.get('market_insights'):
            print(f"\n6. Market Insights:")
            if xai_data['market_insights'].get('market_success_rate'):
                print(f"   📊 Market Success Rate: {xai_data['market_insights']['market_success_rate']:.1f}%")
                print(f"   👥 Sample Size: {xai_data['market_insights']['sample_size']} profiles")
            
            if xai_data['market_insights'].get('upskilling_recommendations'):
                print(f"   💡 Upskilling Recommendations:")
                for rec in xai_data['market_insights']['upskilling_recommendations']:
                    print(f"      • {rec['skill']}: {rec['success_rate']:.0f}% success rate")
        else:
            print(f"\n6. Market Insights: Not available for this role")
        
        print("\n" + "=" * 70)
        print("WHAT THE RECRUITER WILL NOW SEE")
        print("=" * 70)
        print(f"""
When viewing this application, the recruiter will see:

✅ Skills Match: {len(xai_data['matched_skills'])}/{len(job_skills)} required skills ({skill_score:.0f}%)
   ✓ Matched: {', '.join(xai_data['matched_skills'])}
   ✗ Missing: {', '.join(xai_data['missing_skills'])}

💼 Experience: {xai_data['experience_years']} years (Required: {job.experience_required} years - {exp_score:.0f}%)

📊 Market Insights: {'Available' if xai_data.get('market_insights') else 'Not available for this role'}

📈 AI Score Breakdown:
   • Similarity: {similarity_score:.1f}% ({feature_importance[0]:.0f}% of total score)
   • Skills: {skill_score:.1f}% ({feature_importance[1]:.0f}% of total score)
   • Experience: {exp_score:.1f}% ({feature_importance[2]:.0f}% of total score)

🎯 Final Match Score: {final_score:.1f}%

This data is now DYNAMIC and regenerated on every page view!
        """)
    else:
        print("\n⚠️ AI model not available or no resume text")
    
    print("\n" + "=" * 70)
    print("TEST COMPLETE")
    print("=" * 70)
    print(f"\n📝 To view this in the UI:")
    print(f"   1. Login as recruiter: http://127.0.0.1:8000/accounts/recruiter/login/")
    print(f"      Username: test_recruiter_ai")
    print(f"      Password: test123")
    print(f"   2. Go to Applications and click on Jane Developer's application")
    print(f"   3. See the dynamic AI Analysis with full breakdown!")
    print()

if __name__ == '__main__':
    main()
