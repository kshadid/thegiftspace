# 🚀 The giftspace - Live Deployment Guide (Option B)

**Platform Setup: Vercel + Railway + MongoDB Atlas**
**Domain: thegiftspace.com (you own this ✅)**

---

## 📋 PHASE 1: Database Setup (5 minutes)

### 1.1 Create MongoDB Atlas Account
1. Go to https://www.mongodb.com/atlas
2. Click "Try Free" 
3. Sign up with your email
4. Choose **"Build a database"**

### 1.2 Create Free Cluster
1. Select **"M0 Sandbox"** (Free forever)
2. Choose **AWS** as provider
3. Select region closest to your users
4. Cluster name: `thegiftspace-prod`
5. Click **"Create Cluster"**

### 1.3 Configure Database Access
1. Go to **"Database Access"** in left sidebar
2. Click **"Add New Database User"**
3. Choose **"Password"** authentication
4. Username: `thegiftspace_user`
5. Generate secure password (save this!)
6. Database User Privileges: **"Read and write to any database"**
7. Click **"Add User"**

### 1.4 Configure Network Access
1. Go to **"Network Access"** in left sidebar  
2. Click **"Add IP Address"**
3. Click **"Allow access from anywhere"** (0.0.0.0/0)
4. Comment: "Production access"
5. Click **"Confirm"**

### 1.5 Get Connection String
1. Go to **"Databases"** in left sidebar
2. Click **"Connect"** on your cluster
3. Choose **"Connect your application"**
4. Driver: **Node.js**, Version: **4.1 or later**
5. Copy the connection string (looks like: `mongodb+srv://username:<password>@cluster.mongodb.net/`)
6. **SAVE THIS** - you'll need it soon!

---

## 🚀 PHASE 2: Backend Deployment (10 minutes)

### 2.1 Create Railway Account
1. Go to https://railway.app
2. Sign up with GitHub (recommended)
3. Verify your email

### 2.2 Deploy Backend to Railway
1. Click **"New Project"**
2. Choose **"Deploy from GitHub repo"**
3. Connect your GitHub account if needed
4. Select your thegiftspace repository
5. Railway will auto-detect it's a Python app

### 2.3 Configure Environment Variables
1. In Railway dashboard, click on your service
2. Go to **"Variables"** tab
3. Add these variables:

```
MONGO_URL = mongodb+srv://thegiftspace_user:YOUR_PASSWORD@cluster.mongodb.net/thegiftspace
DB_NAME = thegiftspace_production
JWT_SECRET = your-super-secure-jwt-secret-32-chars-minimum
CORS_ORIGINS = https://thegiftspace.com,https://www.thegiftspace.com
RESEND_API_KEY = re_cX3Y7GVT_8wN6Paz95ZmZ5rUhGp6nfKnU
FROM_EMAIL = noreply@thegiftspace.com
SENTRY_DSN = (leave empty for now)
ENVIRONMENT = production
APP_VERSION = 1.0.0
ADMIN_EMAILS = your-email@thegiftspace.com
```

### 2.4 Configure Railway Settings
1. Go to **"Settings"** tab
2. Set **"Root Directory"** to: `backend`
3. Set **"Start Command"** to: `uvicorn server:app --host 0.0.0.0 --port $PORT`
4. Click **"Deploy"**

### 2.5 Get Backend URL
1. After deployment, go to **"Settings"** > **"Networking"**
2. Click **"Generate Domain"**
3. Copy the generated URL (e.g., `https://thegiftspace-production.up.railway.app`)
4. **SAVE THIS** - it's your backend URL!

---

## 🌐 PHASE 3: Frontend Deployment (10 minutes)

### 3.1 Create Vercel Account
1. Go to https://vercel.com
2. Sign up with GitHub (recommended)
3. Import your project repository

### 3.2 Configure Frontend Build
1. In Vercel dashboard, click **"Import"** your repo
2. Framework Preset: **"Create React App"**
3. Root Directory: `frontend`
4. Build Command: `npm run build`
5. Output Directory: `build`

### 3.3 Configure Environment Variables
1. In project settings, go to **"Environment Variables"**
2. Add these variables:

```
REACT_APP_BACKEND_URL = https://your-railway-backend-url.up.railway.app
REACT_APP_DOMAIN = thegiftspace.com
REACT_APP_COMPANY_NAME = The giftspace
```

### 3.4 Deploy Frontend
1. Click **"Deploy"**
2. Wait for build to complete
3. Get your Vercel URL (e.g., `https://thegiftspace.vercel.app`)

