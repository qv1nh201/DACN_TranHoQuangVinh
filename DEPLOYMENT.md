# Deployment Guide

## Security Setup

### Before Deploying:

1. **Environment Variables**
   - Never commit `.env` files or `firebase_key.json` to Git
   - Use your hosting platform's environment variable settings

2. **For Different Platforms:**

   **Render/Railway/Heroku:**
   - Go to your app settings → Environment Variables
   - Add each variable from `.env.example`
   - Paste the private key as-is (including `-----BEGIN PRIVATE KEY-----`)

   **Docker:**
   ```bash
   docker run -e FIREBASE_PROJECT_ID=xxx -e FIREBASE_PRIVATE_KEY="..." your-image
   ```

   **Azure/AWS:**
   - Use Azure Key Vault or AWS Secrets Manager
   - Reference secrets in your app configuration

3. **Current Status:**
   - ✅ Credentials are hardcoded in `firebase_client.py` (works but not ideal)
   - ⚠️ Should migrate to environment variables for production
   - ✅ `.gitignore` updated to protect sensitive files

### Recommended: Migrate to Environment Variables

Update `backend/app/firebase_client.py` to use environment variables instead of hardcoded values for better security.

### After Deployment:

1. **Delete Local Sensitive Files:**
   ```bash
   rm backend/firebase_key.json
   ```

2. **Verify .gitignore:**
   ```bash
   git status
   # Should NOT show firebase_key.json or .env files
   ```

3. **Test in Production:**
   - Check logs for Firebase connection success
   - Verify database reads/writes work
