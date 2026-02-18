
 
# PacificMart E-Commerce Platform

<p align="center">
  <img src="assets/logo.png" alt="GreatKart Logo" width="200" />
</p>

<!-- Badges -->
<p align="center">
  <img alt="Django" src="https://img.shields.io/badge/Django-5.2.6-092E20?style=for-the-badge&logo=django" />
  <img alt="Python" src="https://img.shields.io/badge/Python-3.12-3776AB?style=for-the-badge&logo=python" />
  <img alt="Render" src="https://img.shields.io/badge/Deployed%20on-Render-1E293B?style=for-the-badge&logo=render" />
  <img alt="Cloudinary" src="https://img.shields.io/badge/Storage-Cloudinary-232F3E?style=for-the-badge&logo=cloudinary" />
</p>

## Project Overview
**GreatKard** presents PacificMart - a comprehensive Django-based e-commerce platform designed for modern online retail. This robust solution features complete payment integration, advanced user management, and cloud-based storage infrastructure. Built with scalability and security in mind, PacificMart leverages Django 5.2.6 with Python 3.12 to deliver a seamless shopping experience with multi-payment gateway support (bKash, Nagad, Cash on Delivery), real-time inventory management, and enterprise-grade deployment capabilities on Render.

### Technical Architecture
The platform implements a sophisticated multi-app Django architecture with modular design principles:

- **User Management System**: Custom `Account` model extending Django's `AbstractUser` with email-based authentication, profile management, and role-based permissions
- **Product Catalog**: Advanced product management with variations (colors/sizes), review ratings, and Cloudinary image storage
- **Shopping Cart & Checkout**: Real-time cart functionality with session persistence and multi-step checkout process
- **Payment Processing**: Integrated payment gateways supporting local Bangladeshi mobile payments (bKash, Nagad) and traditional cash on delivery
- **Order Management**: Complete order lifecycle tracking with status updates and email notifications

### Database Design
The application features a well-structured relational database with proper foreign key relationships:
- **User Accounts**: Extended user model with profile pictures, addresses, and contact information
- **Product Management**: Products with categories, variations, reviews, and image galleries
- **Cart System**: Session-based cart with user association and product variations
- **Order Processing**: Orders with items, payment status, and delivery tracking
- **Payment Integration**: Separate models for each payment gateway with transaction tracking

## Architecture
- **Framework**: Django 5.2.6 with Python 3.12
- **Database**: PostgreSQL (production via Render), SQLite (development)
- **Storage**: Cloudinary for media files and images
- **Deployment**: Render with automated builds and database provisioning
- **Static Files**: WhiteNoise with compression and manifest
- **Payment Gateway**: Multiple payment methods (bKash, Nagad, Cash on Delivery)

## Project Structure

```
pacific_mart/
├── App/                           # Django application core
│   ├── accounts/                   # User authentication, profiles, and management
│   │   ├── models.py             # Custom Account model with email verification
│   │   ├── views.py              # Login, register, dashboard, profile management
│   │   └── templates/            # Account-related HTML templates
│   ├── cart/                       # Shopping cart functionality
│   │   ├── models.py             # Cart and CartItem models
│   │   ├── views.py              # Add to cart, update, remove items
│   │   └── templates/            # Cart and checkout templates
│   ├── category/                   # Product categorization
│   │   ├── models.py             # Category model with hierarchy support
│   │   └── admin.py              # Admin interface for categories
│   ├── orders/                     # Order processing and management
│   │   ├── models.py             # Order, OrderItem models with status tracking
│   │   ├── views.py              # Order placement, confirmation, history
│   │   └── templates/            # Order-related emails and pages
│   ├── payments/                   # Payment gateway integrations
│   │   ├── bkash/               # bKash payment integration
│   │   ├── nagad/               # Nagad payment integration
│   │   └── cashOnDelevery/     # Cash on delivery processing
│   ├── product/                    # Product catalog management
│   │   ├── models.py             # Product model with Cloudinary images
│   │   ├── views.py              # Product display, search, filtering
│   │   └── admin.py              # Product admin interface
│   ├── static/                      # Static assets (CSS, JS, images, fonts)
│   │   ├── css/                  # Bootstrap, custom responsive styles
│   │   ├── js/                   # jQuery, Bootstrap, custom scripts
│   │   ├── images/               # Product images, icons, banners
│   │   └── fonts/                # FontAwesome, custom web fonts
│   ├── templates/                   # HTML templates
│   │   ├── accounts/              # User account pages
│   │   ├── store/                 # E-commerce pages
│   │   ├── orders/                # Order confirmation pages
│   │   ├── payments/              # Payment gateway pages
│   │   └── includes/              # Reusable components (navbar, footer)
│   └── factors_Ecom/               # Django project settings
│       ├── settings.py            # Environment-aware configuration
│       ├── urls.py               # Main URL routing
│       ├── wsgi.py               # WSGI application entry point
│       └── asgi.py               # ASGI application entry point
├── docs/                           # Project documentation
│   ├── AUDIT_REPORT.md              # Security and performance audit findings
│   ├── DEPLOYMENT_GUIDE.md          # Step-by-step deployment instructions
│   └── RENDER_DEPLOYMENT.md         # Render-specific deployment guide
├── tests/                          # Testing and development tools
│   ├── test_all_urls.py             # URL endpoint testing
│   ├── test_results.txt             # Automated test results
│   └── run_server.{bat,ps1}       # Local development server scripts
├── build.sh                        # Automated build script for deployment
├── render.yaml                     # Render deployment configuration
├── requirements.txt                 # Python dependencies with pinned versions
├── .env.example                    # Environment variable template
└── README.md                       # This file
```

