# API Documentation

## Authentication
All endpoints require Bearer token except `/auth/register` and `/auth/login`.

## Endpoints

### Auth
- `POST /api/v1/auth/register` - Register new user
- `POST /api/v1/auth/login` - Login and get tokens

### Campaigns
- `POST /api/v1/campaigns` - Create campaign
- `GET /api/v1/campaigns` - List campaigns
- `GET /api/v1/campaigns/{id}` - Get campaign
- `PATCH /api/v1/campaigns/{id}` - Update campaign
- `POST /api/v1/campaigns/{id}/start` - Start campaign workflow
- `DELETE /api/v1/campaigns/{id}` - Delete campaign

### Businesses
- `GET /api/v1/businesses` - List businesses (with filters)
- `GET /api/v1/businesses/{id}` - Get business
- `PATCH /api/v1/businesses/{id}` - Update business
- `DELETE /api/v1/businesses/{id}` - Delete business

### Leads
- `GET /api/v1/leads` - List leads (with filters)
- `GET /api/v1/leads/{id}` - Get lead
- `PATCH /api/v1/leads/{id}` - Update lead

### Outreach
- `GET /api/v1/outreach` - List outreach messages
- `GET /api/v1/outreach/{id}` - Get outreach
- `PATCH /api/v1/outreach/{id}` - Update outreach
- `POST /api/v1/outreach/{id}/approve` - Approve/reject outreach

### Analytics
- `GET /api/v1/analytics/dashboard` - Dashboard metrics
- `GET /api/v1/analytics/campaigns/{id}` - Campaign metrics

### Jobs
- `GET /api/v1/jobs` - List background jobs
- `GET /api/v1/jobs/{id}` - Get job status
