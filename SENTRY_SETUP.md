# 🔍 Sentry Error Monitoring Setup for The giftspace

This guide will help you set up Sentry error monitoring for The giftspace platform.

## 📝 Step-by-Step Setup

### 1. Create Sentry Account
1. Go to https://sentry.io
2. Sign up with your email
3. Choose "Create a new organization"
4. Organization name: "The giftspace"
5. Select the free plan (up to 5,000 errors/month)

### 2. Create Projects

#### Backend Project (FastAPI)
1. Click "Create Project"
2. Platform: **Python**
3. Framework: **FastAPI**
4. Project name: "thegiftspace-backend"
5. Copy the DSN (looks like: `https://abc123@o123456.ingest.sentry.io/123456`)

#### Frontend Project (React) - Optional
1. Create another project
2. Platform: **JavaScript**
3. Framework: **React**
4. Project name: "thegiftspace-frontend"
5. Copy the DSN

### 3. Configure Backend Environment

Add your Sentry DSN to `/app/backend/.env`:
```bash
SENTRY_DSN="https://your-dsn-here@o123456.ingest.sentry.io/123456"
ENVIRONMENT="production"
APP_VERSION="1.0.0"
```

### 4. Test Sentry Integration

1. Restart the backend:
   ```bash
   sudo supervisorctl restart backend
   ```

2. Check logs to confirm Sentry initialization:
   ```bash
   tail -f /var/log/supervisor/backend.err.log
   ```
   You should see: "Sentry monitoring initialized"

3. Test error reporting by triggering a test error:
   ```bash
   curl -X GET "https://your-domain.com/api/sentry-test"
   ```

### 5. Configure Alerts

1. Go to your Sentry project dashboard
2. Navigate to **Alerts** → **Create Alert Rule**
3. Set up alerts for:
   - New issues (immediate email)
   - Error rate threshold (>10 errors/minute)
   - Performance issues (response time >2s)

### 6. Set Up Integrations

#### Slack Integration (Recommended)
1. Go to **Settings** → **Integrations**
2. Find Slack and click **Install**
3. Authorize Sentry to access your Slack workspace
4. Configure which channels receive alerts

#### Email Notifications
1. Go to **Settings** → **Notifications**
2. Configure email alerts for:
   - New issues
   - Error rate spikes
   - Performance degradation

### 7. Dashboard Setup

Create custom dashboards for:
- **Error Overview**: Error rate, affected users, top errors
- **Performance**: Response times, throughput, slow endpoints
- **Business Metrics**: Registry creations, contributions, user signups

### 8. Production Configuration

For production deployment, add these environment variables:

```bash
# Production
SENTRY_DSN="your-production-dsn"
ENVIRONMENT="production"
APP_VERSION="1.0.0"

# Staging
SENTRY_DSN="your-staging-dsn"
ENVIRONMENT="staging"
APP_VERSION="1.0.0-staging"
```

## 🎯 Monitoring Best Practices

### Error Categorization
- **Critical**: Payment failures, data corruption
- **High**: Authentication failures, email sending failures
- **Medium**: Validation errors, rate limiting
- **Low**: 404 errors, client-side issues

### Performance Monitoring
Monitor these key metrics:
- API response times
- Database query performance
- Email sending success rates
- User registration flow

### Custom Events
Track business-critical events:
```python
import sentry_sdk

# Track registry creation
sentry_sdk.add_breadcrumb(
    message="Registry created",
    data={"registry_id": registry.id, "owner": registry.owner_id},
    level="info"
)

# Track contribution
sentry_sdk.add_breadcrumb(
    message="Contribution received",
    data={"amount": contribution.amount, "fund_id": contribution.fund_id},
    level="info"
)
```

## 🚨 Alert Configuration Examples

### Critical Alerts (Immediate)
- Server errors (5xx responses)
- Database connection failures
- Email service failures
- Authentication system failures

### Warning Alerts (15 min delay)
- High error rate (>50 errors/hour)
- Slow response times (>2s average)
- Failed login attempts (>100/hour)

### Info Alerts (Daily digest)
- New feature usage
- Performance summaries
- User activity reports

## 📊 Key Metrics to Monitor

### Technical Metrics
- Error rate: <1% of all requests
- Response time: <500ms average
- Uptime: >99.9%
- Email delivery rate: >95%

### Business Metrics
- Registry creation rate
- Contribution success rate
- User engagement
- Feature adoption

## 🔧 Troubleshooting

### Common Issues

**Sentry not capturing errors:**
- Check DSN configuration
- Verify network connectivity
- Check Sentry client initialization

**Too many alerts:**
- Adjust alert thresholds
- Set up alert rules properly
- Use fingerprinting to group similar errors

**Missing performance data:**
- Increase traces_sample_rate
- Check transaction naming
- Verify performance monitoring is enabled

### Debug Commands
```bash
# Test Sentry connection
python -c "import sentry_sdk; sentry_sdk.init('YOUR_DSN'); sentry_sdk.capture_message('Test message')"

# Check Sentry configuration
curl -X POST "https://sentry.io/api/0/projects/ORG/PROJECT/keys/" \
  -H "Authorization: Bearer YOUR_TOKEN"
```

## 💡 Advanced Features

### Release Tracking
Track deployments and releases:
```python
sentry_sdk.init(
    dsn="YOUR_DSN",
    release="thegiftspace@1.0.0",
    environment="production"
)
```

### User Context
Associate errors with users:
```python
sentry_sdk.set_user({
    "id": user.id,
    "email": user.email,
    "username": user.name
})
```

### Custom Tags
Tag errors for better filtering:
```python
sentry_sdk.set_tag("feature", "registry_creation")
sentry_sdk.set_tag("user_type", "premium")
```

## 🎉 You're All Set!

Once configured, Sentry will:
- ✅ Capture all errors automatically
- ✅ Send alerts for critical issues
- ✅ Provide performance insights
- ✅ Help debug production issues
- ✅ Track release health

Your wedding registry platform now has enterprise-level error monitoring! 🚀

---

**Need help?** Contact Sentry support or check their documentation at https://docs.sentry.io