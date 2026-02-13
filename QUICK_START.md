# Quick Start Guide - AI Candidate Ranking

## 🚀 Get Started in 5 Minutes

### Prerequisites
- Django project running
- Python dependencies installed
- Recruiter account created

---

## Step 1: Verify Setup

```bash
# Check Django is working
python manage.py check
# Output: System check identified no issues (0 silenced).
```

---

## Step 2: Create Test Data (if needed)

```bash
python manage.py shell
```

```python
from django.contrib.auth.models import User
from jobs.models import Job
from accounts.models import Profile

# Get or create recruiter user
recruiter_user = User.objects.first()  # or create new

# Get or create recruiter profile
profile, _ = Profile.objects.get_or_create(
    user=recruiter_user,
    defaults={
        'user_type': 'recruiter',
        'company_description': 'My Company'
    }
)

# Create a sample job
job = Job.objects.create(
    title='Senior Python Developer',
    company='Tech Corp',
    posted_by=recruiter_user,
    description='5+ years Python/Django experience, AWS, PostgreSQL',
    job_type='full-time',
    is_active=True
)

print(f"Job created: {job.id}")
exit()
```

---

## Step 3: Access the Ranking Interface

1. **Start Server:**
   ```bash
   python manage.py runserver
   ```

2. **Log in as Recruiter:**
   - Visit: http://127.0.0.1:8000/accounts/recruiter_login/
   - Use recruiter credentials

3. **Go to Ranking Dashboard:**
   - Visit: http://127.0.0.1:8000/jobs/recruiter/jobs/1/applications/
   - Replace `1` with actual job ID

---

## Step 4: Rank Candidates

1. **Enter Job Description:**
   ```
   Example text:
   Senior Python developer with Django, PostgreSQL, and AWS expertise.
   5+ years experience required. Must know Docker and REST APIs.
   ```

2. **Click "Rank Candidates" Button**

3. **View Results:**
   - Top candidates with match scores
   - Skills highlighted
   - View Profile button for each candidate

---

## Step 5: View Candidate Details

- Click "View Profile" on any candidate
- See full candidate information
- Update application status
- Send feedback if needed

---

## API Usage (Advanced)

### Test API Endpoint

```bash
# Get CSRF token first (visit page in browser)
curl http://127.0.0.1:8000/jobs/recruiter/jobs/1/applications/

# Make API call
curl -X POST http://127.0.0.1:8000/jobs/api/rank/1/ \
  -H "Content-Type: application/json" \
  -H "X-CSRFToken: <your-csrf-token>" \
  -d '{"job_description": "Python developer with Django"}'
```

### Expected Response
```json
{
    "success": true,
    "total": 3,
    "candidates": [
        {
            "id": 1,
            "name": "John Doe",
            "rank_score": 95.5,
            "skills_list": ["Python", "Django", "AWS"]
        }
    ]
}
```

---

## Common Issues & Fixes

### Issue 1: Login Required
**Error:** Redirects to login page
**Fix:** Log in as recruiter first

### Issue 2: Permission Denied
**Error:** "Recruiter access required"
**Fix:** User profile must have `user_type = 'recruiter'`

### Issue 3: No Candidates
**Error:** "No applications for this job"
**Fix:** Create test applications or wait for real applications

### Issue 4: Slow Ranking (10+ seconds)
**Expected:** First time is slow (model loading)
**After:** Subsequent rankings are <500ms

---

## File Structure

```
ProRecruiterAI/
├── jobs/
│   ├── views.py              ← rank_applications_api view
│   ├── urls.py               ← /api/rank/{id}/ endpoint
│   └── templates/jobs/
│       └── recruiter_applications_dashboard.html  ← Ranking UI
├── ProRecruiterAI/
│   └── settings.py           ← LOGGING config
├── DEPLOYMENT_GUIDE.md       ← Deployment instructions
├── API_SPECIFICATION.md      ← API docs
├── IMPLEMENTATION_SUMMARY.md ← What was built
└── QUICK_START.md            ← This file
```

---

## Key URLs

| URL | Method | Purpose |
|-----|--------|---------|
| `/jobs/recruiter/jobs/1/applications/` | GET | Ranking UI page |
| `/jobs/api/rank/1/` | POST | API ranking endpoint |
| `/jobs/recruiter/candidate/1/` | GET | Candidate detail |

---

## Monitoring

### Check Logs
```bash
# View latest logs
tail -f debug.log

# Filter ranking logs
grep "Ranked" debug.log
```

### Django Shell Commands
```bash
python manage.py shell
```

```python
from jobs.models import JobApplication
apps = JobApplication.objects.all()
print(f"Total applications: {apps.count()}")
```

---

## Next Steps

1. **Add More Test Data:**
   - Create more candidates
   - Apply for jobs

2. **Customize Settings:**
   - Adjust logging level in `settings.py`
   - Change ranking weights in `ai_service.py`

3. **Deploy:**
   - Follow `DEPLOYMENT_GUIDE.md` for production setup
   - Use Railway, Heroku, or your own server

4. **Monitor Performance:**
   - Watch `debug.log` for issues
   - Track API response times

---

## Example Workflow

```
1. Recruiter posts job → Senior Python Developer
2. Candidates apply with resumes
3. Recruiter visits ranking page
4. Enters job requirements
5. AI ranks candidates by match score
6. Recruiter reviews top candidates
7. Clicks "View Profile" for best match
8. Updates application status
9. Sends feedback to selected candidates
```

---

## Testing Checklist

- [ ] Django checks pass
- [ ] Can log in as recruiter
- [ ] Can access ranking page
- [ ] Can enter job description
- [ ] API returns candidates
- [ ] Scores display correctly
- [ ] Can click View Profile
- [ ] Logs are created in debug.log

---

## Performance Tips

1. **First ranking is slow:**
   - Model loads ~10-15 seconds
   - Subsequent rankings are <500ms

2. **For large datasets:**
   - Limit to top 10 candidates
   - Use pagination if needed

3. **Optimize queries:**
   - Already uses select_related()
   - Check debug.log for slow queries

---

## Support

### Documentation Files
- `DEPLOYMENT_GUIDE.md` - Production deployment
- `API_SPECIFICATION.md` - API details
- `IMPLEMENTATION_SUMMARY.md` - Technical details

### Debug Steps
1. Check `debug.log` for errors
2. Run `python manage.py check`
3. Verify profile is recruiter type
4. Test in browser developer console

### Contact
See project documentation or create an issue on GitHub

---

## Success! 🎉

You now have a fully functional AI-powered candidate ranking system!

**Next: Try the demo workflow above →**

---

**Tips:**
- 💡 Job descriptions should be 100+ characters for best results
- ⚡ Rankings are faster after first load (model cached)
- 🔒 Only recruiters can access ranking features
- 📊 Check debug.log for performance metrics

**Happy recruiting! 🚀**
