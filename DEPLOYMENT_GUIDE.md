# Deployment Guide - Automated Stock Analysis

This guide covers deploying your stock analysis system to the cloud with automated daily runs.

## 🚀 Quick Deploy to Streamlit Cloud

### Step 1: Push to GitHub

```bash
# Initialize git (if not already done)
git init
git add .
git commit -m "Initial commit - Stock analysis with automation"

# Create a new repository on GitHub, then:
git remote add origin https://github.com/YOUR_USERNAME/shareMarketBot.git
git branch -M main
git push -u origin main
```

### Step 2: Deploy Dashboard to Streamlit Cloud

1. Go to [share.streamlit.io](https://share.streamlit.io)
2. Click "New app"
3. Select your GitHub repository: `YOUR_USERNAME/shareMarketBot`
4. Set main file path: `dashboard.py`
5. Click "Deploy"

Your dashboard is now live! 🎉

### Step 3: Enable Automated Analysis (GitHub Actions)

The repository includes GitHub Actions workflows that run automatically:

#### Daily Automated Run (Midnight UTC)
- **File**: `.github/workflows/daily_analysis.yml`
- **Schedule**: Daily at 12:00 AM UTC
- **What it does**: Runs all three analyses and commits results to the repo
- **No setup needed** - It's already configured!

#### Manual Trigger
- Go to your GitHub repository
- Click "Actions" tab
- Select "Manual Analysis Trigger"
- Click "Run workflow"
- Choose analysis type (all/standard/enhanced/integrated)

### Step 4: Adjust Timezone (Optional)

The default schedule is 12:00 AM UTC. To change it to your timezone:

1. Edit `.github/workflows/daily_analysis.yml`
2. Modify the cron expression:

```yaml
schedule:
  # Examples:
  - cron: '0 0 * * *'   # 12:00 AM UTC (default)
  - cron: '30 18 * * *' # 6:30 PM UTC = 12:00 AM IST
  - cron: '0 5 * * *'   # 5:00 AM UTC
```

**Cron Format**: `minute hour day month weekday`

**Common Timezones**:
- IST (India): UTC + 5:30, so 12:00 AM IST = 6:30 PM previous day UTC
- EST: UTC - 5, so 12:00 AM EST = 5:00 AM UTC
- PST: UTC - 8, so 12:00 AM PST = 8:00 AM UTC

## 📊 How It Works

```
┌─────────────────────────────────────────────────────────────┐
│                    GitHub Actions Workflow                   │
│                    (Runs Daily at Midnight)                  │
└────────────────────────┬────────────────────────────────────┘
                         │
         ┌───────────────┼───────────────┐
         │               │               │
         ▼               ▼               ▼
   ┌─────────┐    ┌──────────┐    ┌──────────┐
   │Standard │    │Enhanced  │    │Integrated│
   │Analysis │    │Analysis  │    │Analysis  │
   └────┬────┘    └────┬─────┘    └────┬─────┘
        │              │               │
        └──────────────┼───────────────┘
                       │
                       ▼
            ┌──────────────────┐
            │ Commit Results   │
            │ to GitHub        │
            └────────┬─────────┘
                     │
                     ▼
            ┌──────────────────┐
            │ Streamlit Cloud  │
            │ Auto-reloads     │
            │ Dashboard        │
            └──────────────────┘
```

## 🔐 Security & Permissions

### GitHub Token
GitHub Actions automatically provides a `GITHUB_TOKEN` with permissions to:
- Read repository code
- Write analysis results back to repo
- No additional setup needed

### Data Storage
- Analysis results stored in `nifty50_analysis/` folder
- Committed to git automatically
- Streamlit Cloud reads latest files
- History preserved in git commits

## 📁 File Structure

```
shareMarketBot/
├── .github/
│   └── workflows/
│       ├── daily_analysis.yml      # Automated daily run
│       └── manual_analysis.yml     # Manual trigger
├── nifty50_analysis/               # Results (auto-committed)
│   ├── NIFTY50_WEEKLY_*.json
│   ├── NIFTY50_WEEKLY_ENHANCED_*.json
│   └── NIFTY50_INTEGRATED_WEEKLY_*.json
├── universes/
│   └── stock_universe.py           # Centralized stock list
├── dashboard.py                    # Streamlit dashboard
├── nifty50_weekly_automation.py
├── nifty50_weekly_automation_enhanced.py
└── nifty50_weekly_integrated_analysis.py
```

## 🎯 Workflow Management

### View Workflow Status
1. Go to your GitHub repository
2. Click "Actions" tab
3. See all workflow runs (success/failure)
4. Click any run to see detailed logs

### Disable Automated Runs
Edit `.github/workflows/daily_analysis.yml` and comment out the schedule:

```yaml
on:
  # schedule:
  #   - cron: '0 0 * * *'
  workflow_dispatch:  # Keep manual trigger
```

### Enable/Disable Specific Analyses
Edit workflow file and comment out steps you don't need:

```yaml
# - name: Run Standard Analysis
#   run: python nifty50_weekly_automation.py

- name: Run Enhanced Analysis
  run: python nifty50_weekly_automation_enhanced.py

- name: Run Integrated Analysis
  run: python nifty50_weekly_integrated_analysis.py
```

## 🔧 Advanced Configuration

### Custom Environment Variables
Add secrets in GitHub repository settings:

1. Go to Settings → Secrets and variables → Actions
2. Add secrets (e.g., API keys, email credentials)
3. Use in workflow:

```yaml
env:
  CUSTOM_API_KEY: ${{ secrets.CUSTOM_API_KEY }}
```

### Notifications
Add notification steps to workflow:

```yaml
- name: Send notification
  if: always()
  uses: actions/github-script@v7
  with:
    script: |
      github.rest.issues.createComment({
        issue_number: context.issue.number,
        owner: context.repo.owner,
        repo: context.repo.repo,
        body: 'Daily analysis completed!'
      })
```

### Multiple Schedules
Run different analyses at different times:

```yaml
on:
  schedule:
    - cron: '0 0 * * *'    # Integrated - Daily midnight
    - cron: '0 12 * * *'   # Quick update - Daily noon
```

## 📊 Monitoring & Logs

### GitHub Actions Logs
- All output from analysis scripts
- Error messages and stack traces
- Download logs from Actions tab

### Artifacts
- Analysis results uploaded as artifacts
- Available for 30 days
- Download from workflow run page

### Git History
```bash
# View commit history
git log --oneline --grep="Automated analysis"

# See changes in specific file
git log -p nifty50_analysis/NIFTY50_INTEGRATED_WEEKLY_*.json
```

## 🐛 Troubleshooting

### Workflow Not Running
- ✅ Check if workflow file is in `.github/workflows/`
- ✅ Verify cron syntax is correct
- ✅ GitHub Actions must be enabled in repo settings

### Analysis Fails
- ✅ Check Actions tab for error logs
- ✅ Verify all dependencies in `requirements.txt`
- ✅ Test scripts locally before pushing

### Results Not Showing in Dashboard
- ✅ Verify results were committed to repo
- ✅ Check Streamlit Cloud logs
- ✅ Ensure dashboard reads correct file paths

### Commit Conflicts
If manual commits conflict with automated commits:
```bash
git pull --rebase origin main
git push
```

## 💰 Cost Considerations

### GitHub Actions
- ✅ **Free tier**: 2,000 minutes/month for public repos
- ✅ **Free tier**: Unlimited for public repos
- ✅ Current usage: ~30-60 minutes/day = 900-1,800 min/month
- ✅ Well within free tier!

### Streamlit Cloud
- ✅ **Free tier**: 1 app, unlimited viewers
- ✅ Auto-sleeps after inactivity
- ✅ Wakes up on access

## 🎉 You're All Set!

Your stock analysis system now:
- ✅ Runs automatically every day at midnight
- ✅ Commits results to GitHub
- ✅ Updates Streamlit dashboard automatically
- ✅ Works on any cloud platform
- ✅ No manual intervention needed
- ✅ Completely free!

Just push to GitHub and forget about it. Check your dashboard anytime for fresh analysis!
