# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Project Overview

This is a Django 5.2 parking management system for shopping centers, managing stores, commercial units, tickets, and parking occupancy. The project uses uv for dependency management and follows Django app structure conventions.

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

### Selectors Pattern
The codebase uses a selector pattern for complex queries:
- Example: `apps.stores.selectors.unit_occupancy.get_current_store_for_unit()`
- Separates query logic from views and models