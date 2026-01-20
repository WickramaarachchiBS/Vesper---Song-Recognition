# Quick Start Guide - Vesper Song Recognition

## ✅ What You Already Have
- PostgreSQL database: `VesperSongData`
- Tables: `songs` and `fingerprints`

## 🎯 Simple 3-Step Process

### Step 1: Configure Database Connection (2 minutes)

1. Open `.env.example` and save it as `.env`
2. Edit the `.env` file with your database name:

```env
DB_HOST=localhost
DB_PORT=5432
DB_NAME=VesperSongData
DB_USER=postgres
DB_PASSWORD=your_password_here
```

**Important**: Replace `your_password_here` with your actual PostgreSQL password.

---

### Step 2: Add Sample Songs to Database (5 minutes)

You have **TWO OPTIONS**:

#### Option A: Use Cloud Storage (RECOMMENDED for production)
If your MP3s are in cloud storage, you can:
1. Download a few sample songs (3-5 songs) to the `dataset/` folder for testing
2. Later, modify `populate_db.py` to fetch from cloud storage

#### Option B: Use Local Dataset Folder (EASIEST for testing)
1. Copy 3-5 MP3 songs to the `dataset/` folder
2. Run the population script (see below)

**For now, let's use Option B (easier to test):**

```bash
# 1. Copy some MP3 files to dataset folder
# Just drag and drop 3-5 MP3 files into: Vesper - Song Recognition\dataset\

# 2. Install dependencies (one-time only)
pip install -r requirements.txt

# 3. Populate database with songs
python -m app.services.populate_db
```

This will:
- Read all MP3/WAV files from `dataset/`
- Generate fingerprints for each song
- Store them in your `VesperSongData` database

---

### Step 3: Start the API Server

```bash
# Start the server
uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
```
`
The server will run at: `http://localhost:8000`

---

## 📱 Testing from Mobile App

Once the server is running, your mobile app can send songs to recognize:

### API Endpoint
```
POST http://your-server-ip:8000/api/identify
```

### Request Format
- **Method**: POST
- **Content-Type**: multipart/form-data
- **Field name**: `audio_file`
- **File**: MP3 or WAV audio file

### Example Response (Success)
```json
{
  "success": true,
  "song_id": 1,
  "title": "Song Name",
  "artist": "Artist Name",
  "match_count": 127,
  "confidence": 85.32
}
```

### Example Response (Not Found)
```json
{
  "success": false,
  "message": "No matching song found in database"
}
```

---

## 🧪 Quick Test

### Test 1: Check if server is running
Open browser: `http://localhost:8000`

You should see:
```json
{
  "message": "Audio Fingerprinting API",
  "version": "1.0.0"
}
```

### Test 2: Test with a sample file
```bash
# Using curl (if you have it)
curl -X POST "http://localhost:8000/api/identify" -F "audio_file=@path/to/test.mp3"

# Or visit the interactive docs
# Open browser: http://localhost:8000/docs
# Click on POST /api/identify
# Click "Try it out"
# Upload a file and click "Execute"
```

---

## 🔧 Troubleshooting

### Problem: "Database connection failed"
**Solution**: 
1. Make sure PostgreSQL is running
2. Check your `.env` file has correct password
3. Test connection: `psql -U postgres -d VesperSongData`

### Problem: "No songs in database"
**Solution**: 
1. Make sure you have MP3 files in `dataset/` folder
2. Run: `python -m app.services.populate_db`
3. Check: `psql -U postgres -d VesperSongData -c "SELECT COUNT(*) FROM songs;"`

### Problem: "Module not found"
**Solution**: 
```bash
pip install -r requirements.txt
```

---

## 📋 Complete Workflow

```
1. Setup (One-time)
   ├── Edit .env file with database credentials
   ├── Install dependencies: pip install -r requirements.txt
   └── Verify database exists: VesperSongData

2. Add Songs (Whenever you want to add new songs)
   ├── Put MP3 files in dataset/ folder
   └── Run: python -m app.services.populate_db

3. Run Server (Every time you want to use the API)
   └── Run: uvicorn app.main:app --reload --host 0.0.0.0 --port 8000

4. Use from Mobile App
   └── POST audio file to: http://your-ip:8000/api/identify
```

---

## 🌐 For Production (Deploy on Server)

When you're ready to deploy:

1. **Install on server** (same steps as above)
2. **Update mobile app** to use server IP instead of localhost
3. **Use cloud storage**: Modify `populate_db.py` to download from cloud
4. **Run with production server**:
   ```bash
   uvicorn app.main:app --host 0.0.0.0 --port 8000
   ```

---

## 💡 Tips

- **Start small**: Test with 3-5 songs first
- **Use short clips**: For testing, 10-15 second clips work well
- **Check logs**: The terminal will show what's happening
- **Database size**: Each 3-minute song = ~100,000 fingerprints (~15 MB)

---

## ❓ Need Help?

Run the test script to verify everything:
```bash
python test_system.py
```

This will check:
- ✓ Database connection
- ✓ Audio files in dataset
- ✓ Fingerprinting works
- ✓ Database statistics
