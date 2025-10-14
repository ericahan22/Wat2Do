# Authentication Guide

## How to Authenticate and Use Submission Features

The Wat2Do app now supports user authentication for submitting events and clubs. Here's how to get started:

### 1. Create an Account

You can create an account in two ways:

#### Option A: Through the UI (Recommended)
1. Click the "Login" button in the top navigation
2. Switch to the "Register" tab
3. Fill in your username, email (optional), and password
4. Click "Create Account"

#### Option B: Using the API directly
```bash
curl -X POST http://localhost:8000/api/auth/register/ \
  -H "Content-Type: application/json" \
  -d '{
    "username": "your_username",
    "password": "your_password",
    "email": "your@email.com"
  }'
```

### 2. Login

#### Option A: Through the UI
1. Click the "Login" button in the top navigation
2. Enter your username and password
3. Click "Login"

#### Option B: Using the API directly
```bash
curl -X POST http://localhost:8000/api/auth/token/ \
  -H "Content-Type: application/json" \
  -d '{
    "username": "your_username",
    "password": "your_password"
  }'
```

### 3. Test Credentials

For testing purposes, you can use these credentials:

**Regular User:**
- Username: `testuser`
- Password: `testpass123`

**Admin User:**
- Username: `admin` (if you created one)
- Password: `admin` (or whatever you set)

### 4. Using Submission Features

Once authenticated, you'll see new options in the navigation:

- **Submit**: Submit new events or clubs
- **My Submissions**: View the status of your submissions
- **Admin**: (Admin only) Moderate pending submissions

### 5. API Authentication

When making API calls, include your token in the Authorization header:

```bash
curl -X GET http://localhost:8000/api/events/submissions/ \
  -H "Authorization: Token YOUR_TOKEN_HERE"
```

### 6. Admin Features

To access admin features (moderation), you need admin privileges. You can:

1. Create an admin user through Django admin: `http://localhost:8000/admin/`
2. Or use the Django shell:
```bash
cd backend
python manage.py shell
>>> from django.contrib.auth.models import User
>>> user = User.objects.get(username='your_username')
>>> user.is_staff = True
>>> user.is_superuser = True
>>> user.save()
```

### 7. Logout

Click the logout button (X icon) next to your username in the navigation bar.

## Features Available After Authentication

### For Regular Users:
- Submit events with image uploads
- Submit new clubs
- View submission status
- Track approval/rejection status

### For Admin Users:
- All regular user features
- Moderate pending submissions
- Approve or reject events/clubs
- Provide rejection feedback

## Troubleshooting

### "Authentication required" error
- Make sure you're logged in
- Check that your token is valid
- Try logging out and back in

### "Access denied" error
- You need admin privileges for moderation features
- Contact an admin to grant you admin access

### API calls failing
- Ensure you're including the Authorization header
- Check that your token is correct
- Verify the API endpoint URL

## Development Notes

- Tokens are stored in localStorage in the browser
- Tokens don't expire automatically (you can implement expiration if needed)
- Admin status is determined by Django's `is_staff` and `is_superuser` flags
- All submission endpoints require authentication
- Moderation endpoints require admin privileges
