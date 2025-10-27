# Railway PostgreSQL Setup - REQUIRED FOR DATA PERSISTENCE

## ⚠️ Current Status
Your application is currently using SQLite, which **WILL LOSE ALL DATA** on every Railway deployment.

## ✅ Quick Setup (5 minutes)

### Step 1: Add PostgreSQL Database to Railway

1. Go to [Railway Dashboard](https://railway.app/dashboard)
2. Click on your **fineprint_simplifier** project
3. Click **"+ New"** button (top right)
4. Select **"Database"**
5. Select **"Add PostgreSQL"**

Railway will automatically:
- Create a new PostgreSQL service
- Set the `DATABASE_URL` environment variable
- Connect it to your application

### Step 2: Verify the Setup

1. In your Railway project, go to the **"Variables"** tab
2. Look for a variable named `DATABASE_URL`
3. It should look like: `postgresql://postgres:password@hostname:port/database`

### Step 3: Redeploy

1. Railway will automatically detect the new `DATABASE_URL` variable
2. Your next deployment will use PostgreSQL instead of SQLite
3. Check the deployment logs for: `✅ Using PostgreSQL - data will persist across deployments`

## 🎯 What This Fixes

After adding PostgreSQL:
- ✅ User accounts will persist across deployments
- ✅ Usage tracking will persist across deployments
- ✅ No more data loss on deployment
- ✅ Your account won't disappear after updates

## 🔍 Verify It's Working

After deployment, check the logs for:
```
✅ Database connection successful: postgresql://...
✅ Using PostgreSQL - data will persist across deployments
```

If you see:
```
⚠️ Using SQLite - data will NOT persist on Railway deployments
```
Then the `DATABASE_URL` variable is not set correctly.

## 💰 Cost

Railway's PostgreSQL database is included in their free tier with:
- 512 MB storage
- More than enough for user accounts and usage tracking
- No credit card required for free tier

## 📝 Troubleshooting

### Database URL Not Appearing
1. Make sure you added PostgreSQL as a **Service** to your project
2. Check the **Variables** tab - `DATABASE_URL` should be automatically set
3. If missing, click on the PostgreSQL service → Connect tab → Copy the connection string
4. Manually add it as an environment variable in your main service

### Still Using SQLite
1. Check that `DATABASE_URL` starts with `postgresql://` not `sqlite://`
2. Redeploy your application after setting the variable
3. Check deployment logs to confirm PostgreSQL is being used

### Need Help?
If you're still seeing the SQLite warning after following these steps, the `DATABASE_URL` environment variable may not be set correctly. Check the Railway dashboard Variables tab.
