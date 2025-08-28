# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Project Overview

**SYMT Parking** is a Django 5.2 parking management system designed for shopping centers and commercial complexes. The system manages stores, commercial units, parking tickets, and real-time parking occupancy tracking. 

**Key Features:**
- Email-based user authentication with custom user profiles
- **Hierarchical user role management system** with 4-tier access control
- Store and commercial unit management with temporal occupancy tracking
- Parking space allocation and ticket management
- Location-based parking area organization
- Comprehensive reporting system
- Dashboard interface for administrative tasks

**Technology Stack:**
- Django 5.2 (Python web framework)
- PostgreSQL 17 (database)
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
- `apps.accounts` - Custom user model using email authentication + **hierarchical role management**
- `apps.stores` - Store management with temporal occupancy tracking
- `apps.locations` - Location/parking area management
- `apps.parkings` - Parking space management
- `apps.tickets` - Parking ticket system
- `apps.reports` - Reporting functionality
- `apps.common` - Shared models and utilities
- `apps.dashboard` - Administrative interface with **user management** section

### Key Models
- `CustomUser` (apps.accounts) - Email-based authentication with profile fields
- **`UserProfile` (apps.accounts) - Hierarchical role system with location/store assignments**
- `Store` (apps.stores) - Business/operator entities
- `CommercialUnit` (apps.stores) - Physical commercial spaces
- `UnitOccupancy` (apps.stores) - Temporal store-unit relationships
- `Location` (apps.locations) - Physical locations/plazas

### Authentication & User Management
- Uses `django-allauth` for authentication
- Custom user model with email as USERNAME_FIELD
- User manager: `apps.accounts.managers.CustomUserManager`
- **Hierarchical role system with 4-tier access control:**
  - **Admin** - Full system access, can manage multiple locations and create any user type
  - **Admin Plaza** - Limited to one location, can create managers and store users for their plaza
  - **Gerente Local** - Limited to their store, can create store users for their establishment
  - **Usuario Local** - Operational user who processes parking tickets only

### Database
- Uses PostgreSQL 17 for all environments
- Timezone: America/Mexico_City
- Language: Spanish (es-mx)

### URL Structure
The project uses a highly modular URL configuration with Spanish-language URL patterns:

**Main URL Configuration (`config/urls.py`):**
- `/admin/` - Django admin interface
- `/accounts/` - django-allauth authentication URLs (login, logout, signup, etc.)
- `/` - Dashboard root (maps to apps.dashboard.urls with namespace 'dashboard')

**Dashboard URL Organization (`apps/dashboard/urls/`):**
The dashboard uses a modular URL structure with separate files for each resource:
- `/` - Dashboard home (`DashboardView`)
- `/locations/` - Location management (namespace: 'locations')
- `/tiendas/` - Store management (namespace: 'stores') 
- `/unidades-comerciales/` - Commercial unit management (namespace: 'commercial_units')
- `/ocupaciones/` - Unit occupancy management (namespace: 'unit_occupancies')
- `/estacionamientos/` - Parking management (namespace: 'parkings')
- `/tickets/` - Ticket management (namespace: 'tickets')
- **`/usuarios/` - User management (namespace: 'users') - Role-based access control**

**Standard CRUD URL Pattern:**
Each resource follows a consistent Spanish URL pattern:
- `''` - List view (e.g., `/tiendas/`)
- `'crear/'` - Create view (e.g., `/tiendas/crear/`)
- `'<uuid:pk>/'` - Detail view (e.g., `/tiendas/123e4567-e89b-12d3-a456-426614174000/`)
- `'<uuid:pk>/editar/'` - Update view (e.g., `/tiendas/123e4567-e89b-12d3-a456-426614174000/editar/`)
- `'<uuid:pk>/eliminar/'` - Delete view (e.g., `/tiendas/123e4567-e89b-12d3-a456-426614174000/eliminar/`)

**URL Naming Convention:**
- Uses Django's reverse URL naming with namespaces
- Format: `dashboard:resource_name:action` (e.g., `dashboard:stores:create`)
- All models use UUID primary keys in URLs for security

### Selectors Pattern
The codebase uses a selector pattern for complex queries:
- Example: `apps.stores.selectors.unit_occupancy.get_current_store_for_unit()`
- Separates query logic from views and models

## User Management System

### Role Hierarchy
The system implements a 4-tier hierarchical role system designed for shopping center management:

**1. Admin (Administrator)**
- **Scope:** System-wide access across all locations
- **Capabilities:**
  - Manage multiple locations through `managed_locations` M2M field
  - Create and manage all user types (Admin, Admin Plaza, Gerente Local, Usuario Local)
  - Full CRUD access to all system resources
  - Access all dashboard sections without restrictions

**2. Admin Plaza (Plaza Administrator)**
- **Scope:** Single location (shopping center/plaza)
- **Assignment:** Must have a `location` assigned via FK relationship
- **Capabilities:**
  - Create and manage Gerente Local and Usuario Local users within their plaza
  - Manage stores and commercial units within their assigned location
  - View and manage all operations within their plaza boundary
  - Cannot create other Admin Plaza or Admin users

**3. Gerente Local (Store Manager)**
- **Scope:** Single store within a plaza
- **Assignment:** Must have a `store` assigned via FK relationship
- **Capabilities:**
  - Create and manage Usuario Local users for their specific store
  - Manage their store's operations and data
  - Process and validate parking tickets for their store
  - Limited view access only to their store's data

**4. Usuario Local (Store User/Cashier)**
- **Scope:** Single store, operational level only
- **Assignment:** Must have a `store` assigned via FK relationship
- **Capabilities:**
  - Process parking tickets and handle customer transactions
  - View basic operational data for their store
  - Cannot create or manage other users
  - Limited to operational tasks only

### Implementation Details

**Models:**
- `UserProfile` (apps.accounts.models.user_profile) - Extends CustomUser with role and relationship data
- Database constraints ensure proper role assignments (CheckConstraint)
- M2M relationship for Admin users to manage multiple locations

**Views & Templates:**
- Complete CRUD interface at `/usuarios/` (dashboard:users namespace)
- Role-based form fields with dynamic JavaScript visibility
- Permission-filtered querysets based on user hierarchy
- Spanish language interface following project conventions

**Permissions & Security:**
- Permission decorators in `apps.accounts.utils.permissions`
- Mixins: `RoleRequiredMixin`, `CanManageUserMixin`, `UserManagementMixin`
- View-level filtering prevents users from seeing/managing unauthorized data
- Database constraints prevent invalid role-location/store combinations

**Example Usage:**
```python
# Check if user can manage another user
if request.user.profile.can_manage_user(target_profile):
    # Allow management action
    
# Get users current user can manage
queryset = request.user.profile.get_managed_users()

# Apply role-based decorator
@role_required(UserProfile.Role.ADMIN, UserProfile.Role.ADMIN_PLAZA)
def my_view(request):
    # View logic here
```

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
- **`UserProfile` extends CustomUser with role-based permissions and location/store assignments**
- **Hierarchical relationships:** Admin → Admin Plaza → Gerente Local → Usuario Local

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
- **Role-based access control (RBAC) with hierarchical permissions**
- **Permission decorators and mixins** in `apps.accounts.utils.permissions`
- **Database constraints** ensure proper role-location/store assignments
- **View-level security** prevents unauthorized user management

## Performance Notes
- PostgreSQL 17 provides robust performance for all deployment scales
- Selectors pattern optimizes complex queries
- Static file serving configured for development
- UUID primary keys enhance security but require indexing consideration
- All code must be generated in English
- add to memory. remember, this project use uv