## Core Features

### User Management
- **Registration & Authentication**: Email-based user registration with verification
- **Profile Management**: Custom user profiles with avatar support
- **Dashboard**: User dashboard with order history and account settings
- **Security**: Password reset, email verification, secure session handling

### E-Commerce Functionality
- **Product Catalog**: Organized by categories with search and filtering
- **Shopping Cart**: Add, update, remove cart items with quantity management
- **Checkout Process**: Multi-step checkout with address and payment selection
- **Order Management**: Order placement, confirmation, tracking, and history

### Payment Integration
- **bKash**: Mobile payment gateway integration
- **Nagad**: Mobile payment gateway integration  
- **Cash on Delivery**: Traditional payment method processing
- **Payment Security**: Secure payment processing with order confirmation

### Admin Features
- **Django Admin**: Full admin interface for all models
- **Product Management**: Bulk product upload and management
- **Order Management**: Order viewing, status updates, and processing
- **User Management**: User account administration and support

## Development Setup

### Prerequisites
- Python 3.12+
- PostgreSQL client libraries
- Git for version control
- Cloudinary account (for media storage)

### Local Development
1. **Clone Repository**
   ```bash
   git clone https://github.com/NutCrackersOrg/pacific_mart.git
   cd pacific_mart
   ```

2. **Environment Setup**
   ```bash
   cp .env.example .env
   # Edit .env with your actual configuration
   ```

3. **Virtual Environment**
   ```bash
   python -m venv .venv
   source .venv/bin/activate
   pip install -r requirements.txt
   ```

4. **Database Setup**
   ```bash
   python App/manage.py makemigrations
   python App/manage.py migrate
   python App/manage.py createsuperuser
   ```

5. **Start Development Server**
   ```bash
   python App/manage.py runserver
   # Access at http://127.0.0.1:8000
   ```

### Testing
```bash
# Run URL endpoint tests
python tests/test_all_urls.py

# Run development server
python tests/run_server.bat  # Windows
python tests/run_server.ps1  # PowerShell
```

## Production Deployment

### Render Deployment
1. **Repository Setup**: Code pushed to GitHub repository
2. **Render Configuration**: `render.yaml` with database and service definitions
3. **Environment Variables**: Production secrets configured in Render dashboard
4. **Automated Build**: `build.sh` executes on each deployment
5. **Database Provisioning**: PostgreSQL database automatically created and connected

### Build Process
The `build.sh` script handles:
- **Dependency Installation**: Installs all Python requirements
- **Migration Creation**: Generates database migrations
- **Database Migration**: Applies schema changes
- **Static File Collection**: Collects and optimizes static assets
- **Health Checks**: Verifies database connectivity

### Environment Configuration
- **Development**: SQLite database, DEBUG=True, HTTP allowed
- **Production**: PostgreSQL database, DEBUG=False, HTTPS enforced
- **Security**: Automatic SSL redirects, secure cookies, CSRF protection

## Configuration Files

### Environment Variables (.env)
```env
# Core Django Settings
SECRET_KEY=your-secret-key-here
DEBUG=False
ALLOWED_HOSTS=pacific-mart.onrender.com
CSRF_TRUSTED_ORIGINS=https://pacific-mart.onrender.com

# Database Configuration
DATABASE_URL=postgresql://user:password@host:5432/dbname

# Cloudinary Configuration
CLOUDINARY_CLOUD_NAME=your-cloud-name
CLOUDINARY_API_KEY=your-api-key
CLOUDINARY_API_SECRET=your-api-secret

# Email Configuration
EMAIL_HOST=smtp.gmail.com
EMAIL_PORT=587
EMAIL_HOST_USER=your-email@gmail.com
EMAIL_HOST_PASSWORD=your-app-password
EMAIL_USE_TLS=True
```

