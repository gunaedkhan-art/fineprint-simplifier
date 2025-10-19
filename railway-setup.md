# Railway PostgreSQL Setup Guide

## Step 1: Add PostgreSQL to Your Railway Project

1. Go to your Railway dashboard: https://railway.app/dashboard
2. Click on your `fineprint_simplifier` project
3. Click "New" → "Database" → "PostgreSQL"
4. Railway will automatically provision a PostgreSQL database

## Step 2: Get Database Connection String

1. Click on your newly created PostgreSQL service
2. Go to the "Connect" tab
3. Copy the "DATABASE_URL" connection string
4. It will look like: `postgresql://postgres:password@hostname:port/database`

## Step 3: Set Environment Variable

1. In your Railway project, go to "Variables" tab
2. Add a new variable:
   - **Name**: `DATABASE_URL`
   - **Value**: Paste the connection string from Step 2

## Step 4: Deploy

The application will automatically:
- Detect the `DATABASE_URL` environment variable
- Create the necessary database tables
- Start using PostgreSQL instead of the JSON file

## Step 5: Verify

After deployment, you can verify the database is working by:
1. Registering a new user account
2. Logging in with that account
3. The data will persist even after Railway restarts the container

## Local Development

For local development, the app will fall back to SQLite:
- Create a local `.env` file
- Add: `DATABASE_URL=sqlite:///./smallprintchecker.db`
- The app will use SQLite locally and PostgreSQL on Railway

## Database Schema

The following tables will be automatically created:
- `users` - Stores user accounts, subscriptions, and usage data

## Migration Notes

- Existing user data in `users.json` will not be automatically migrated
- Users will need to re-register their accounts
- This is a one-time migration cost for the improved persistence
