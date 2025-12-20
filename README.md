# ATF Sentinel

**Automated Security Scanning for GitHub Pull Requests**

ATF Sentinel is a comprehensive security scanning platform that automatically analyzes Pull Requests for security vulnerabilities, hardcoded secrets, and code quality issues. It features a modern dashboard, AI-powered analysis, and seamless integration with GitHub and Slack.

## Architecture

```
atf-sentinel/
├── backend/                 # FastAPI Python Backend
│   ├── app/
│   │   ├── main.py         # API endpoints & webhook handler
│   │   ├── config.py       # Configuration management
│   │   ├── database.py     # Cloud SQL connection
│   │   ├── models.py       # SQLAlchemy models
│   │   ├── scanner.py      # Security scan orchestration
│   │   ├── pattern_scanner.py  # Regex pattern detection
│   │   ├── gemini_analyzer.py  # AI-powered analysis
│   │   ├── github_client.py    # GitHub API integration
│   │   ├── reporter.py     # Slack notifications
│   │   └── slack_client.py # Slack API client
│   ├── tests/
│   ├── Dockerfile
│   └── requirements.txt
│
├── frontend/               # Next.js 15 Dashboard
│   ├── app/               # App Router pages
│   │   ├── dashboard/     # Main dashboard
│   │   ├── analytics/     # Detailed analytics
│   │   ├── metrics/       # Time-series metrics
│   │   ├── champions/     # Security leaderboard
│   │   ├── tests/         # AI test generator
│   │   ├── chat/          # Security AI chat
│   │   └── api/           # API routes
│   ├── components/        # React components
│   ├── lib/               # Utilities & Prisma
│   ├── prisma/            # Database schema
│   ├── Dockerfile
│   └── package.json
│
├── cloudbuild.yaml        # GCP Cloud Build config
├── docker-compose.yml     # Local development
├── deploy.sh              # Manual deployment script
└── .env.example           # Environment template
```

## Features

- **Automated PR Scanning**: Webhook-triggered security scans on every PR
- **Pattern Detection**: Regex-based detection of secrets, API keys, credentials
- **AI Analysis**: Gemini-powered vulnerability detection and recommendations
- **Real-time Dashboard**: Modern UI with charts and analytics
- **Security Champions**: Gamified leaderboard for secure coding
- **AI Chat**: Ask questions about security best practices
- **Test Generator**: AI-powered security test case generation
- **Slack Alerts**: Instant notifications for security issues

## Tech Stack

### Backend
- **Python 3.12** with FastAPI
- **SQLAlchemy 2.0** for ORM
- **Cloud SQL (PostgreSQL)** for data storage
- **Google Gemini** for AI analysis
- **PyGithub** for GitHub integration

### Frontend
- **Next.js 15** with App Router
- **React 19** with TypeScript
- **Tailwind CSS** for styling
- **Prisma 6** for database access
- **Recharts** for data visualization

### Infrastructure
- **Google Cloud Run** for serverless deployment
- **Cloud Build** for CI/CD
- **Secret Manager** for credentials
- **Cloud SQL** for PostgreSQL

## Quick Start

### Prerequisites

- Node.js 20+
- Python 3.12+
- Docker & Docker Compose
- GCP Account (for deployment)
- GitHub Account

### Local Development

1. **Clone the repository**
   ```bash
   git clone https://github.com/atf-inc/atf-sentinel.git
   cd atf-sentinel
   ```

2. **Set up environment variables**
   ```bash
   cp .env.example .env
   # Edit .env with your values
   ```

3. **Start with Docker Compose**
   ```bash
   docker-compose up -d
   ```

   This starts:
   - PostgreSQL on `localhost:5432`
   - Backend API on `localhost:8000`
   - Frontend on `localhost:3000`

4. **Or run services individually**

   Backend:
   ```bash
   cd backend
   python -m venv venv
   source venv/bin/activate
   pip install -r requirements.txt
   uvicorn app.main:app --reload --port 8000
   ```

   Frontend:
   ```bash
   cd frontend
   npm install
   npm run dev
   ```

### Access Points

- **Frontend Dashboard**: http://localhost:3000
- **Backend API Docs**: http://localhost:8000/docs
- **Health Check**: http://localhost:8000/health

## Configuration

### Required Environment Variables

| Variable | Description |
|----------|-------------|
| `DATABASE_URL` | PostgreSQL connection string |
| `GITHUB_TOKEN` | GitHub Personal Access Token |
| `WEBHOOK_SECRET` | GitHub webhook secret |
| `GEMINI_API_KEY` | Google Gemini API key |
| `ALLOWED_REPOS` | JSON array of allowed repositories |

### Optional Variables

| Variable | Description |
|----------|-------------|
| `SLACK_WEBHOOK_URL` | Slack incoming webhook URL |
| `FRONTEND_URL` | Frontend URL for CORS |
| `GCP_PROJECT_ID` | GCP project ID |

## Deployment to GCP

### Prerequisites

1. GCP Project with billing enabled
2. Enable APIs:
   - Cloud Run
   - Cloud Build
   - Cloud SQL
   - Secret Manager
   - Container Registry

3. Create secrets in Secret Manager:
   - `github-token`
   - `webhook-secret`
   - `gemini-api-key`
   - `db-password`
   - `database-url`

### Deploy with Cloud Build

```bash
gcloud builds submit --config=cloudbuild.yaml \
  --substitutions=_REGION=us-central1
```

### Manual Deployment

```bash
./deploy.sh all
```

Or deploy services individually:
```bash
./deploy.sh backend
./deploy.sh frontend
```

## GitHub Webhook Setup

1. Go to your repository → Settings → Webhooks
2. Add webhook:
   - **Payload URL**: `https://your-backend-url/webhook/github`
   - **Content type**: `application/json`
   - **Secret**: Your `WEBHOOK_SECRET` value
   - **Events**: Select "Pull requests"

## API Endpoints

### Webhook
- `POST /webhook/github` - GitHub webhook handler

### Analytics
- `GET /api/analytics/dashboard` - Dashboard summary
- `GET /api/analytics/repos` - Repository metrics
- `GET /api/analytics/engineers` - Engineer metrics

### Metrics
- `GET /api/metrics` - Time-series data
- `GET /api/champions` - Leaderboard
- `GET /api/issues/patterns` - Issue distribution

### Scans
- `GET /api/scans/recent` - Recent scan results

## Contributing

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Run tests
5. Submit a pull request

## License

MIT License - see LICENSE file for details.

## Author

**ANIRUDH S J** - ATF Inc.

---

For questions or support, please open an issue on GitHub.
