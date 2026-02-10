# 🚀 Quick Start - Git & Deployment

Your project is now ready for cloud deployment with automated daily analysis!

## Step 1: Initialize Git (if not done already)

```bash
cd C:\PythonProjects\shareMarketBot
git init
git add .
git commit -m "Initial commit: Stock analysis with GitHub Actions automation"
```

## Step 2: Create GitHub Repository

1. Go to https://github.com/new
2. Repository name: `shareMarketBot` (or your preferred name)
3. Make it **Public** (required for free GitHub Actions)
4. Do NOT initialize with README (we already have one)
5. Click "Create repository"

## Step 3: Push to GitHub

```bash
# Replace YOUR_USERNAME with your GitHub username
git remote add origin https://github.com/YOUR_USERNAME/shareMarketBot.git
git branch -M main
git push -u origin main
```

## Step 4: Verify GitHub Actions

1. Go to your GitHub repository
2. Click the "Actions" tab
3. You should see two workflows:
   - ✅ Daily Stock Analysis (runs daily at midnight)
   - ✅ Manual Analysis Trigger (run on demand)

## Step 5: Deploy Dashboard to Streamlit Cloud

1. Go to https://share.streamlit.io
2. Sign in with GitHub
3. Click "New app"
4. Select:
   - Repository: `YOUR_USERNAME/shareMarketBot`
   - Branch: `main`
   - Main file path: `dashboard.py`
5. Click "Deploy"
6. Wait 2-3 minutes for deployment

## Step 6: Test Manual Trigger

Before waiting for midnight, test the automation:

1. Go to GitHub → Actions tab
2. Click "Manual Analysis Trigger"
3. Click "Run workflow" dropdown
4. Select analysis type: "all"
5. Click "Run workflow"
6. Wait 15-20 minutes for completion
7. Check your repository for new files in `nifty50_analysis/`

## Step 7: Access Your Dashboard

Your dashboard will be at:
```
https://YOUR_APP_NAME.streamlit.app
```

Or click the link shown in Streamlit Cloud deployment page.

## 🎉 You're Done!

**What happens now:**
- ✅ Analysis runs automatically every day at midnight (UTC)
- ✅ Results are committed to GitHub automatically
- ✅ Dashboard updates automatically with fresh data
- ✅ No manual work required!

**To change the schedule:**
Edit `.github/workflows/daily_analysis.yml`:
```yaml
schedule:
  - cron: '30 18 * * *'  # 6:30 PM UTC = 12:00 AM IST
```

**To manually trigger analysis:**
GitHub → Actions → Manual Analysis Trigger → Run workflow

**To view logs:**
GitHub → Actions → Click any workflow run → View logs

## 📊 What You Get

Every day you'll have fresh analysis for **503 stocks**:

1. **Standard Analysis** - Quick technical signals
2. **Enhanced Analysis** - Advanced pattern detection  
3. **Integrated Analysis** - 21-module comprehensive analysis

All available in your dashboard with:
- 🔍 Search functionality
- 📈 Price updates
- 🎯 Buy/Hold/Avoid signals
- 💹 Target prices and stop losses
- 📊 Confidence scores

## 🛠️ Customization

**Change stocks analyzed:**
Edit `universes/stock_universe.py` and push to GitHub

**Add/remove analysis types:**
Edit `.github/workflows/daily_analysis.yml` workflow file

**Change dashboard appearance:**
Edit `dashboard.py` and push to GitHub (Streamlit auto-redeploys)

## 📞 Need Help?

- Check [DEPLOYMENT_GUIDE.md](DEPLOYMENT_GUIDE.md) for detailed instructions
- View [README.md](README.md) for project overview
- Open an issue on GitHub if you encounter problems

---

**Made with ❤️ for automated stock analysis**

Start analyzing smarter, not harder! 📈
