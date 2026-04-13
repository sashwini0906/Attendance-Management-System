<<<<<<< HEAD
# Railway Deployment Steps

## Step 1: Push Code to GitHub

Open Command Prompt or Git Bash in your project folder and run:

```
bash
git init
git add .
git commit -m "Railway deployment ready"
git branch -M main
git remote set-url origin https://github.com/Deepthi-Nadar/Attendance-Management.git
git push -u origin main
```

**Note:** If you get "remote origin already exists" error, use `git remote set-url` instead of `git remote add`.

## Step 2: Deploy to Railway

1. Go to [railway.app](https://railway.app) and login with GitHub
2. Click **"New Project"**
3. Select **"Deploy from GitHub repo"**
4. Choose **"Deepthi-Nadar/Attendance-Management"**

## Step 3: Add MySQL Database

1. In your Railway project, click **"+ New"** (top right)
2. Search for **"MySQL"** 
3. Click **"MySQL"** to add it

4. Wait for MySQL to start (green status)

## Step 4: Add Environment Variable

1. Go to **"Variables"** tab
2. Click **"+ Add Variable"**
3. Add: `SECRET_KEY` = `attendance-system-secret-2024`

## Step 5: Deploy

1. Click **"Deploy"** button
2. Wait for build to complete (may take 2-3 minutes)
3. Click the generated URL to view your app!

## Step 6: Set Up Database Tables

After deployment, you need to create the database tables:

### Option A: Using Railway Shell
1. In Railway, go to your deployed service
2. Click **"Shell"** tab
3. Run: `python init_db.py`

### Option B: Using MySQL Console
1. Go to Railway MySQL → **"Connect"**
2. Copy the connection string
3. Run the SQL commands from `as.sql` file

## Login Credentials

After setup, use these credentials:
- **Admin:** Username: `admin`, Password: `admin123`
- **Teacher:** Add teachers via Admin Dashboard
=======
# Railway Deployment Steps

## Step 1: Push Code to GitHub

Open Command Prompt or Git Bash in your project folder and run:

```
bash
git init
git add .
git commit -m "Railway deployment ready"
git branch -M main
git remote set-url origin https://github.com/Deepthi-Nadar/Attendance-Management.git
git push -u origin main
```

**Note:** If you get "remote origin already exists" error, use `git remote set-url` instead of `git remote add`.

## Step 2: Deploy to Railway

1. Go to [railway.app](https://railway.app) and login with GitHub
2. Click **"New Project"**
3. Select **"Deploy from GitHub repo"**
4. Choose **"Deepthi-Nadar/Attendance-Management"**

## Step 3: Add MySQL Database

1. In your Railway project, click **"+ New"** (top right)
2. Search for **"MySQL"** 
3. Click **"MySQL"** to add it

4. Wait for MySQL to start (green status)

## Step 4: Add Environment Variable

1. Go to **"Variables"** tab
2. Click **"+ Add Variable"**
3. Add: `SECRET_KEY` = `attendance-system-secret-2024`

## Step 5: Deploy

1. Click **"Deploy"** button
2. Wait for build to complete (may take 2-3 minutes)
3. Click the generated URL to view your app!

## Step 6: Set Up Database Tables

After deployment, you need to create the database tables:

### Option A: Using Railway Shell
1. In Railway, go to your deployed service
2. Click **"Shell"** tab
3. Run: `python init_db.py`

### Option B: Using MySQL Console
1. Go to Railway MySQL → **"Connect"**
2. Copy the connection string
3. Run the SQL commands from `as.sql` file

## Login Credentials

After setup, use these credentials:
- **Admin:** Username: `admin`, Password: `admin123`
- **Teacher:** Add teachers via Admin Dashboard
>>>>>>> a741fce4340050b093253c89486b1f4e20183baf
