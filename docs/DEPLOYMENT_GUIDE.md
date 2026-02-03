# Free Hosting Options for Students - Deployment Guide

## 🎓 Best Free Hosting Platforms for Students

### ⭐ **RECOMMENDED: Render.com** (Easiest)

- **Free Tier**: 750 hours/month (enough for 24/7)
- **PostgreSQL**: Free database included
- **Auto-deploy**: From GitHub
- **Custom domain**: Supported
- **Sleep after inactivity**: Yes (wakes up on request)
- **Perfect for**: Students, FYP projects

### 🐍 **Railway.app** (Great for Python)

- **Free Tier**: $5 credit/month (usually enough)
- **PostgreSQL**: Included
- **Easy setup**: One-click deploy
- **No sleep**: Stays active
- **Perfect for**: Active development

### 🚀 **Fly.io** (Good Performance)

- **Free Tier**: 3 VMs, 3GB storage
- **PostgreSQL**: Free tier available
- **Global CDN**: Fast worldwide
- **Perfect for**: Production apps

### 🔵 **Heroku** (Classic Choice)

- **Free Tier**: Removed (now paid only)
- ❌ **Not recommended** for free hosting anymore

### 🆓 **PythonAnywhere** (Python-specific)

- **Free Tier**: Limited but permanent
- **MySQL**: Free (not PostgreSQL)
- **Good for**: Simple apps
- ⚠️ **Limitation**: Need to use MySQL instead of PostgreSQL

---

## 🏆 RECOMMENDED APPROACH: Render.com

I'll show you step-by-step how to deploy on **Render.com** (completely free for students):

---

## 📋 Step-by-Step: Deploy to Render.com

### Prerequisites

1. GitHub account (free)
2. Render.com account (free) - sign up at https://render.com

---

### Step 1: Prepare Your Code for Deployment

I'll create the necessary configuration files:

#### A. Create `render.yaml` (deployment config)

#### B. Update `requirements.txt` (add production server)

#### C. Create startup script

---

### Step 2: Push Code to GitHub

```bash
# Initialize git (if not already done)
git init

# Add all files
git add .

# Commit
git commit -m "Initial commit - Vesper Song Recognition"

# Create repository on GitHub, then:
git remote add origin https://github.com/YOUR_USERNAME/vesper-song-recognition.git
git branch -M main
git push -u origin main
```

---

### Step 3: Deploy on Render.com

1. **Go to**: https://render.com
2. **Sign up** with GitHub
3. **Click**: "New +" → "Web Service"
4. **Connect** your GitHub repository
5. **Configure**:
   - **Name**: `vesper-song-recognition`
   - **Environment**: `Python 3`
   - **Build Command**: `pip install -r requirements.txt`
   - **Start Command**: `uvicorn app.main:app --host 0.0.0.0 --port $PORT`
   - **Plan**: Free

6. **Add PostgreSQL Database**:
   - Click "New +" → "PostgreSQL"
   - **Name**: `vesper-database`
   - **Plan**: Free
   - Copy the **Internal Database URL**

7. **Add Environment Variables**:
   - Go to your web service → Environment
   - Add these variables:
     ```
     DB_HOST=<from database URL>
     DB_PORT=5432
     DB_NAME=<from database URL>
     DB_USER=<from database URL>
     DB_PASSWORD=<from database URL>
     ```
   - Or use single variable:
     ```
     DATABASE_URL=<full internal database URL>
     ```

8. **Deploy**: Click "Create Web Service"

---

### Step 4: Initialize Database

After deployment:

```bash
# Connect to your Render PostgreSQL
# Use the connection string from Render dashboard

# Run schema
psql <DATABASE_URL> -f sql/schema.sql
```

Or use Render's web shell to run the schema.

---

### Step 5: Upload Songs

**Option 1**: Use cloud storage (recommended)

- Upload MP3s to Google Drive, Dropbox, or AWS S3
- Use `populate_from_cloud.py` script

**Option 2**: Use Render's persistent disk (paid)

- Not available on free tier

**Option 3**: Populate from local, connect to remote DB

- Run `populate_db.py` locally but connect to Render's database

---

## 🌐 Your API Will Be Available At:

```
https://vesper-song-recognition.onrender.com/api/identify
```

