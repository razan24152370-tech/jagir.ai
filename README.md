# ProRecruiterAI

An intelligent recruitment platform powered by AI that connects job seekers with recruiters through smart matching and CV ranking.

## Features

### 🎯 User Panel (Job Seekers)

- **Profile Setup**: Create a detailed profile with skills, experience, education, and resume
- **AI Job Recommendations**: Get personalized job recommendations based on your profile
- **Job Search**: Browse and search for available job postings
- **Application Tracking**: Apply to jobs and track application status

### 👔 Recruiter Panel

- **Job Posting**: Create and manage job listings with detailed requirements
- **Receive Applications**: View all applications for your job postings
- **AI CV Ranking**: Automatically rank candidates based on skill match, experience, and more
- **Top Candidates**: See the best-matched candidates highlighted
- **Application Management**: Update application status (pending, reviewed, shortlisted, rejected, hired)
- **Team Management**: Add and manage team members with role-based access control
- **Email Invitations**: Automatically send invitation emails to new team members
- **Access Control**: Manage team member permissions and track invitation status

### 🔧 Admin Panel

- **User Management**: Manage all users and their profiles
- **Job Management**: View, edit, and manage all job postings
- **Application Oversight**: Monitor all applications across the platform
- **Bulk Actions**: Activate/deactivate jobs, update multiple applications

## Tech Stack

- **Backend**: Django 6.0
- **Database**: SQLite (development)
- **AI**: Custom matching algorithm (skill match, experience, location)
- **Email**: SMTP with Django's email system (Gmail, SendGrid, etc.)
- **Frontend**: Django Templates with custom CSS

## Setup

1. **Activate virtual environment**:

   ```bash
   # Windows
   .venv\Scripts\activate

   # macOS/Linux
   source .venv/bin/activate
   ```

2. **Run migrations**:

   ```bash
   python manage.py migrate
   ```

3. **Create a superuser** (for admin access):

   ```bash
   python manage.py createsuperuser
   ```

4. **Run the development server**:

   ```bash
   python manage.py runserver
   ```

5. **Access the application**:
   - Main site: http://127.0.0.1:8000/
   - Admin panel: http://127.0.0.1:8000/admin/

## URL Structure

### Public

- `/` - Landing page
- `/about/` - About us
- `/contact/` - Contact us

### Accounts

- `/accounts/signup/` - User registration
- `/accounts/login/` - User login
- `/accounts/profile/` - View profile
- `/accounts/profile/edit/` - Edit profile

### Jobs (User Panel)

- `/jobs/dashboard/` - User dashboard with recommendations
- `/jobs/browse/` - Browse all jobs
- `/jobs/job/<id>/` - Job details
- `/jobs/apply/<id>/` - Apply to a job
- `/jobs/my-applications/` - View your applications

### Jobs (Recruiter Panel)

- `/jobs/recruiter/` - Recruiter dashboard
- `/jobs/recruiter/jobs/` - Manage posted jobs
- `/jobs/recruiter/post/` - Post new job
- `/jobs/recruiter/edit/<id>/` - Edit job
- `/jobs/recruiter/applications/<id>/` - View applications with AI ranking

### Team Management (Recruiter Panel)

- `/accounts/team/` - View and manage team members
- `/accounts/team/add/` - Add new team member (sends invitation email)
- `/accounts/team/<id>/edit/` - Edit team member permissions
- `/accounts/team/<id>/resend/` - Resend invitation email
- `/accounts/invitation/<token>/` - Accept team invitation

## 📧 Email System

### SMTP Configuration

**✨ NEW: Configure SMTP settings directly from the admin panel!**

All email settings can now be managed from the Django admin interface:

1. **Access:** `http://localhost:8000/admin/`
2. **Navigate to:** Accounts → Email configurations
3. **Configure:** Set up Console (dev) or SMTP (production)
4. **Test:** Built-in connection testing
5. **Switch:** Activate/deactivate configurations instantly

**No code changes or server restarts required!**

For detailed instructions: [`ADMIN_SMTP_GUIDE.md`](ADMIN_SMTP_GUIDE.md)

### Email Features
The platform includes a complete email system for team member management:

- **Invitation Emails**: Automatically sent when adding team members
- **Access Notifications**: Updates when permissions change
- **Welcome Emails**: Sent after accepting invitations
- **Account Alerts**: Notifications for status changes

### Setup Options
- **Console Backend (Development)**: Emails appear in terminal - perfect for testing
- **SMTP Backend (Production)**: Configure via admin panel - Gmail, SendGrid, Mailgun, etc.

**Quick Setup:**
```bash
# Create default configuration
python setup_email_config.py

# Access admin panel and configure
http://localhost:8000/admin/
```

### Documentation
- **Admin Panel Guide**: [`ADMIN_SMTP_GUIDE.md`](ADMIN_SMTP_GUIDE.md) - Configure via web interface
- **Advanced Setup**: [`SMTP_SETUP_GUIDE.md`](SMTP_SETUP_GUIDE.md) - Detailed technical guide
- **Quick Reference**: [`QUICK_REFERENCE_SMTP.md`](QUICK_REFERENCE_SMTP.md) - Commands and snippets

### Test Email System
```bash
python test_smtp_emails.py
```

## AI Matching Algorithm

The AI service calculates match scores based on:

- **Skills Match (50%)**: Percentage of required skills the candidate has
- **Experience Match (30%)**: Years of experience vs. required experience
- **Location Match (20%)**: Location compatibility
- **Bonus Points**: Resume uploaded, cover letter provided

---

_Built with ❤️ using Django and AI_
