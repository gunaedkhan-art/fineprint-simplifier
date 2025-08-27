# Railway Deployment Guide

## Quick Deploy to Railway

### Step 1: Connect to Railway
1. Go to [Railway.app](https://railway.app)
2. Sign up with GitHub
3. Click "New Project"
4. Select "Deploy from GitHub repo"
5. Choose your repository: `gunaedkhan-art/fineprint-simplifier`

### Step 2: Configure Environment Variables
In your Railway project dashboard, go to "Variables" and add:

```
ADMIN_USERNAME=admin
ADMIN_PASSWORD=your-secure-password-here
ENVIRONMENT=production
DEBUG=false
```

### Step 3: Deploy
Railway will automatically:
- Detect it's a Python app
- Install dependencies from `requirements.txt`
- Start the app using the `Procfile`

## Troubleshooting

### If deployment fails:

1. **Check the logs** in Railway dashboard
2. **Verify requirements.txt** has all dependencies
3. **Check Procfile** format is correct
4. **Ensure all files are committed** to GitHub

### Common Issues:

**Port Error:**
- The `$PORT` environment variable should be automatically set by Railway
- If you see port errors, check that the Procfile uses `$PORT` (not a hardcoded port)

**Import Errors:**
- Make sure all Python files are in the root directory
- Check that all imports are correct

**Admin Access:**
- Use the credentials you set in environment variables
- Default: username=`admin`, password=your-secure-password

## Testing Your Deployment

1. **Health Check:** Visit `https://your-app.railway.app/health`
2. **Main App:** Visit `https://your-app.railway.app/`
3. **Admin Area:** Visit `https://your-app.railway.app/admin`

## Environment Variables Reference

| Variable | Description | Default |
|----------|-------------|---------|
| `ADMIN_USERNAME` | Admin login username | `admin` |
| `ADMIN_PASSWORD` | Admin login password | `admin123` |
| `ENVIRONMENT` | App environment | `production` |
| `DEBUG` | Debug mode | `false` |

## Support

If you continue to have issues:
1. Check Railway's [documentation](https://docs.railway.app/)
2. Review the deployment logs in Railway dashboard
3. Ensure your local app runs without errors first
