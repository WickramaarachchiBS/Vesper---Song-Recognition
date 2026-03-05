# Azure Deployment Guide (Student Edition)

This guide provides a comprehensive step-by-step process to deploy the **Vesper Song Recognition** backend to **Microsoft Azure** using the **Azure for Students** subscription.

---

## 📋 Step-by-Step Deployment Guide

---

### Step 1: Create Azure Resources

#### 1.1 Create a Resource Group
1. Go to [Azure Portal](https://portal.azure.com).
2. Search for **"Resource groups"** → Click **Create**.
3. **Subscription**: Azure for Students.
4. **Resource group name**: `vesper-rg`.
5. **Region**: Choose the region closest to you (e.g., `Southeast Asia`, `East US`).
6. Click **Review + Create** → **Create**.

#### 1.2 Create PostgreSQL Flexible Server
1. Search for **"Azure Database for PostgreSQL"** → Select **Flexible Server**.
2. Click **Create**.
3. **Basics**:
   - **Resource Group**: `vesper-rg`.
   - **Server name**: `vesper-db-server` (must be unique).
   - **Workload type**: `Development`.
   - **Compute + storage**: Select **Burstable B1ms** (1 vCore, 2GB RAM).
   - **Storage**: 32 GB.
4. **Authentication**:
   - **Method**: PostgreSQL authentication only.
   - **Admin username**: `vesperadmin`.
   - **Password**: Create a strong password (save this safely!).
5. **Networking**:
   - ✅ Check **"Allow public access from any Azure service"**.
   - Click **"+ Add current client IP address"**.
6. Click **Review + Create** → **Create**.

> **Note**: Deployment takes 5-10 minutes.

---

### Step 2: Initialize the Database

Once the database is created, connect to it from your local machine to set up the schema.

#### 2.1 Get Connection Details
- **Host**: `vesper-db-server.postgres.database.azure.com`
- **Username**: `vesperadmin`
- **Password**: Your chosen password
- **Database**: `postgres` (default)

#### 2.2 Run Schema Script
Run the following commands in your local terminal (PowerShell):

```powershell
# 1. Connect to Azure PostgreSQL
psql "host=vesper-pgdb-server.postgres.database.azure.com port=5432 dbname=vesper user=vesperadmin password=AzurePG@2002 sslmode=require"

psql "host=vesper-db-server.postgres.database.azure.com port=5432 dbname=postgres user=vesperadmin password=YOUR_PASSWORD sslmode=require"

# 2. Create the 'vesper' database
postgres=> CREATE DATABASE vesper;
postgres=> \q

# 3. Run the schema file
psql "host=vesper-db-server.postgres.database.azure.com port=5432 dbname=vesper user=vesperadmin password=YOUR_PASSWORD sslmode=require" -f sql/schema.sql
```

---

### Step 3: Create Azure App Service

1. Search for **"App Service"** → Click **Create** → **Web App**.
2. **Basics**:
   - **Resource Group**: `vesper-rg`.
   - **Name**: `vesper-song-recognition` (unique URL).
   - **Publish**: Code.
   - **Runtime stack**: `Python 3.11`.
   - **Operating System**: Linux.
   - **Region**: Same as database.
3. **Pricing Plan**:
   - Select **Basic B1** (Recommended for stability using credits).
   - Or **Free F1** (For testing, 60 mins CPU/day).
4. Click **Review + Create** → **Create**.

---

### Step 4: Configure App Service

#### 4.1 Set Environment Variables
1. Go to App Service → **Configuration** → **Application settings** → **+ New application setting**.
2. Add the following key-value pairs:

| Name | Value |
|------|-------|
| `DB_HOST` | `vesper-db-server.postgres.database.azure.com` |
| `DB_PORT` | `5432` |
| `DB_NAME` | `vesper` |
| `DB_USER` | `vesperadmin` |
| `DB_PASSWORD` | `your-password` |
| `SCM_DO_BUILD_DURING_DEPLOYMENT` | `true` |

3. Click **Save**.

#### 4.2 Configure Startup Command
1. Go to **Configuration** → **General settings**.
2. **Startup Command**:
   ```bash
   gunicorn -w 4 -k uvicorn.workers.UvicornWorker app.main:app --bind 0.0.0.0:8000
   ```
3. Click **Save**.

---

### Step 5: Deploy Code

#### Option A: Azure CLI (Recommended)
Run in your project folder:

```powershell
az login
az webapp up --name vesper-song-recognition --resource-group vesper-rg --runtime "PYTHON:3.11"
```

#### Option B: GitHub Actions (Continuous Deployment)
1. App Service → **Deployment Center**.
2. Source: **GitHub**.
3. Authorization: Connect your account.
4. Repository: Select `vesper-song-recognition`.
5. Branch: `main`.
6. Click **Save**. Azure will automatically build and deploy on every push.

---

### Step 6: Populate Database

Populate your cloud database with songs from your local machine:

```powershell
# Set temporary env vars for the script
$env:DB_HOST = "vesper-db-server.postgres.database.azure.com"
$env:DB_PORT = "5432"
$env:DB_NAME = "vesper"
$env:DB_USER = "vesperadmin"
$env:DB_PASSWORD = "your-password"

# Run populate script
python -m app.services.populate_db
```

---

## 🌐 API Details for Mobile App

Update your mobile application's base URL:

```javascript
// Production Azure URL
const API_URL = "https://vesper-song-recognition.azurewebsites.net/api/identify";
```

**Available Endpoints:**
- `GET /docs` - Swagger UI Documentation
- `GET /health` - Health Check
- `GET /api/songs` - List all songs
- `POST /api/identify` - Identify song

---

## 💰 Cost Management (Azure for Students)

Your **$100 credit** lasts for 12 months.

| Resource | Service Tier | Est. Cost |
|----------|-------------|-----------|
| **App Service** | Linux Basic B1 | ~$13/mo |
| **Database** | Flexible Server (B1ms) | ~$13/mo |
| **Storage** | 32 GB | ~$2/mo |
| **Total** | | **~$28/mo** |

> **Tip**: To save credits, stop the **App Service** when not in use. You can also stop the **PostgreSQL Server** (it can be stopped for up to 7 days).

---

## 🔧 Troubleshooting

### Application Error :(
- Go to App Service → **Log stream**.
- Check if `requirements.txt` is present and correct.
- Verify environment variables properly match database credentials.

### Database Connection Failed
- Ensure "Allow public access from any Azure service" is checked in Database Networking.
- Check firewall rules if connecting from local PC.

### 504 Gateway Timeout
- Increase Gunicorn timeout or worker count if processing large files.
- Ensure the server isn't running out of memory (check App Service **Metrics**).

---

## 📚 Helpful Links

- [Azure Portal](https://portal.azure.com)
- [Azure for Students](https://azure.microsoft.com/free/students)
- [FastAPI Deployment Docs](https://fastapi.tiangolo.com/deployment/server-workers/)
