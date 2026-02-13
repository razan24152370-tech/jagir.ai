# Netflix-Style Personalized Job Feed Implementation Guide

## Overview

Your AI system now includes **Netflix-style personalization** that learns from user behavior to create a personalized job feed for each user.

## How It Works

### 1. **User Embedding Vector**
Each user has a dynamic embedding that combines:
- **Base Signal (1.0x weight)**: Resume/profile text
- **Applied Jobs (0.5x weight)**: Strong positive signal
- **Viewed Jobs (0.1-0.4x weight)**: Based on time spent (max at 5 minutes)
- **Saved Jobs (0.4x weight)**: Interest signal
- **Rejected Jobs (-0.3x weight)**: Negative signal

### 2. **Behavioral Tracking**
System automatically tracks:
- ✅ Job views (when user visits job detail page)
- ✅ Time spent on each job (via JavaScript)
- ✅ Applied jobs (positive preference)
- ✅ Saved jobs (interest signal)
- ✅ Rejected jobs (negative signal)
- ✅ Ignored jobs (passive disinterest)

### 3. **Collaborative Filtering**
Boosts job scores based on similar users:
- Finds users with similar skills
- If they applied to a job, boosts that job's score
- Up to +10 points boost

### 4. **Smart Filtering**
Feed automatically excludes:
- Jobs already applied to
- Jobs explicitly rejected
- Jobs marked as ignored

## Database Schema

### New Models

**JobView** - Tracks engagement
```python
- user: ForeignKey
- job: ForeignKey
- viewed_at: DateTime
- time_spent_seconds: Integer
- source: String (search/recommendations/browse/direct)
```

**JobPreference** - Tracks explicit preferences
```python
- user: ForeignKey
- job: ForeignKey
- preference_type: String (applied/rejected/saved/ignored)
- created_at: DateTime
```

## API Endpoints

### Track Job View
```
POST /jobs/api/track-view/
Body: {
    "job_id": 123,
    "time_spent_seconds": 45,
    "source": "recommendations"
}
```

### Track Preference
```
POST /jobs/api/track-preference/
Body: {
    "job_id": 123,
    "preference_type": "saved"  # or rejected, ignored
}
```

## Frontend Integration

### 1. Include JavaScript
Add to your job detail template:
```html
{% load static %}
<script src="{% static 'jobs/behavioral_tracking.js' %}"></script>
```

### 2. Add data-job-id Attribute
```html
<body data-job-id="{{ job.id }}">
    <!-- or -->
<main data-job-id="{{ job.id }}">
```

### 3. Add Action Buttons
```html
<!-- Save button -->
<button data-action="save-job" data-job-id="{{ job.id }}">
    💾 Save Job
</button>

<!-- Not interested -->
<button data-action="reject-job" data-job-id="{{ job.id }}">
    ❌ Not Interested
</button>

<!-- Ignore (passive) -->
<button data-action="ignore-job" data-job-id="{{ job.id }}">
    👁️ Hide
</button>
```

## Migration

Run migrations to create new tables:
```bash
python manage.py migrate jobs
```

## Testing Personalization

### 1. Create Test User
```python
from django.contrib.auth.models import User
from accounts.models import Profile

user = User.objects.create_user('test_user', 'test@test.com', 'password')
profile = Profile.objects.create(user=user, user_type='jobseeker')
```

### 2. Simulate Behavior
```python
from jobs.models import Job, JobView, JobPreference

# View some jobs
job1 = Job.objects.first()
JobView.objects.create(user=user, job=job1, time_spent_seconds=120)

# Save a job
JobPreference.objects.create(user=user, job=job1, preference_type='saved')

# Reject a job
job2 = Job.objects.all()[1]
JobPreference.objects.create(user=user, job=job2, preference_type='rejected')
```

### 3. Test Recommendations
```python
from jobs.ai_service import get_job_recommendations

jobs = Job.objects.filter(is_active=True)
recs = get_job_recommendations(profile, jobs, use_personalization=True)

# Check that:
# - Rejected jobs are filtered out
# - Applied jobs are filtered out
# - Scores reflect behavioral history
```

