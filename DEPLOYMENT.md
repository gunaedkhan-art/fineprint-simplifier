# Deployment Guide for Fineprint Simplifier

## Overview

This guide covers how to deploy your application live while maintaining a development workflow that doesn't affect the production version.

## Strategy 1: Git-Based Development Workflow

### Setup Git Repository
```bash
# Initialize git repository
git init
git add .
git commit -m "Initial commit"

# Create GitHub/GitLab repository and push
git remote add origin <your-repo-url>
git push -u origin main
```

### Branch Strategy
```bash
# Main branch (production-ready code)
git checkout main

# Development branch (for new features)
git checkout -b develop
git push -u origin develop

# Feature branches (for specific features)
git checkout -b feature/new-feature
# ... make changes ...
git commit -m "Add new feature"
git push origin feature/new-feature
```

## Strategy 2: Environment-Based Deployment

### Development Environment (Local)
- **Purpose**: Active development and testing
- **URL**: `http://localhost:8000`
- **Database**: Local JSON files
- **Features**: All features enabled, debug mode

### Staging Environment
- **Purpose**: Pre-production testing
- **URL**: `https://staging.yourdomain.com`
- **Database**: Separate staging data
- **Features**: Production-like environment

### Production Environment
- **Purpose**: Live application
- **URL**: `https://yourdomain.com`
- **Database**: Production data
- **Features**: Optimized, monitored

## Strategy 3: Platform-Specific Deployment

### Option A: Heroku (Recommended for Beginners)

#### Setup
1. **Install Heroku CLI**
2. **Create Heroku app**:
   ```bash
   heroku create your-app-name
   ```

3. **Add Procfile**:
   ```
   web: uvicorn main:app --host 0.0.0.0 --port $PORT
   ```

4. **Deploy**:
   ```bash
   git add .
   git commit -m "Deploy to production"
   git push heroku main
   ```

#### Environment Variables
```bash
heroku config:set ENVIRONMENT=production
heroku config:set ADMIN_USERNAME=your-admin-username
heroku config:set ADMIN_PASSWORD=your-secure-password
```

### Option B: DigitalOcean App Platform

1. **Connect GitHub repository**
2. **Configure build settings**:
   - Build command: `pip install -r requirements.txt`
   - Run command: `uvicorn main:app --host 0.0.0.0 --port $PORT`
3. **Set environment variables**
4. **Deploy**

### Option C: AWS/Google Cloud/Azure

#### Docker Setup
```dockerfile
FROM python:3.9-slim

WORKDIR /app

COPY requirements.txt .
RUN pip install -r requirements.txt

COPY . .

EXPOSE 8000

CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "8000"]
```

#### Docker Compose (for local development)
```yaml
version: '3.8'
services:
  web:
    build: .
    ports:
      - "8000:8000"
    volumes:
      - .:/app
    environment:
      - ENVIRONMENT=development
```

## Strategy 4: Database Migration

### Current State: JSON Files
- `users.json` - User data
- `custom_patterns.json` - Approved patterns
- `pending_patterns.json` - Pending patterns

### Future: Database Migration
Consider migrating to a proper database (PostgreSQL, MySQL) for:
- Better performance
- Data integrity
- Backup capabilities
- Multi-user support

## Strategy 5: CI/CD Pipeline

### GitHub Actions Example
```yaml
name: Deploy to Production

on:
  push:
    branches: [ main ]

jobs:
  deploy:
    runs-on: ubuntu-latest
    steps:
    - uses: actions/checkout@v2
    
    - name: Deploy to Heroku
      uses: akhileshns/heroku-deploy@v3.12.12
      with:
        heroku_api_key: ${{ secrets.HEROKU_API_KEY }}
        heroku_app_name: ${{ secrets.HEROKU_APP_NAME }}
        heroku_email: ${{ secrets.HEROKU_EMAIL }}
```

## Development Workflow

### 1. Local Development
```bash
# Start development server
uvicorn main:app --reload --host 0.0.0.0 --port 8000

# Make changes and test locally
# Commit changes to feature branch
git add .
git commit -m "Feature description"
git push origin feature-branch
```

### 2. Staging Testing
```bash
# Merge feature to develop branch
git checkout develop
git merge feature-branch
git push origin develop

# Deploy to staging (automatic via CI/CD)
# Test on staging environment
```

### 3. Production Deployment
```bash
# Merge develop to main
git checkout main
git merge develop
git push origin main

# Deploy to production (automatic via CI/CD)
```

## Environment Configuration

### Environment Variables
Create `.env` files for different environments:

#### Development (.env.local)
```
ENVIRONMENT=development
DEBUG=true
ADMIN_USERNAME=admin
ADMIN_PASSWORD=dev-password
```

#### Production (.env.production)
```
ENVIRONMENT=production
DEBUG=false
ADMIN_USERNAME=your-secure-admin
ADMIN_PASSWORD=your-secure-password
DATABASE_URL=your-database-url
```

## Monitoring and Maintenance

### 1. Logging
Add structured logging to track:
- User uploads
- Pattern matches
- Errors
- Performance metrics

### 2. Health Checks
Add health check endpoints:
```python
@app.get("/health")
async def health_check():
    return {"status": "healthy", "timestamp": datetime.now()}
```

### 3. Backup Strategy
- Regular database backups
- Pattern file backups
- User data backups

## Security Considerations

### 1. Environment Variables
- Never commit sensitive data
- Use environment variables for secrets
- Rotate passwords regularly

### 2. HTTPS
- Always use HTTPS in production
- Configure SSL certificates
- Redirect HTTP to HTTPS

### 3. Rate Limiting
- Implement rate limiting for uploads
- Protect against abuse
- Monitor usage patterns

## Recommended Next Steps

1. **Set up Git repository** and push your code
2. **Choose a deployment platform** (Heroku recommended for simplicity)
3. **Create staging environment** for testing
4. **Set up CI/CD pipeline** for automated deployments
5. **Configure monitoring** and logging
6. **Plan database migration** for future scalability

## Quick Start Commands

```bash
# Initialize git and push to remote
git init
git add .
git commit -m "Initial commit"
git remote add origin <your-repo-url>
git push -u origin main

# Create development branch
git checkout -b develop
git push -u origin develop

# Deploy to Heroku
heroku create your-app-name
git push heroku main
```
