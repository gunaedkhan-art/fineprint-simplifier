#!/bin/bash

# Deployment script for Fineprint Simplifier
# Usage: ./deploy.sh [environment]

set -e  # Exit on any error

ENVIRONMENT=${1:-production}
APP_NAME="fineprint-simplifier"

echo "🚀 Deploying Fineprint Simplifier to $ENVIRONMENT..."

# Check if we're in a git repository
if [ ! -d ".git" ]; then
    echo "❌ Error: Not in a git repository. Please initialize git first."
    exit 1
fi

# Check if we have uncommitted changes
if [ -n "$(git status --porcelain)" ]; then
    echo "⚠️  Warning: You have uncommitted changes. Consider committing them first."
    read -p "Continue anyway? (y/N): " -n 1 -r
    echo
    if [[ ! $REPLY =~ ^[Yy]$ ]]; then
        exit 1
    fi
fi

# Create uploads directory if it doesn't exist
mkdir -p uploads

# Install dependencies
echo "📦 Installing dependencies..."
pip install -r requirements.txt

# Run tests (if you add them later)
# echo "🧪 Running tests..."
# python -m pytest

# Commit changes if any
if [ -n "$(git status --porcelain)" ]; then
    echo "💾 Committing changes..."
    git add .
    git commit -m "Deploy to $ENVIRONMENT - $(date)"
fi

# Deploy based on environment
case $ENVIRONMENT in
    "production")
        echo "🌐 Deploying to production..."
        
        # Check if Heroku CLI is installed
        if ! command -v heroku &> /dev/null; then
            echo "❌ Heroku CLI not found. Please install it first."
            exit 1
        fi
        
        # Deploy to Heroku
        git push heroku main
        
        echo "✅ Deployed to production!"
        echo "🌍 Your app is live at: https://$APP_NAME.herokuapp.com"
        ;;
        
    "staging")
        echo "🧪 Deploying to staging..."
        
        # Deploy to staging (you can customize this)
        git push origin staging
        
        echo "✅ Deployed to staging!"
        ;;
        
    "local")
        echo "🏠 Starting local development server..."
        uvicorn main:app --reload --host 0.0.0.0 --port 8000
        ;;
        
    *)
        echo "❌ Unknown environment: $ENVIRONMENT"
        echo "Usage: ./deploy.sh [production|staging|local]"
        exit 1
        ;;
esac

echo "🎉 Deployment complete!"
