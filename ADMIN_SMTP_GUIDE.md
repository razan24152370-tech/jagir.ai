# SMTP Configuration via Admin Panel - Quick Guide

## 🎯 Overview

You can now configure all SMTP email settings directly from the Django admin panel! No need to edit code or restart the server.

## 🚀 Quick Start

### 1. Access Admin Panel
```
http://localhost:8000/admin/
```

Login with:
- **Username:** `admin`
- **Password:** `admin`

### 2. Navigate to Email Configurations
- Click **"Accounts"** in the sidebar
- Click **"Email configurations"**

### 3. Add/Edit Configuration
Click "Add Email Configuration" or edit the existing one.

## 📝 Configuration Options

### **Console Backend (Development)**
For testing - emails print to terminal

**Settings:**
- Name: `Development (Console)`
- Backend: `Console (Development - prints to terminal)`
- Is active: ✅ Checked
- From email: `noreply@prorecruiter.ai`
- From name: `ProRecruiter AI`

### **SMTP Backend (Production)**
For sending real emails

**Gmail Example:**
- Name: `Gmail SMTP`
- Backend: `SMTP (Email Server)`
- Is active: ✅ Checked
- SMTP host: `smtp.gmail.com`
- SMTP port: `587`
- Use TLS: ✅ Checked
- Use SSL: ❌ Unchecked
- Username: `your-email@gmail.com`
- Password: `your-app-password` (16 characters)
- From email: `noreply@yourcompany.com`
- From name: `Your Company Name`

**SendGrid Example:**
- Name: `SendGrid SMTP`
- Backend: `SMTP (Email Server)`
- SMTP host: `smtp.sendgrid.net`
- SMTP port: `587`
- Use TLS: ✅ Checked
- Username: `apikey`
- Password: `your-sendgrid-api-key`

**Mailgun Example:**
- Name: `Mailgun SMTP`
- Backend: `SMTP (Email Server)`
- SMTP host: `smtp.mailgun.org`
- SMTP port: `587`
- Use TLS: ✅ Checked
- Username: `postmaster@yourdomain.com`
- Password: `your-mailgun-password`

## ✅ Testing Configuration

### Method 1: Admin Panel Actions
1. Select your configuration (checkbox)
2. Choose "Test email connection" from Actions dropdown
3. Click "Go"
4. Check for success/error message

### Method 2: Send Test Team Invitation
1. Add a team member with your test email
2. Check if email is received (or appears in console)

## 🔄 Switching Configurations

**Only ONE configuration can be active at a time.**

To switch:
1. Find the configuration you want to activate
2. Check the "Is active" checkbox
3. Click "Save"
4. ✅ Previous active config will be automatically deactivated

**Or use the Action:**
1. Select configuration (checkbox)
2. Choose "Activate configuration" from Actions
3. Click "Go"

## 🔐 Gmail Setup (Detailed)

### Step 1: Enable 2-Factor Authentication
1. Go to Google Account Security
2. Enable 2-Step Verification

### Step 2: Generate App Password
1. Google Account → Security → 2-Step Verification
2. Scroll to "App passwords"
3. Select app: "Mail"
4. Select device: "Other" → Type "ProRecruiter AI"
5. Click "Generate"
6. Copy the 16-character password

### Step 3: Configure in Admin Panel
1. Name: `Gmail SMTP`
2. Backend: `SMTP`
3. SMTP host: `smtp.gmail.com`
4. SMTP port: `587`
5. Use TLS: ✅
6. Username: `your-email@gmail.com`
7. Password: **Paste 16-char app password**
8. Is active: ✅
9. Save

### Step 4: Test
- Use "Test email connection" action
- Or send a test team invitation

## 📊 Configuration Status

View all configurations at a glance:

| Column | Description |
|--------|-------------|
| **Name** | Configuration name |
| **Backend** | Console or SMTP |
| **SMTP host** | Email server address |
| **SMTP username** | Login username |
| **Is active** | ✅ = Currently in use |
| **Updated at** | Last modification time |

## 🛠️ Admin Panel Features

### Actions
- **Test email connection** - Verify SMTP settings work
- **Activate configuration** - Make a config active

### Filters
- Backend (Console / SMTP)
- Is active (Yes / No)

