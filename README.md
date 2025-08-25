# SYMT Parking Management System

A comprehensive Django-based parking management system designed for shopping centers and commercial complexes. This system provides complete control over parking spaces, commercial units, store management, and occupancy tracking.

## 🚀 Features

- **User Management**: Email-based authentication with custom user profiles
- **Store Management**: Business entity tracking with temporal occupancy relationships
- **Commercial Units**: Physical space management within parking facilities
- **Parking System**: Ticket management and space allocation
- **Location Management**: Organized parking area and zone management
- **Reporting**: Comprehensive analytics and reporting tools
- **Dashboard**: Administrative interface for system management

## 🛠️ Technology Stack

- **Backend**: Django 5.2 (Python)
- **Database**: SQLite (development) / PostgreSQL (production ready)
- **Authentication**: django-allauth with custom user model
- **Configuration**: django-split-settings for modular setup
- **Package Management**: uv (modern Python dependency management)
- **Frontend**: Bootstrap with custom dashboard styling
- **Language**: Spanish (es-mx) with Mexico City timezone

## 📋 Requirements

- Python 3.12+
- uv (Python package manager)

## 🚀 Quick Start

### 1. Clone the Repository

```bash
git clone <repository-url>
cd symt-parking
```

### 2. Install Dependencies

```bash
# Install uv if you haven't already
curl -LsSf https://astral.sh/uv/install.sh | sh

# Install project dependencies
uv sync
```

### 3. Database Setup

```bash
# Create and apply migrations
python manage.py makemigrations
python manage.py migrate

# Create a superuser account
python manage.py createsuperuser
```

### 4. Run the Development Server

```bash
python manage.py runserver
# or
uv run python manage.py runserver
```

Visit `http://127.0.0.1:8000` to access the application.

## 📁 Project Structure

```
symt-parking/
├── apps/                          # Custom Django applications
│   ├── accounts/                  # User authentication & profiles
│   │   ├── models/               # Custom user model
│   │   └── managers.py           # User management logic
│   ├── common/                   # Shared utilities and models
│   ├── dashboard/                # Administrative dashboard
│   ├── locations/                # Parking areas and zones
│   ├── parkings/                 # Parking space management
│   ├── reports/                  # Analytics and reporting
│   ├── stores/                   # Business entity management
│   │   ├── models/              # Store, CommercialUnit, UnitOccupancy
│   │   └── selectors/           # Complex query logic
│   └── tickets/                  # Parking ticket system
├── config/                       # Project configuration
│   ├── components/              # Split settings components
│   │   ├── auth.py             # Authentication settings
│   │   ├── base.py             # Base Django settings
│   │   ├── database.py         # Database configuration
│   │   └── email.py            # Email settings
│   └── settings.py             # Main settings file
├── static/                      # Static files (CSS, JS, images)
├── templates/                   # Django templates
└── manage.py                   # Django management script
```

## 🏗️ Architecture

### Apps Overview

- **accounts**: Custom user model with email authentication, profile management
- **stores**: Business entities (tenants/operators) with temporal occupancy tracking
- **locations**: Physical parking areas and zone organization
- **parkings**: Individual parking space management and allocation
- **tickets**: Parking ticket generation and management system
- **reports**: Analytics, reporting, and data visualization
- **dashboard**: Administrative interface and system overview
- **common**: Shared models, utilities, and base classes

### Key Models

- **CustomUser**: Email-based authentication with extended profile fields
- **Store**: Business entities that operate within the parking facility
- **CommercialUnit**: Physical commercial spaces (shops, offices)
- **UnitOccupancy**: Time-based relationships between stores and units
- **Location**: Parking areas and organizational zones

### Design Patterns

- **Selectors Pattern**: Complex database queries separated from views
- **Split Settings**: Modular configuration management
- **Custom User Manager**: Secure user creation and management

## 🧪 Testing

```bash
# Run all tests
python manage.py test

# Run tests for specific app
python manage.py test apps.accounts
python manage.py test apps.stores

# Run with verbose output
python manage.py test --verbosity=2
```

## 🔧 Development

### Adding Dependencies

```bash
# Add new dependency
uv add package-name

# Add development dependency
uv add --dev package-name

# Update lock file
uv lock
```

### Database Operations

```bash
# Create migrations for changes
python manage.py makemigrations

# Apply migrations
python manage.py migrate

# Reset database (development only)
rm db.sqlite3
python manage.py migrate
```

### Configuration

Create `config/local_settings.py` for local development overrides:

```python
# Example local_settings.py
DEBUG = True
ALLOWED_HOSTS = ['*']

# Override database settings, email configuration, etc.
```

## 🚀 Deployment Considerations

### Database

- Development uses SQLite for simplicity
- Production should use PostgreSQL or similar robust database
- Update `config/components/database.py` for production settings

### Static Files

```bash
# Collect static files for production
python manage.py collectstatic
```

### Environment Variables

Use environment variables for sensitive settings:
- Database credentials
- Email configuration
- Secret keys
- Third-party API keys

## 🤝 Contributing

1. Fork the repository
2. Create a feature branch (`git checkout -b feature/amazing-feature`)
3. Make your changes
4. Add tests for new functionality
5. Ensure all tests pass (`python manage.py test`)
6. Commit your changes (`git commit -m 'Add amazing feature'`)
7. Push to the branch (`git push origin feature/amazing-feature`)
8. Open a Pull Request

### Code Style Guidelines

- Follow Django best practices and conventions
- Use the apps/ directory structure for new applications
- Implement the selectors pattern for complex queries
- Add comprehensive docstrings and comments
- Ensure proper model relationships and data integrity

## 📝 License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

## 🆘 Support

For support and questions:
- Review the [CLAUDE.md](CLAUDE.md) file for development guidance
- Check the Django documentation for framework-specific questions
- Open an issue for bugs or feature requests

## 🏆 Acknowledgments

- Built with Django 5.2
- Uses django-allauth for authentication
- Styled with Bootstrap
- Package management with uv