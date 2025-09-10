# 🔐 Security Setup Guide

This guide explains how to set up secure authentication for the FinePrint Simplifier admin area.

## 🚀 Quick Setup

### 1. Install Dependencies
```bash
pip install -r requirements.txt
```

### 2. Generate Admin Password Hash
```bash
python setup_admin.py
```

### 3. Set Environment Variables
```bash
# Required for production
ADMIN_USERNAME=your_admin_username
ADMIN_PASSWORD_HASH=your_generated_hash
JWT_SECRET_KEY=your_secure_jwt_secret_key
JWT_EXPIRE_MINUTES=60
FORCE_HTTPS=true

# Optional (for development)
ADMIN_PASSWORD=admin123  # Only used if ADMIN_PASSWORD_HASH is not set
```

## 🔧 Security Features Implemented

### ✅ JWT Token Authentication
- **Secure tokens**: JWT tokens with expiration
- **HttpOnly cookies**: Tokens stored in secure, HttpOnly cookies
- **Token validation**: Automatic token verification on each request
- **Expiration handling**: Automatic logout when tokens expire

### ✅ Password Security
- **Bcrypt hashing**: Passwords hashed with bcrypt
- **Salt generation**: Automatic salt generation for each password
- **No plain text**: Passwords never stored in plain text

### ✅ Rate Limiting
- **Login attempts**: 5 attempts per minute for login
- **General API**: 120 requests per minute
- **Admin endpoints**: 30 requests per minute
- **IP-based tracking**: Rate limiting by IP address

### ✅ Security Headers
- **Content Security Policy**: Prevents XSS attacks
- **X-Frame-Options**: Prevents clickjacking
- **X-Content-Type-Options**: Prevents MIME sniffing
- **Strict-Transport-Security**: Enforces HTTPS
- **Referrer-Policy**: Controls referrer information

### ✅ HTTPS Enforcement
- **Automatic redirect**: HTTP requests redirected to HTTPS
- **Secure cookies**: Cookies only sent over HTTPS
- **HSTS headers**: HTTP Strict Transport Security

## 🛠️ Deployment Configuration

### Heroku
```bash
heroku config:set ADMIN_USERNAME=your_admin_username
heroku config:set ADMIN_PASSWORD_HASH=your_generated_hash
heroku config:set JWT_SECRET_KEY=your_secure_jwt_secret_key
heroku config:set JWT_EXPIRE_MINUTES=60
heroku config:set FORCE_HTTPS=true
```

### Railway
Add these environment variables in your Railway dashboard:
```
ADMIN_USERNAME=your_admin_username
ADMIN_PASSWORD_HASH=your_generated_hash
JWT_SECRET_KEY=your_secure_jwt_secret_key
JWT_EXPIRE_MINUTES=60
FORCE_HTTPS=true
```

### Docker
```dockerfile
ENV ADMIN_USERNAME=your_admin_username
ENV ADMIN_PASSWORD_HASH=your_generated_hash
ENV JWT_SECRET_KEY=your_secure_jwt_secret_key
ENV JWT_EXPIRE_MINUTES=60
ENV FORCE_HTTPS=true
```

## 🔑 Admin Access

### URL
- **Login**: `https://your-domain.com/admin/login`
- **Dashboard**: `https://your-domain.com/admin/dashboard`

### Default Credentials (Development Only)
- **Username**: `admin`
- **Password**: `admin123`

⚠️ **Important**: Change these credentials in production using the setup script!

## 🚨 Security Best Practices

### 1. Strong Passwords
- Use at least 12 characters
- Include uppercase, lowercase, numbers, and symbols
- Avoid common words or patterns

### 2. Secure JWT Secret
- Generate a cryptographically secure random string
- At least 32 characters long
- Never commit to version control

### 3. Environment Variables
- Never commit credentials to version control
- Use different credentials for each environment
- Rotate credentials regularly

### 4. HTTPS Only
- Always use HTTPS in production
- Set `FORCE_HTTPS=true`
- Use valid SSL certificates

### 5. Regular Updates
- Keep dependencies updated
- Monitor security advisories
- Review access logs regularly

## 🔍 Monitoring & Logging

### Rate Limit Monitoring
- Failed login attempts are logged
- Rate limit violations are tracked
- IP addresses are monitored

### Security Events
- Authentication failures
- Token validation errors
- Rate limit violations
- HTTPS redirects

## 🛡️ Additional Security Measures

### 1. IP Whitelisting (Optional)
Add IP whitelisting to admin routes:
```python
ALLOWED_ADMIN_IPS = ["192.168.1.100", "10.0.0.50"]
```

### 2. Two-Factor Authentication (Future)
Consider implementing 2FA for additional security:
- TOTP (Time-based One-Time Password)
- SMS verification
- Email verification

### 3. Session Management
- Automatic logout after inactivity
- Concurrent session limits
- Session invalidation on password change

## 🚨 Incident Response

### If Admin Account is Compromised
1. **Immediately change password**:
   ```bash
   python setup_admin.py
   ```

2. **Update environment variables**:
   ```bash
   heroku config:set ADMIN_PASSWORD_HASH=new_hash
   ```

3. **Review access logs** for suspicious activity

4. **Consider rotating JWT secret**:
   ```bash
   heroku config:set JWT_SECRET_KEY=new_secret
   ```

### If Rate Limits are Triggered
- Check for legitimate high traffic
- Review for potential attacks
- Adjust rate limits if needed
- Monitor IP addresses

## 📞 Support

For security-related issues:
1. Check the logs for error messages
2. Verify environment variables are set correctly
3. Test with the setup script
4. Review this documentation

## 🔄 Migration from Old System

If upgrading from the old session-based system:

1. **Install new dependencies**:
   ```bash
   pip install -r requirements.txt
   ```

2. **Generate new password hash**:
   ```bash
   python setup_admin.py
   ```

3. **Set environment variables** (see above)

4. **Deploy and test** the new authentication

The old session cookies will be automatically invalidated, and users will need to log in again with the new system.
