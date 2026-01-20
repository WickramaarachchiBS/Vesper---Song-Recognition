# Quick Deployment Commands

## For Render.com (Recommended - FREE)

### 1. Push to GitHub
```bash
git init
git add .
git commit -m "Ready for deployment"
git remote add origin https://github.com/YOUR_USERNAME/vesper-song-recognition.git
git push -u origin main
```

### 2. On Render.com Dashboard
1. Go to https://render.com
2. Sign up with GitHub
3. Click "New +" → "Web Service"
4. Connect your repository
5. Settings:
   - **Build Command**: `pip install -r requirements.txt`
   - **Start Command**: `uvicorn app.main:app --host 0.0.0.0 --port $PORT`
6. Click "New +" → "PostgreSQL" (free tier)
7. Add environment variables from database URL
8. Deploy!

### 3. Your API URL
```
https://your-app-name.onrender.com/api/identify
```

---

## For Railway.app (Also FREE with $5 credit)

### 1. Push to GitHub (same as above)

### 2. On Railway Dashboard
1. Go to https://railway.app
2. Sign up with GitHub
3. Click "New Project" → "Deploy from GitHub"
4. Select your repository
5. Add PostgreSQL database (one click)
6. Environment variables auto-configured!
7. Deploy automatically

### 3. Your API URL
```
https://your-app-name.up.railway.app/api/identify
```

---

## Environment Variables Needed

```env
DB_HOST=<your-database-host>
DB_PORT=5432
DB_NAME=<your-database-name>
DB_USER=<your-database-user>
DB_PASSWORD=<your-database-password>
```

Or single variable:
```env
DATABASE_URL=postgresql://user:password@host:port/database
```

---

## After Deployment

### Initialize Database
```bash
# Connect to your database and run:
psql <DATABASE_URL> -f sql/schema.sql
```

### Populate Songs
Use cloud storage option or connect locally to remote database.

---

## Test Your Deployed API

```bash
# Health check
curl https://your-app-name.onrender.com/

# Test recognition
curl -X POST "https://your-app-name.onrender.com/api/identify" \
  -F "audio_file=@test.mp3"
```

---

## Update Mobile App

Change API endpoint to your deployed URL:
```javascript
const API_URL = 'https://your-app-name.onrender.com/api/identify';
```

---

## Free Tier Limits

**Render.com:**
- 750 hours/month (enough for 24/7)
- Sleeps after 15 min inactivity
- Wakes up in ~30 seconds

**Railway.app:**
- $5 credit/month
- No sleep
- ~500 hours of uptime

**Both are perfect for student FYP projects!**
