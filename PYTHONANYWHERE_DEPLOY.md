<<<<<<< HEAD
# Deploy on PythonAnywhere - Simple Steps

## Step 1: Upload Files
1. Go to https://www.pythonanywhere.com/
2. Create account and login
3. Go to "Files" tab
4. Upload all your files to `/home/yourusername/attendance-system/`

## Step 2: Create Database
1. Go to "Databases" tab
2. Under "MySQL", fill:
   - Database name: `attendance_db`
   - Username & Password
3. Click "Create"

## Step 3: Setup Web App
1. Go to "Web" tab
2. Click "Add a new web app"
3. Select "Manual configuration" → "Python 3.11"
4. Click "Next"

## Step 4: Configure WSGI File
1. Click on the WSGI file link (under "Code")
2. Find the file and edit it
3. Change the path and add your app:

```
python
import sys
path = '/home/yourusername/attendance-system'
if path not in sys.path:
    sys.path.append(path)

from app import app as application
```

Save and close.

## Step 5: Install Requirements
1. Open "Consoles" → "Bash"
2. Run:
```
pip install --user -r /home/yourusername/attendance-system/requirements.txt
```

## Step 6: Set Environment Variables
1. Go to "Web" tab
2. Click on your web app
3. Find "Environment variables" section
4. Add:
   - DB_HOST: `localhost`
   - DB_USER: your mysql username
   - DB_PASSWORD: your mysql password
   - DB_NAME: `attendance_db`
   - SECRET_KEY: any random text

## Step 7: Initialize Database
1. Open "Consoles" → "Bash"
2. Run:
```
cd /home/yourusername/attendance-system
python init_db.py
```

## Step 8: Reload App
1. Go to "Web" tab
2. Click "Reload" button

## Step 9: Open Your App
- Click the URL shown (like `https://yourusername.pythonanywhere.com`)
- Login with: username `admin`, password `admin123`

That's it!
=======
# Deploy on PythonAnywhere - Simple Steps

## Step 1: Upload Files
1. Go to https://www.pythonanywhere.com/
2. Create account and login
3. Go to "Files" tab
4. Upload all your files to `/home/yourusername/attendance-system/`

## Step 2: Create Database
1. Go to "Databases" tab
2. Under "MySQL", fill:
   - Database name: `attendance_db`
   - Username & Password
3. Click "Create"

## Step 3: Setup Web App
1. Go to "Web" tab
2. Click "Add a new web app"
3. Select "Manual configuration" → "Python 3.11"
4. Click "Next"

## Step 4: Configure WSGI File
1. Click on the WSGI file link (under "Code")
2. Find the file and edit it
3. Change the path and add your app:

```
python
import sys
path = '/home/yourusername/attendance-system'
if path not in sys.path:
    sys.path.append(path)

from app import app as application
```

Save and close.

## Step 5: Install Requirements
1. Open "Consoles" → "Bash"
2. Run:
```
pip install --user -r /home/yourusername/attendance-system/requirements.txt
```

## Step 6: Set Environment Variables
1. Go to "Web" tab
2. Click on your web app
3. Find "Environment variables" section
4. Add:
   - DB_HOST: `localhost`
   - DB_USER: your mysql username
   - DB_PASSWORD: your mysql password
   - DB_NAME: `attendance_db`
   - SECRET_KEY: any random text

## Step 7: Initialize Database
1. Open "Consoles" → "Bash"
2. Run:
```
cd /home/yourusername/attendance-system
python init_db.py
```

## Step 8: Reload App
1. Go to "Web" tab
2. Click "Reload" button

## Step 9: Open Your App
- Click the URL shown (like `https://yourusername.pythonanywhere.com`)
- Login with: username `admin`, password `admin123`

That's it!
>>>>>>> a741fce4340050b093253c89486b1f4e20183baf
