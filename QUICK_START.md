# Quick Start Guide - Deploy Fineprint Simplifier

## 🚀 Deploy to Production in 5 Minutes

### Option 1: Heroku (Recommended for Beginners)

1. **Install Heroku CLI**
   ```bash
   # Windows (with Chocolatey)
   choco install heroku-cli
   
   # macOS
   brew install heroku/brew/heroku
   
   # Linux
   curl https://cli-assets.heroku.com/install.sh | sh
   ```

2. **Login to Heroku**
   ```bash
   heroku login
   ```

3. **Create Heroku App**
   ```bash
   heroku create your-app-name
   ```

4. **Deploy**
   ```bash
   git add .
   git commit -m "Initial deployment"
   git push heroku main
   ```

5. **Set Environment Variables**
   ```bash
   heroku config:set ADMIN_USERNAME=your-admin-username
   heroku config:set ADMIN_PASSWORD=your-secure-password
   ```

6. **Open Your App**
   ```bash
   heroku open
   ```

### Option 2: DigitalOcean App Platform

1. **Push to GitHub**
   ```bash
   git init
   git add .
   git commit -m "Initial commit"
   git remote add origin https://github.com/yourusername/fineprint-simplifier.git
   git push -u origin main
   ```

2. **Deploy on DigitalOcean**
   - Go to [DigitalOcean App Platform](https://cloud.digitalocean.com/apps)
   - Click "Create App"
   - Connect your GitHub repository
   - Set build command: `pip install -r requirements.txt`
   - Set run command: `uvicorn main:app --host 0.0.0.0 --port $PORT`
   - Deploy!

### Option 3: Local Development with Docker

1. **Build and Run**
   ```bash
   docker-compose up --build
   ```

2. **Access at** `http://localhost:8000`

## 🔄 Development Workflow

### 1. Set Up Git Repository
```bash
git init
git add .
git commit -m "Initial commit"
git remote add origin https://github.com/yourusername/fineprint-simplifier.git
git push -u origin main
```

### 2. Create Development Branch
```bash
git checkout -b develop
git push -u origin develop
```

### 3. Development Process
```bash
# Create feature branch
git checkout -b feature/new-feature

# Make changes and test locally
uvicorn main:app --reload

# Commit changes
git add .
git commit -m "Add new feature"
git push origin feature/new-feature

# Merge to develop
git checkout develop
git merge feature/new-feature
git push origin develop

# Deploy to staging (if you have staging environment)
# Test on staging

# Merge to main for production
git checkout main
git merge develop
git push origin main
```

## 📋 Pre-Deployment Checklist

- [ ] All files committed to git
- [ ] `requirements.txt` is up to date
- [ ] Environment variables configured
- [ ] Admin credentials set
- [ ] Health check endpoint working (`/health`)
- [ ] Uploads directory exists
- [ ] No sensitive data in code (use environment variables)

## 🔧 Environment Variables

Set these in your deployment platform:

```bash
# Required
ADMIN_USERNAME=your-admin-username
ADMIN_PASSWORD=your-secure-password

# Optional
ENVIRONMENT=production
DEBUG=false
```

## 🚨 Common Issues

### "Build failed" on Heroku
- Check `requirements.txt` is up to date
- Ensure `Procfile` exists and is correct
- Check `runtime.txt` specifies correct Python version

### "Module not found" errors
- Make sure all dependencies are in `requirements.txt`
- Check for typos in import statements

### Admin area not accessible
- Verify environment variables are set correctly
- Check admin credentials in deployment platform

## 📞 Support

If you encounter issues:
1. Check the logs: `heroku logs --tail`
2. Verify health endpoint: `curl https://your-app.herokuapp.com/health`
3. Test locally first: `uvicorn main:app --reload`

## 🎯 Next Steps After Deployment

1. **Set up monitoring** (Heroku has built-in monitoring)
2. **Configure custom domain** (optional)
3. **Set up SSL certificate** (automatic on Heroku)
4. **Add logging** for better debugging
5. **Plan database migration** for future scalability