### Render Configuration (render.yaml)
```yaml
databases:
  - name: thepacificmart-db
    plan: free
    databaseName: thepacificmart
    user: thepacificmart

services:
  - type: web
    plan: free
    name: thepacificmart
    runtime: python
    buildCommand: './build.sh'
    startCommand: 'python -m gunicorn factors_Ecom.wsgi:application --timeout 30 --workers 1'
    
    envVars:
      - key: DATABASE_URL
        fromDatabase:
          name: thepacificmart-db
          property: connectionString
      - key: SECRET_KEY
        generateValue: true
      - key: DEBUG
        value: "False"
      - key: ALLOWED_HOSTS
        value: "pacific-mart.onrender.com"
      - key: CSRF_TRUSTED_ORIGINS
        value: "https://pacific-mart.onrender.com"
```

## API Documentation

### User Authentication
- **POST** `/accounts/register/`: User registration with email verification
- **POST** `/accounts/login/`: User authentication with session creation
- **GET** `/accounts/logout/`: User session termination
- **GET** `/accounts/dashboard/`: User dashboard and profile management

### E-Commerce Operations
- **GET** `/store/`: Product listing with category filtering
- **GET** `/store/product/<id>/`: Individual product details
- **POST** `/cart/add_to_cart/<id>/`: Add items to shopping cart
- **GET** `/cart/`: View and manage shopping cart
- **POST** `/orders/place_order/`: Complete checkout and create order

### Payment Processing
- **GET** `/payments/bkash/`: bKash payment processing
- **GET** `/payments/nagad/`: Nagad payment processing
- **GET** `/payments/cod/`: Cash on delivery processing
- **POST** `/cod/pay/<order_id>/`: Cash payment confirmation

## Monitoring and Maintenance

### Health Checks
- **Database Connectivity**: Automated connection verification
- **Static File Status**: Collection and compression verification
- **Application Logs**: Build process logging and error tracking

### Performance Monitoring
- **Response Time**: Page load optimization
- **Database Query**: Query performance tracking
- **Static Delivery**: CDN performance via Cloudinary

## Security Considerations

### Implemented Security Measures
- **Environment Variable Protection**: Sensitive data in environment, not code
- **CSRF Protection**: All forms protected with CSRF tokens
- **SQL Injection Prevention**: Django ORM parameterized queries
- **XSS Protection**: Template auto-escaping and content security
- **Session Security**: Secure cookies with proper configuration
- **HTTPS Enforcement**: Automatic SSL redirect in production

### Security Best Practices
- **Regular Updates**: Dependencies kept up-to-date
- **Input Validation**: Form validation and sanitization
- **Access Control**: Role-based permissions and admin protection
- **Audit Logging**: User action tracking and security events

## Future Enhancements

### Planned Improvements
- **Advanced Search**: Full-text search with filtering and sorting
- **Order Tracking**: Real-time order status updates
- **Payment Analytics**: Payment method performance tracking
- **Mobile Optimization**: Progressive Web App and mobile-specific features
- **API Development**: RESTful API for mobile applications
- **Performance Monitoring**: Application performance metrics
- **Security Hardening**: Additional security layers and monitoring

### Scalability Considerations
- **Database Optimization**: Query optimization and indexing
- **CDN Integration**: Enhanced static file delivery
- **Load Balancing**: Multi-instance deployment support
- **Caching Strategy**: Redis integration for session and data caching

## Contributing Guidelines

### Development Workflow
1. **Fork Repository**: Create personal copy for development
2. **Feature Branch**: Create branch for new features
3. **Testing**: Comprehensive testing before deployment
4. **Documentation**: Update documentation for changes
5. **Pull Request**: Submit changes for review and merge

### Code Standards
- **PEP 8 Compliance**: Python code formatting and style
- **Django Best Practices**: Framework conventions and patterns
- **Security First**: Security considerations in all development
- **Test Coverage**: Unit tests for all new features
- **Documentation**: Clear documentation for complex functionality

## Support and Maintenance

### Troubleshooting
- **Build Failures**: Check `build.sh` logs and dependency versions
- **Database Issues**: Verify connection strings and migration status
- **Static File Problems**: Check `collectstatic` output and permissions
- **Payment Errors**: Review payment gateway credentials and API status

### Regular Maintenance
- **Dependency Updates**: Regular security and feature updates
- **Database Backups**: Automated backup verification
- **Log Rotation**: Manage application log files
- **Performance Reviews**: Regular performance assessment and optimization

---

**PacificMart** - Modern e-commerce platform built with Django, designed for scalability and security.