---

## 🌍 PHASE 4: Domain Configuration (15 minutes)

### 4.1 Configure Custom Domain on Vercel
1. In Vercel project dashboard, go to **"Settings"** > **"Domains"**
2. Add domain: `thegiftspace.com`
3. Add domain: `www.thegiftspace.com`
4. Vercel will show you DNS records to configure

### 4.2 Configure DNS Records
**Go to your domain registrar (GoDaddy, Namecheap, etc.) and add:**

```
Type    Name    Value
A       @       76.76.19.61 (Vercel's IP)
A       www     76.76.19.61 (Vercel's IP)
CNAME   @       cname.vercel-dns.com
CNAME   www     cname.vercel-dns.com
```

**Or use Vercel's nameservers (easier):**
1. In Vercel, go to **Domains** > **"Use Vercel DNS"**
2. Copy the nameservers
3. Update nameservers in your domain registrar

### 4.3 Configure Email DNS Records
**Add these for email deliverability:**

```
Type    Name                    Value
TXT     @                       "v=spf1 include:_spf.resend.com ~all"
TXT     _dmarc                  "v=DMARC1; p=quarantine; rua=mailto:dmarc@thegiftspace.com"
CNAME   resend._domainkey       resend1._domainkey.resend.com
```

---

## 🧪 PHASE 5: Testing & Verification (10 minutes)

### 5.1 Wait for DNS Propagation (5-30 minutes)
- Check https://dnschecker.org with your domain
- Test: https://thegiftspace.com should load your site

### 5.2 Test Core Features
1. **Homepage loads**: Visit https://thegiftspace.com
2. **User registration**: Create a test account
3. **Registry creation**: Make a test registry  
4. **Contribution flow**: Test making a contribution
5. **Email notifications**: Check if emails are sent
6. **Admin access**: Test admin login

### 5.3 SSL Certificate
- Vercel automatically provides SSL
- https://thegiftspace.com should show secure padlock

---

## 🔧 PHASE 6: Final Configuration (10 minutes)

### 6.1 Update Backend CORS
1. Go back to Railway dashboard
2. Update `CORS_ORIGINS` variable to:
   ```
   https://thegiftspace.com,https://www.thegiftspace.com
   ```

### 6.2 Update Frontend Backend URL
1. In Vercel dashboard, update environment variable:
   ```
   REACT_APP_BACKEND_URL = https://your-railway-domain.up.railway.app
   ```

### 6.3 Redeploy Both Services
1. In Railway: Click **"Deploy"** 
2. In Vercel: Go to **"Deployments"** > **"Redeploy"**

---

## 🎉 PHASE 7: You're Live! 

### ✅ Success Checklist
- [ ] https://thegiftspace.com loads correctly
- [ ] User registration works
- [ ] Registry creation works  
- [ ] Contributions work
- [ ] Emails are being sent
- [ ] Admin panel accessible
- [ ] Mobile version works

### 🚀 Post-Launch Tasks
1. **Set up Sentry**: Follow SENTRY_SETUP.md
2. **Monitor performance**: Check Railway and Vercel dashboards  
3. **Test email deliverability**: Send test contributions
4. **Social media**: Announce your launch! 

---

## 📞 Support During Deployment

**If you get stuck:**
1. **Railway Issues**: Check logs in Railway dashboard
2. **Vercel Issues**: Check build logs in Vercel  
3. **DNS Issues**: Wait 30 minutes for propagation
4. **Email Issues**: Verify DNS records with dig/nslookup

**Common Issues:**
- **Backend not connecting**: Check MONGO_URL format
- **Frontend not loading**: Check REACT_APP_BACKEND_URL
- **CORS errors**: Update CORS_ORIGINS in Railway
- **Email not sending**: Verify DNS records

---

## 💡 Pro Tips

1. **Use Railway CLI** for easier deployments: `npm i -g @railway/cli`
2. **Monitor costs**: Both platforms have generous free tiers
3. **Scale when needed**: Upgrade plans as you grow
4. **Backup database**: Set up MongoDB Atlas backups
5. **Use custom domains**: Looks more professional

---

**🎊 Ready to Launch The giftspace!** 

This setup gives you:
- **Professional hosting** with 99.9% uptime
- **Automatic scaling** based on traffic  
- **SSL certificates** managed automatically
- **Global CDN** for fast loading worldwide
- **Easy deployments** with Git integration

**Your platform is ready to help couples create amazing wedding registries!** 💕