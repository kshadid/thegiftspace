# 🚀 The giftspace - Production Deployment Guide

Welcome to The giftspace production deployment guide! This document will help you deploy your wedding registry platform to production.

## 📋 Pre-Deployment Checklist

### ✅ Domain & SSL Setup
- [ ] Purchase domain: `thegiftspace.com`
- [ ] Set up DNS records pointing to your server
- [ ] Configure SSL certificate (Let's Encrypt or commercial)
- [ ] Set up www redirect (www.thegiftspace.com → thegiftspace.com)

### ✅ Email Configuration  
- [ ] Configure SPF record: `v=spf1 include:_spf.resend.com ~all`
- [ ] Configure DKIM record (provided by Resend)
- [ ] Update FROM_EMAIL to use your domain
- [ ] Test email deliverability

### ✅ Database Setup
- [ ] Set up production MongoDB (Atlas recommended)
- [ ] Configure database backups
- [ ] Set up monitoring and alerts
- [ ] Update MONGO_URL in production environment

### ✅ Monitoring & Alerting
- [ ] Create Sentry account at https://sentry.io
- [ ] Get your Sentry DSN
- [ ] Configure error monitoring
- [ ] Set up uptime monitoring

## 🔧 Environment Configuration

### Backend Environment Variables (.env)
```bash
# Database
MONGO_URL="mongodb+srv://username:password@cluster.mongodb.net/thegiftspace"
DB_NAME="thegiftspace_production"

# Security
JWT_SECRET="your-super-secure-jwt-secret-min-32-characters"
JWT_EXPIRE_MINUTES="1440"

# CORS (add your domain)
CORS_ORIGINS="https://thegiftspace.com,https://www.thegiftspace.com"

# Email
RESEND_API_KEY="re_cX3Y7GVT_8wN6Paz95ZmZ5rUhGp6nfKnU"
FROM_EMAIL="noreply@thegiftspace.com"

# Monitoring
SENTRY_DSN="https://your-dsn@sentry.io/project-id"
ENVIRONMENT="production"
APP_VERSION="1.0.0"

# Admin
ADMIN_EMAILS="your-admin@thegiftspace.com"
```

### Frontend Environment Variables (.env)
```bash
REACT_APP_BACKEND_URL="https://api.thegiftspace.com"
REACT_APP_DOMAIN="thegiftspace.com"
REACT_APP_COMPANY_NAME="The giftspace"
```

## 🏗️ Infrastructure Setup

### Option A: VPS/Dedicated Server
1. **Server Requirements:**
   - Ubuntu 20.04+ or CentOS 8+
   - 2GB+ RAM
   - 20GB+ SSD storage
   - Public IP address

2. **Install Dependencies:**
   ```bash
   # Update system
   sudo apt update && sudo apt upgrade -y
   
   # Install Node.js 18+
   curl -fsSL https://deb.nodesource.com/setup_18.x | sudo -E bash -
   sudo apt-get install -y nodejs
   
   # Install Python 3.11+
   sudo apt install python3.11 python3.11-pip python3.11-venv
   
   # Install Nginx
   sudo apt install nginx
   
   # Install MongoDB (or use Atlas)
   wget -qO - https://www.mongodb.org/static/pgp/server-6.0.asc | sudo apt-key add -
   echo "deb [ arch=amd64,arm64 ] https://repo.mongodb.org/apt/ubuntu focal/mongodb-org/6.0 multiverse" | sudo tee /etc/apt/sources.list.d/mongodb-org-6.0.list
   sudo apt-get update
   sudo apt-get install -y mongodb-org
   ```

3. **Deploy Application:**
   ```bash
   # Clone repository
   git clone https://github.com/your-username/thegiftspace.git
   cd thegiftspace
   
   # Backend setup
   cd backend
   python3.11 -m venv venv
   source venv/bin/activate
   pip install -r requirements.txt
   
   # Frontend setup
   cd ../frontend
   npm install
   npm run build
   ```

### Option B: Cloud Platforms

#### Vercel (Frontend) + Railway (Backend)
1. **Frontend on Vercel:**
   - Connect GitHub repository
   - Set build command: `npm run build`
   - Add environment variables
   - Deploy!

2. **Backend on Railway:**
   - Connect GitHub repository
   - Add environment variables
   - Deploy with automatic scaling

#### DigitalOcean App Platform
- One-click deployment
- Automatic scaling
- Built-in monitoring

## 🌐 Nginx Configuration

Create `/etc/nginx/sites-available/thegiftspace.com`:

```nginx
# Redirect www to non-www
server {
    listen 80;
    listen 443 ssl http2;
    server_name www.thegiftspace.com;
    
    # SSL configuration
    ssl_certificate /etc/letsencrypt/live/thegiftspace.com/fullchain.pem;
    ssl_certificate_key /etc/letsencrypt/live/thegiftspace.com/privkey.pem;
    
    return 301 https://thegiftspace.com$request_uri;
}

# Main site
server {
    listen 80;
    server_name thegiftspace.com;
    return 301 https://$server_name$request_uri;
}

server {
    listen 443 ssl http2;
    server_name thegiftspace.com;
    
    # SSL configuration
    ssl_certificate /etc/letsencrypt/live/thegiftspace.com/fullchain.pem;
    ssl_certificate_key /etc/letsencrypt/live/thegiftspace.com/privkey.pem;
    ssl_protocols TLSv1.2 TLSv1.3;
    ssl_ciphers ECDHE+AESGCM:ECDHE+CHACHA20:DHE+AESGCM:DHE+CHACHA20:!aNULL:!MD5:!DSS;
    ssl_prefer_server_ciphers off;
    
    # Security headers
    add_header X-Frame-Options DENY;
    add_header X-Content-Type-Options nosniff;
    add_header X-XSS-Protection "1; mode=block";
    add_header Strict-Transport-Security "max-age=31536000; includeSubDomains" always;
    
    # Frontend (React)
    location / {
        root /var/www/thegiftspace/frontend/build;
        try_files $uri $uri/ /index.html;
        
        # Cache static assets
        location ~* \.(js|css|png|jpg|jpeg|gif|ico|svg|woff|woff2)$ {
            expires 1y;
            add_header Cache-Control "public, immutable";
        }
    }
    
    # Backend API
    location /api/ {
        proxy_pass http://127.0.0.1:8001;
        proxy_http_version 1.1;
        proxy_set_header Upgrade $http_upgrade;
        proxy_set_header Connection 'upgrade';
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto $scheme;
        proxy_cache_bypass $http_upgrade;
        
        # CORS headers for production
        add_header Access-Control-Allow-Origin "https://thegiftspace.com" always;
        add_header Access-Control-Allow-Methods "GET, POST, PUT, DELETE, OPTIONS" always;
        add_header Access-Control-Allow-Headers "Authorization, Content-Type" always;
    }
}
```

Enable the site:
```bash
sudo ln -s /etc/nginx/sites-available/thegiftspace.com /etc/nginx/sites-enabled/
sudo nginx -t
sudo systemctl reload nginx
```

## 🔒 SSL Certificate Setup

### Using Certbot (Let's Encrypt)
```bash
# Install certbot
sudo apt install certbot python3-certbot-nginx

# Get certificate
sudo certbot --nginx -d thegiftspace.com -d www.thegiftspace.com

# Auto-renewal
sudo crontab -e
# Add: 0 12 * * * /usr/bin/certbot renew --quiet
```

## 📊 Monitoring Setup

### 1. Sentry Error Monitoring
1. Create account at https://sentry.io
2. Create new project for FastAPI
3. Copy DSN to environment variables
4. Configure alerts and notifications

### 2. Uptime Monitoring
- **UptimeRobot** (free): Monitor main pages
- **Pingdom**: Professional monitoring
- **StatusCake**: Advanced monitoring

### 3. Performance Monitoring
- **New Relic**: APM and infrastructure
- **DataDog**: Comprehensive monitoring
- **Google Analytics**: User behavior

## 🔄 Process Management

### Using Systemd

Create `/etc/systemd/system/thegiftspace-backend.service`:
```ini
[Unit]
Description=The giftspace Backend
After=network.target

[Service]
Type=simple
User=www-data
WorkingDirectory=/var/www/thegiftspace/backend
Environment=PATH=/var/www/thegiftspace/backend/venv/bin
ExecStart=/var/www/thegiftspace/backend/venv/bin/uvicorn server:app --host 0.0.0.0 --port 8001
Restart=always
RestartSec=3

[Install]
WantedBy=multi-user.target
```

Enable and start:
```bash
sudo systemctl enable thegiftspace-backend
sudo systemctl start thegiftspace-backend
sudo systemctl status thegiftspace-backend
```

## 📧 DNS Records Setup

Add these DNS records to your domain:

```
# A records
@               A       YOUR_SERVER_IP
www             A       YOUR_SERVER_IP
api             A       YOUR_SERVER_IP

# Email authentication
@               TXT     "v=spf1 include:_spf.resend.com ~all"
_dmarc          TXT     "v=DMARC1; p=quarantine; rua=mailto:dmarc@thegiftspace.com"

# DKIM (provided by Resend)
resend._domainkey  TXT  "YOUR_DKIM_KEY_FROM_RESEND"
```

## 🧪 Production Testing

### Pre-Launch Testing Checklist
- [ ] SSL certificate working
- [ ] All pages loading correctly
- [ ] User registration/login working
- [ ] Registry creation working
- [ ] Email notifications sending
- [ ] Contribution flow working
- [ ] Admin panel accessible
- [ ] Analytics tracking
- [ ] Error monitoring active
- [ ] Backup systems working

### Performance Testing
```bash
# Load testing with ab
apt install apache2-utils
ab -n 1000 -c 10 https://thegiftspace.com/

# Or use wrk
wrk -t12 -c400 -d30s https://thegiftspace.com/
```

## 🔐 Security Hardening

### Server Security
```bash
# Firewall setup
sudo ufw enable
sudo ufw allow ssh
sudo ufw allow 'Nginx Full'

# Disable root login
sudo sed -i 's/PermitRootLogin yes/PermitRootLogin no/' /etc/ssh/sshd_config
sudo systemctl restart ssh

# Fail2ban
sudo apt install fail2ban
sudo systemctl enable fail2ban
```

### Application Security
- ✅ JWT tokens with secure secrets
- ✅ Rate limiting on API endpoints
- ✅ Input validation with Pydantic
- ✅ CORS properly configured
- ✅ HTTPS everywhere
- ✅ Security headers in Nginx

## 📊 Analytics & SEO

### Google Analytics
1. Create GA4 property
2. Add tracking code to frontend
3. Configure goals and conversions

### Search Console
1. Verify domain ownership
2. Submit sitemap: `https://thegiftspace.com/sitemap.xml`
3. Monitor search performance

### SEO Checklist
- ✅ Sitemap.xml present
- ✅ Robots.txt configured
- ✅ Meta tags optimized
- ✅ Open Graph tags
- ✅ Fast loading times
- ✅ Mobile responsive

## 🎯 Go-Live Checklist

### Final Steps Before Launch
1. [ ] All environment variables configured
2. [ ] Database backed up and secured
3. [ ] SSL certificate active
4. [ ] Email deliverability tested
5. [ ] Error monitoring active
6. [ ] Performance optimized
7. [ ] Security measures in place
8. [ ] Analytics tracking configured
9. [ ] Legal pages complete
10. [ ] Admin access confirmed

### Launch Day
1. Deploy to production
2. Test all critical paths
3. Monitor error rates
4. Check email notifications
5. Verify analytics tracking
6. Announce launch! 🎉

## 🆘 Troubleshooting

### Common Issues

**Frontend not loading:**
- Check Nginx configuration
- Verify build files exist
- Check browser console for errors

**API not responding:**
- Check backend service status: `sudo systemctl status thegiftspace-backend`
- View logs: `sudo journalctl -u thegiftspace-backend -f`
- Verify database connection

**Emails not sending:**
- Check Resend API key
- Verify DNS records
- Check backend logs for email errors

**Performance issues:**
- Monitor with Sentry
- Check database queries
- Optimize static asset caching

## 📞 Support

For deployment support or issues:
- Email: support@thegiftspace.com
- Check logs: `/var/log/nginx/` and `journalctl`
- Monitor with Sentry dashboard

---

**🎊 Congratulations!** Your wedding registry platform is now ready for production!

Remember to:
- Monitor performance and errors
- Keep backups current
- Update dependencies regularly
- Scale as needed

**Happy registries!** 💕