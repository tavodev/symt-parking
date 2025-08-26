# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Project Overview

**SYMT Parking** is a Django 5.2 parking management system designed for shopping centers and commercial complexes. The system manages stores, commercial units, parking tickets, and real-time parking occupancy tracking. 

**Key Features:**
- Email-based user authentication with custom user profiles
- Store and commercial unit management with temporal occupancy tracking
- Parking space allocation and ticket management
- Location-based parking area organization
- Comprehensive reporting system
- Dashboard interface for administrative tasks

**Technology Stack:**
- Django 5.2 (Python web framework)
- SQLite (development database)
- django-allauth (authentication)
- django-split-settings (modular configuration)
- uv (modern Python package management)
- Bootstrap (frontend styling)

## Common Commands

### Development Server
```bash
python manage.py runserver
# or
uv run python manage.py runserver
```

### Database Operations
```bash
# Create migrations
python manage.py makemigrations

# Apply migrations  
python manage.py migrate

# Create superuser
python manage.py createsuperuser
```

### Testing
```bash
# Run all tests
python manage.py test

# Run tests for specific app
python manage.py test apps.accounts
python manage.py test apps.stores
```

### Package Management
```bash
# Install dependencies
uv sync

# Add new dependency
uv add package-name

# Update lock file
uv lock
```

## Architecture

### Settings Structure
- Uses `django-split-settings` for modular configuration
- Settings split into components: `base.py`, `database.py`, `auth.py`, `email.py`
- Main settings file: `config/settings.py`
- Local overrides: `config/local_settings.py` (optional)

### Custom Apps Structure
- `apps.accounts` - Custom user model using email authentication
- `apps.stores` - Store management with temporal occupancy tracking
- `apps.locations` - Location/parking area management
- `apps.parkings` - Parking space management
- `apps.tickets` - Parking ticket system
- `apps.reports` - Reporting functionality
- `apps.common` - Shared models and utilities

### Key Models
- `CustomUser` (apps.accounts) - Email-based authentication with profile fields
- `Store` (apps.stores) - Business/operator entities
- `CommercialUnit` (apps.stores) - Physical commercial spaces
- `UnitOccupancy` (apps.stores) - Temporal store-unit relationships

### Authentication
- Uses `django-allauth` for authentication
- Custom user model with email as USERNAME_FIELD
- User manager: `apps.accounts.managers.CustomUserManager`

### Database
- Uses SQLite for development (`db.sqlite3`)
- Timezone: America/Mexico_City
- Language: Spanish (es-mx)

### URL Structure
The project uses a modular URL configuration:
- Main URL config: `config/urls.py`
- Admin panel: `/admin/` - Django admin interface
- Authentication: `/accounts/` - django-allauth authentication URLs (login, logout, signup, etc.)
- Dashboard: `/` - Main dashboard interface (apps.dashboard.urls with namespace 'dashboard')
- Individual app URLs included via namespace pattern for modularity

### Selectors Pattern
The codebase uses a selector pattern for complex queries:
- Example: `apps.stores.selectors.unit_occupancy.get_current_store_for_unit()`
- Separates query logic from views and models

## Development Guidelines

### Code Organization
- Follow Django app conventions with logical separation of concerns
- Use the `apps/` directory for all custom Django applications
- Keep models, views, and business logic properly separated
- Utilize the selectors pattern for complex database queries

### Model Relationships
- `Store` represents business entities (tenants/operators)
- `CommercialUnit` represents physical spaces within the parking facility
- `UnitOccupancy` creates temporal relationships between stores and units
- `CustomUser` handles all user authentication and profile management

### Static Files and Templates
- Static files located in `static/` directory
- Templates use Django's template system with Bootstrap styling
- Dashboard interface provides administrative functionality

### Configuration Management
- Environment-specific settings using django-split-settings
- Components separated by functionality (auth, database, email, base)
- Use `config/local_settings.py` for local development overrides (not tracked in git)

## Security Considerations
- Email-based authentication instead of username
- Custom user manager handles user creation securely
- Uses django-allauth for robust authentication flows
- Profile pictures uploaded to secure directory structure

## Performance Notes
- SQLite suitable for development and small-scale deployments
- Consider PostgreSQL for production environments
- Selectors pattern optimizes complex queries
- Static file serving configured for development