# Project MindRush — Public competition prototype

## Local run
1. Install Python 3.10+.
2. In this folder run:
   `python -m venv .venv`
3. Activate it:
   - Windows PowerShell: `.venv\Scripts\Activate.ps1`
   - macOS/Linux: `source .venv/bin/activate`
4. Install packages: `python -m pip install -r requirements.txt`
5. Run: `python app.py`
6. Visit http://127.0.0.1:5000

## Public deployment (Render)
1. Create a GitHub account if you don't already have one.
2. Create a new repository and upload `app.py`, `requirements.txt`, and `render.yaml`.
3. Sign in to Render and choose New > Blueprint (or create a Python web service).
4. Connect the repository and deploy.
5. Confirm the service has `SECRET_KEY` set to a generated secret. Do not publish the secret.
6. Confirm the persistent disk is mounted at `/var/data` and `DATABASE_PATH=/var/data/mindrush.sqlite3`.
7. Open the HTTPS `onrender.com` URL and test on a phone before printing a QR code.
8. Create a QR code using the final public URL only after deployment and testing.

## Important limitations before a real prize competition
- This is a prototype, not a tamper-proof competition platform. Scores are calculated on the server, but browser sessions and public web apps can still be abused (multiple attempts, bots, collusion, nickname impersonation, repeated plays).
- It currently stores every completed run, not one official attempt per person. For a fair prize competition, define whether each nickname gets one attempt and implement server-side attempt limits, rate limiting, monitoring, and an organiser review.
- SQLite on a persistent disk is fine for a small prototype. For production or larger traffic, use a managed PostgreSQL database and proper backup/restore.
- If a free hosting tier sleeps or does not support persistent disks, the app may be slow to start or scores may not persist. Check the host's current plan features before launch.
- Because the target audience is 13–16, publish clear competition terms: organiser identity/contact, eligibility and region, start/end dates and time zone, scoring and tie-break rules, prize description/value, how the winner is verified/contacted, and how a prize is collected. Avoid collecting personal data on the game page; arrange winner contact in a privacy-conscious way. Get appropriate parental/guardian consent where required.
- Confirm local promotional contest and privacy requirements before launching. Use Unacademy branding or imply official endorsement only with permission. This is an independent prototype.
- The displayed leaderboard shows the top 50 submissions, not necessarily unique players. Before awarding a prize, manually review eligibility and suspicious entries.