### Search
Search by: name, SMTP host, username, from email

## 💡 Best Practices

### Development
- ✅ Use Console backend
- No setup required
- Emails appear in terminal
- Perfect for testing

### Staging
- ⚠️ Use real SMTP
- Test with internal emails
- Verify all email templates
- Monitor delivery rates

### Production
- ✅ Use professional SMTP service (SendGrid, Mailgun)
- Configure SPF/DKIM records
- Monitor bounce rates
- Set up alerts for failures
- Use environment-specific from addresses

## 🔒 Security

### Protecting Credentials
1. **Never share** SMTP passwords
2. **Use app passwords** (not main account passwords)
3. **Rotate passwords** regularly
4. **Monitor usage** for suspicious activity
5. **Limit access** to admin panel

### Environment Variables (Advanced)
For extra security, you can still use environment variables:

1. Set in your environment:
   ```bash
   EMAIL_HOST_USER=your-email@gmail.com
   EMAIL_HOST_PASSWORD=your-app-password
   ```

2. Configure in admin panel:
   - Leave username/password empty
   - System will fall back to environment variables

## 🐛 Troubleshooting

### Email Not Sending

**Check 1: Configuration is Active**
- Only one config can be active
- Verify checkbox is checked

**Check 2: SMTP Credentials**
- Username is correct email
- Password is app password (not account password)
- For Gmail: 2FA must be enabled

**Check 3: Test Connection**
- Use "Test email connection" action
- Read error message carefully

**Check 4: Firewall/Network**
- Port 587 (TLS) must be open
- Port 465 (SSL) must be open if using SSL
- Check corporate firewall

### Gmail "Username and Password not accepted"
- ❌ Using **account password** → ✅ Use **app password**
- ❌ 2FA not enabled → ✅ Enable 2-Step Verification first
- Clear browser cache and try again

### "Connection refused"
- Wrong SMTP host or port
- Firewall blocking connection
- Service down (check status page)

### Emails Going to Spam
- Configure SPF records for your domain
- Set up DKIM authentication
- Verify sender domain
- Use professional SMTP service

## 📚 Quick Reference

### Common SMTP Ports
- **587** - TLS (recommended)
- **465** - SSL
- **25** - Non-encrypted (not recommended)

### Email Triggers
- ✉️ Add team member → Invitation email
- ✉️ Edit permissions → Update notification
- ✉️ Deactivate account → Deactivation alert
- ✉️ Activate account → Activation notice
- ✉️ Accept invitation → Welcome email

### Admin URLs
```
http://localhost:8000/admin/
http://localhost:8000/admin/accounts/emailconfiguration/
http://localhost:8000/admin/accounts/emailconfiguration/add/
```

## 🎯 Quick Tasks

### Switch to Console (Development)
1. Admin → Email configurations
2. Find "Development (Console)"
3. Check "Is active"
4. Save

### Switch to Gmail (Production)
1. Admin → Email configurations
2. Find "Gmail SMTP" or create new
3. Fill in credentials (see Gmail Setup above)
4. Check "Is active"
5. Save
6. Test connection

### Create New Configuration
1. Admin → Email configurations → Add
2. Fill in all required fields
3. For SMTP: username and password required
4. Check "Is active" if you want to use immediately
5. Save
6. Test connection

## ✅ Checklist

Before going to production:

- [ ] SMTP configuration created in admin panel
- [ ] Credentials added and verified
- [ ] "Is active" checkbox checked
- [ ] Test connection action run successfully
- [ ] Test invitation email sent and received
- [ ] SPF/DKIM records configured (optional but recommended)
- [ ] Email monitoring set up
- [ ] Bounce handling configured

## 🆘 Support

### Resources
- Django Email Docs: https://docs.djangoproject.com/en/stable/topics/email/
- Gmail App Passwords: https://support.google.com/accounts/answer/185833
- SendGrid Docs: https://docs.sendgrid.com/
- Mailgun Docs: https://documentation.mailgun.com/

### Contact
If you encounter issues:
1. Check this guide
2. Review `SMTP_SETUP_GUIDE.md`
3. Check application logs
4. Test with console backend first

---

**Last Updated:** February 11, 2026  
**Version:** 2.0.0 - **Admin Panel Configuration**  
**Status:** ✅ Ready to Use
