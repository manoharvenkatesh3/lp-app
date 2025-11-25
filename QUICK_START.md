# Quick Start Guide - Recruiter Dashboard

Get the Recruiter Dashboard up and running in 5 minutes.

## Prerequisites

- Python 3.10+
- Node.js 18+
- PostgreSQL 14+ (or use Docker)

## Option 1: Docker (Recommended)

The fastest way to get started:

```bash
# Clone and navigate to project
cd /path/to/project

# Start all services
docker-compose up -d

# Wait for services to start (about 30 seconds)
docker-compose logs -f
```

**Access the application:**
- Frontend: http://localhost:3000
- Backend API: http://localhost:8000/api
- API Docs: http://localhost:8000/api/docs

## Option 2: Manual Setup

### Step 1: Database Setup

**Option A - Docker PostgreSQL:**
```bash
docker run -d \
  --name recruiter-postgres \
  -e POSTGRES_DB=recruiter_db \
  -e POSTGRES_PASSWORD=postgres \
  -p 5432:5432 \
  postgres:15-alpine
```

**Option B - Local PostgreSQL:**
```bash
# Create database
createdb recruiter_db
```

### Step 2: Backend Setup

```bash
# Navigate to backend
cd backend

# Create virtual environment
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate

# Install dependencies
pip install -r requirements.txt

# Configure environment
export DATABASE_URL="postgresql+asyncpg://postgres:postgres@localhost/recruiter_db"
export JWT_SECRET_KEY="your-secret-key-change-in-production"

# Initialize database
python -c "from database import init_db; import asyncio; asyncio.run(init_db())"

# Start the server
uvicorn main:app --reload --host 0.0.0.0 --port 8000
```

### Step 3: Frontend Setup

```bash
# In a new terminal, navigate to frontend
cd frontend

# Install dependencies
npm install

# Start development server
npm run dev
```

## Step 4: Create Your First User

### Using the API directly:

```bash
curl -X POST http://localhost:8000/api/auth/register \
  -H "Content-Type: application/json" \
  -d '{
    "email": "admin@company.com",
    "username": "admin",
    "password": "securepass123",
    "role": "admin"
  }'
```

### Or use the frontend:
1. Open http://localhost:3000
2. You'll be redirected to the login page
3. First, create an admin user via the API (see above)
4. Then login with your credentials

## Step 5: Explore the Dashboard

Once logged in, you can:

1. **Dashboard** - View interview statistics
2. **Scheduling** - Schedule new interviews
3. **Live Monitoring** - Monitor interviews in real-time
4. **Candidates** - View candidate history
5. **Analytics** - Analyze performance metrics

## Step 6: Set Up ATS Integration (Optional)

### Register an ATS Integration:

```bash
curl -X POST http://localhost:8000/api/ats/integrations/register \
  -H "Content-Type: application/json" \
  -d '{
    "name": "My ATS",
    "webhook_url": "https://yourcompany.com/webhook"
  }'
```

**Save the API key** returned in the response!

### Test the Integration:

```bash
cd scripts
export ATS_API_KEY="ats_xxx..."  # Use your API key
python ats_integration_sample.py
```

## Common Issues

### Database Connection Error
```
Error: could not connect to server
```

**Solution:**
- Ensure PostgreSQL is running
- Check DATABASE_URL is correct
- Verify database exists: `psql -l`

### Port Already in Use
```
Error: Port 8000 is already in use
```

**Solution:**
```bash
# Find and kill the process
lsof -ti:8000 | xargs kill -9

# Or use a different port
uvicorn main:app --port 8001
```

### Node Module Errors
```
Error: Cannot find module 'react'
```

**Solution:**
```bash
cd frontend
rm -rf node_modules package-lock.json
npm install
```

### CORS Errors in Browser
```
Access to fetch at 'http://localhost:8000' has been blocked by CORS policy
```

**Solution:**
- Ensure backend is running
- Check CORS configuration in `backend/main.py`
- Access frontend at the correct URL (http://localhost:3000)

## Next Steps

1. **Read the Documentation:**
   - [Complete Dashboard Documentation](DASHBOARD_README.md)
   - [API Documentation](API_DOCUMENTATION.md)

2. **Create Test Data:**
   - Add candidates via API or ATS integration
   - Schedule test interviews
   - Create scorecards

3. **Configure for Production:**
   - Set strong JWT_SECRET_KEY
   - Configure proper CORS origins
   - Set up SSL/TLS
   - Configure database connection pooling
   - Set up monitoring and logging

4. **Customize:**
   - Adjust bias detection keywords
   - Customize role permissions
   - Add custom notification handlers
   - Extend ATS integration

## Development Workflow

### Backend Development:
```bash
cd backend
source venv/bin/activate
uvicorn main:app --reload
```

### Frontend Development:
```bash
cd frontend
npm run dev
```

### Run Tests:
```bash
# Backend tests
cd backend
pytest

# Frontend tests
cd frontend
npm test
```

### Format Code:
```bash
# Backend
black backend/
isort backend/

# Frontend
cd frontend
npm run lint
```

## Support

If you encounter issues:
1. Check the logs: `docker-compose logs -f` (if using Docker)
2. Review error messages in browser console
3. Check API documentation: http://localhost:8000/api/docs
4. Review the documentation files in this repository

## Security Notes

⚠️ **Important for Production:**

1. **Change default secrets:**
   ```bash
   export JWT_SECRET_KEY=$(openssl rand -hex 32)
   ```

2. **Use strong passwords** for database and admin accounts

3. **Enable HTTPS** in production

4. **Restrict CORS origins** to your actual domain

5. **Set up rate limiting** with Redis

6. **Regular security audits** and dependency updates

7. **Database backups** configured

## What's Next?

- Explore the live monitoring feature with WebSocket connections
- Create scorecards and see bias detection in action
- Test the ATS integration with sample scripts
- Review audit logs for compliance
- Customize the UI theme and branding

Happy recruiting! 🚀