## Performance Optimization

### 1. Query Optimization
The system uses select_related and limits to optimize:
- Last 20 applied jobs
- Last 10 rejected jobs
- Last 15 viewed jobs (10+ seconds)
- Last 10 saved jobs

### 2. Time Window
Only uses last 90 days of behavioral data to keep embeddings fresh.

### 3. Collaborative Filtering
Limited to 50 similar applicants per job to prevent slow queries.

## Monitoring

### Check Engagement
```python
from jobs.models import JobView
from django.db.models import Avg, Sum

# Average time spent per job
JobView.objects.aggregate(Avg('time_spent_seconds'))

# Most engaged users
JobView.objects.values('user').annotate(
    total_time=Sum('time_spent_seconds')
).order_by('-total_time')
```

### Check Preferences
```python
from jobs.models import JobPreference

# User preference breakdown
JobPreference.objects.values('preference_type').annotate(
    count=Count('id')
)
```

## Benefits

### For Users
- ✅ More relevant job recommendations over time
- ✅ Feed adapts to their interests
- ✅ Saves time by filtering out unwanted jobs
- ✅ Discovers jobs similar to ones they liked

### For Platform
- ✅ Higher engagement (users spend more time)
- ✅ Better match quality (higher application rates)
- ✅ Reduced noise (fewer irrelevant applications)
- ✅ Competitive advantage (Netflix-style UX)

### Metrics to Track
- **Engagement Rate**: Average time spent per job view
- **Conversion Rate**: Views → Applications ratio
- **Return Rate**: How often users come back
- **Match Quality**: Application → Interview ratio

## Advanced Features (Future)

### 1. A/B Testing
Compare personalized vs non-personalized feeds:
```python
# Randomly assign 50% to personalized
use_personalization = user.id % 2 == 0
recs = get_job_recommendations(profile, jobs, use_personalization)
```

### 2. Diversity Injection
Occasionally show jobs outside user's typical interests:
```python
# 20% of feed = exploration
if random.random() < 0.2:
    job = random.choice(unexplored_jobs)
```

### 3. Recency Boost
Boost newer jobs to keep feed fresh:
```python
days_old = (timezone.now() - job.created_at).days
recency_boost = max(0, 10 - days_old)  # +10 for brand new, 0 after 10 days
```

### 4. Salary Optimization
Learn user's salary expectations from accepted/rejected offers:
```python
# Track jobs with salary ranges user accepts/rejects
# Build salary preference model
```

## Troubleshooting

### Issue: Personalization not working
**Check:**
1. User has uploaded PDF resume
2. Behavioral data exists (JobView/JobPreference records)
3. `use_personalization=True` in get_job_recommendations()

### Issue: Same jobs keep appearing
**Check:**
1. JobPreference records are being created on apply
2. Filters are working (applied/rejected/ignored)
3. Enough diverse jobs in database

### Issue: JavaScript tracking not working
**Check:**
1. behavioral_tracking.js is loaded
2. data-job-id attribute exists on page
3. CSRF token is valid
4. Check browser console for errors

## Example Output

### Without Personalization
```
Job A: 65% match (skills only)
Job B: 58% match
Job C: 72% match
```

### With Personalization
```
Job A: 75% match (65% base + 10% collaborative boost)
Job B: [filtered out - user rejected similar job]
Job C: 82% match (72% base + 10% from viewing similar jobs)
Job D: 68% match (new discovery based on applied jobs)
```

## Production Checklist

- [x] Migrations applied
- [x] JavaScript file included in templates
- [x] Action buttons added to UI
- [x] API endpoints secured with login_required
- [ ] Add data-job-id to job detail template
- [ ] Add preference buttons to browse page
- [ ] Set up monitoring dashboard
- [ ] Create analytics queries
- [ ] Document A/B testing plan

## Next Steps

1. **Run Migration**: `python manage.py migrate jobs`
2. **Update Templates**: Add data-job-id and action buttons
3. **Test With Real Users**: Monitor engagement metrics
4. **Iterate**: Adjust weights based on user feedback

Your job feed will now learn and improve over time, just like Netflix! 🎯
