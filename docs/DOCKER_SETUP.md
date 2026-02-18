# 🐳 Docker Setup for Pacific Mart (Minimal SQLite)

## Quick Start with Docker

### Prerequisites
- Docker installed on your system
- Docker Compose installed

### 1. Clone and Navigate
```bash
git clone <your-repo-url>
cd pacific_mart
```

### 2. Start the Application
```bash
docker-compose up --build
```

This will:
- Build the minimal Docker image
- Run Django migrations (SQLite database)
- Collect static files
- Start the development server

### 3. Access the Application
- **Main App:** http://localhost:8001
- **Admin Panel:** http://localhost:8001/admin/

### 4. Create Superuser (Optional)
Open a new terminal and run:
```bash
docker-compose exec web python manage.py createsuperuser
```

## Development Commands

### Start services
```bash
docker-compose up
```

### Start in detached mode
```bash
docker-compose up -d
```

### Stop services
```bash
docker-compose down
```

### View logs
```bash
docker-compose logs -f 
```

### Run Django commands
```bash
docker-compose exec web python manage.py <command>
```

### Create migrations
```bash
docker-compose exec web python manage.py makemigrations
```

### Apply migrations
```bash
docker-compose exec web python manage.py migrate
```

### Collect static files
```bash
docker-compose exec web python manage.py collectstatic
```

## Environment Configuration

The Docker setup automatically loads environment variables from the `.env` file in the project root.

### Required Environment Variables

Make sure your `.env` file contains at least:

```bash
# Django Core
SECRET_KEY=your-secret-key-here
DEBUG=True
ALLOWED_HOSTS=localhost,127.0.0.1
CSRF_TRUSTED_ORIGINS=http://localhost:8001,http://127.0.0.1:8001

# Cloudinary (Required)
CLOUDINARY_CLOUD_NAME=your-cloud-name
CLOUDINARY_API_KEY=your-api-key
CLOUDINARwebY_API_SECRET=your-api-secret

# Database (Optional - defaults to SQLite)
DATABASE_URL=sqlite:///db.sqlite3

# Email (Optional)
EMAIL_HOST=smtp.gmail.com
EMAIL_PORT=587
EMAIL_HOST_USER=your-email@gmail.com
EMAIL_HOST_PASSWORD=your-app-password
EMAIL_USE_TLS=True
```

### Setup Instructions

1. Copy `.env.example` to `.env`:
```bash
cp .env.example .env
```

2. Update `.env` with your actual values
3. Restart Docker:
```bash
clear && docker-compose down && docker-compose up --build
```

4. Create superuser (optional):
```bash
docker-compose exec web python manage.py createsuperuser
```

5. Start Shell
```bash
docker-compose exec web python manage.py shell
```

## Database

- **Development:** SQLite (file-based, no setup required)
- **Production:** Consider PostgreSQL for better performance

## Troubleshooting

### Port already in use
```bash
# Check what's using port 8001
lsof -i :8001
# Or change port in docker-compose.yml
```

### Database issues
```bash
# Reset database (removes all data)
docker-compose down -v
docker-compose up --build
```

### Permission issues
```bash
# Fix file permissions
sudo chown -R $USER:$USER .
```

## Production Deployment

For production deployment, consider:

1. Use environment-specific `.env` file
2. Set `DEBUG=False`
3. Use PostgreSQL instead of SQLite
4. Configure proper ALLOWED_HOSTS
5. Set up SSL/HTTPS
6. Use reverse proxy (nginx)

## One-Command Development Setup

```bash
git clone <repo-url> && cd pacific_mart && docker-compose up --build
```

That's it! Your Pacific Mart e-commerce app is running with minimal Docker setup. 🚀