Use this URL in your mobile app!

---

## 💰 Cost Comparison

| Platform           | Free Tier       | Database     | Sleep?      | Best For    |
| ------------------ | --------------- | ------------ | ----------- | ----------- |
| **Render**         | 750h/month      | PostgreSQL ✓ | Yes (30min) | Students    |
| **Railway**        | $5 credit/month | PostgreSQL ✓ | No          | Active dev  |
| **Fly.io**         | 3 VMs           | PostgreSQL ✓ | No          | Production  |
| **PythonAnywhere** | Forever         | MySQL only   | No          | Simple apps |

---

## 🎓 Student Benefits (Get More Free Credits!)

### GitHub Student Developer Pack

**Get**: https://education.github.com/pack

**Includes**:

- **DigitalOcean**: $200 credit (1 year)
- **Heroku**: Free credits
- **Azure**: $100 credit
- **AWS**: Free tier + credits
- **MongoDB Atlas**: Free cluster

### Apply with:

- Student email (.edu)
- Student ID card
- Enrollment verification

---

## 🚀 Alternative: DigitalOcean (with Student Pack)

If you get GitHub Student Pack:

1. **Get $200 credit** from DigitalOcean
2. **Create Droplet**: Ubuntu 22.04 ($6/month)
3. **Install**:
   ```bash
   sudo apt update
   sudo apt install python3-pip postgresql nginx
   pip3 install -r requirements.txt
   ```
4. **Setup**: PostgreSQL, Nginx reverse proxy
5. **Run**: With systemd service

This gives you **33 months free** with student credits!

---

## 📱 Update Mobile App

Change API endpoint from:

```javascript
// Local
const API_URL = "http://192.168.1.x:8000/api/identify";
```

To:

```javascript
// Production
const API_URL = "https://vesper-song-recognition.onrender.com/api/identify";
```

---

## ⚡ Important Notes

### Render Free Tier Limitations:

- **Sleeps after 15 min** of inactivity
- **First request** takes ~30 seconds to wake up
- **750 hours/month** = ~24/7 for one month
- **Good for**: FYP demos, testing

### Solutions:

1. **Keep-alive ping**: Ping your API every 10 minutes
2. **Show loading**: "Waking up server..." message
3. **Upgrade**: $7/month for always-on

---

## 🔧 Troubleshooting

### "Application failed to start"

- Check logs in Render dashboard
- Verify `requirements.txt` is complete
- Check start command is correct

### "Database connection failed"

- Verify environment variables
- Check database URL is correct
- Ensure database is in same region

### "Songs not found"

- Database is empty
- Need to populate songs first
- Use cloud storage or local populate

---

## 📊 Recommended Setup for FYP

**For Development/Testing:**

- **Render.com** (free)
- **PostgreSQL** on Render (free)
- **Songs**: 10-20 sample songs

**For Demo/Presentation:**

- **Railway.app** ($5 credit)
- Always-on, no sleep
- Fast response times

**For Production (after graduation):**

- **DigitalOcean** ($6/month)
- Full control
- Scalable

---

## 🎯 Next Steps

1. ✅ Create GitHub account (if needed)
2. ✅ Push code to GitHub
3. ✅ Sign up for Render.com
4. ✅ Deploy web service
5. ✅ Create PostgreSQL database
6. ✅ Set environment variables
7. ✅ Initialize database schema
8. ✅ Populate with songs
9. ✅ Test API endpoint
10. ✅ Update mobile app URL

---

## 📚 Helpful Links

- **Render Docs**: https://render.com/docs
- **Railway Docs**: https://docs.railway.app
- **Fly.io Docs**: https://fly.io/docs
- **GitHub Student Pack**: https://education.github.com/pack
- **FastAPI Deployment**: https://fastapi.tiangolo.com/deployment/

---

## 💡 Pro Tips

1. **Use environment variables** for all secrets
2. **Enable HTTPS** (automatic on Render)
3. **Monitor logs** during development
4. **Set up health check** endpoint
5. **Use GitHub Actions** for auto-deploy
6. **Keep local backup** of database

---

## 🆘 Need Help?

- **Render Community**: https://community.render.com
- **Railway Discord**: https://discord.gg/railway
- **Stack Overflow**: Tag with `render`, `fastapi`, `deployment`
