# Build Link — Multi-page website

This version uses REAL separate HTML pages. Navigation links use filenames rather than section anchors.

## Run with Flask

PowerShell:

```powershell
py -m venv .venv
.\.venv\Scripts\Activate.ps1
py -m pip install -r requirements.txt
py app.py
```

Open http://127.0.0.1:5000. The first run creates `buildlink.db` automatically.

The Flask server serves all pages and assets, and the forms submit JSON to SQLite. Every submission is stored in the `submissions` table; project and contractor onboarding submissions are also indexed in their dedicated tables. `GET /api/health` can be used as a quick server check.

## Pages
- index.html — Home
- about.html — About
- how-it-works.html — How it works
- services.html — Services
- categories.html — Categories
- find-contractors.html — Contractor search
- contractor-profile.html — Contractor profile
- projects.html — Project opportunities
- project-details.html — Project details
- connect.html — Connection request
- connections.html — My connections
- messages.html — Messages
- post-project.html — Post requirement
- login.html — Login
- signup.html — Account type selection
- company-onboarding.html — Company onboarding
- contractor-onboarding.html — Contractor onboarding
- contractor-dashboard.html — Contractor dashboard
- contact.html — Contact

