# Library Management System - Project Structure

This document outlines the developer-friendly structure of the Library Management System project.

## Directory Structure

```
library_management/
├── apps/                  # All Django apps are organized here
│   ├── accounts/          # User authentication and management
│   ├── books/             # Book management
│   ├── core/              # Core functionality
│   ├── libraries/         # Library management
│   ├── library_admin/     # Library admin functionality
│   ├── member/            # Member functionality
│   ├── staff/             # Staff functionality
│   ├── superadmin/        # Super admin functionality
│   └── transactions/      # Transaction management
│
├── library_management/    # Project settings and configuration
│
├── media/                 # User-uploaded files
│
├── static/                # Static files (CSS, JS, images)
│   ├── css/               # CSS files
│   ├── js/                # JavaScript files
│   ├── images/            # Image files
│   └── videos/            # Video files
│
├── templates/             # HTML templates organized by role
│   ├── accounts/          # Authentication templates
│   ├── core/              # Shared templates and layouts
│   ├── library_admin/     # Library admin dashboard templates
│   ├── members/           # Member dashboard templates
│   ├── staff/             # Staff dashboard templates
│   ├── super_admin/       # Super admin dashboard templates
│   └── base.html          # Base template for the entire site
│
└── manage.py              # Django management script
```

## Role-Based Organization

The project is organized according to user roles:

1. **Member** - Regular library users who can borrow books
2. **Staff** - Library staff who assist with day-to-day operations
3. **Library Admin** - Administrators of individual libraries
4. **Super Admin** - System administrators who manage all libraries

Each role has its own Django app and corresponding templates folder.

## Template Structure

Templates are organized by role to make it easier to find and modify templates for specific user types:

- `templates/accounts/` - Authentication templates (login, signup, password reset)
- `templates/core/` - Shared templates and layouts
  - `admin_base.html` - Base template for all admin dashboards
- `templates/library_admin/` - Templates for library administrators
  - `base.html` - Extends core/admin_base.html
  - `includes/sidebar.html` - Sidebar menu for library admin
  - Dashboard, books, members, and other library admin pages
- `templates/members/` - Templates for regular library members
  - `base.html` - Base template for member pages
  - `includes/sidebar.html` - Sidebar menu for members
  - Dashboard, borrowed books, profile, and other member pages
- `templates/staff/` - Templates for library staff
  - `base.html` - Extends core/admin_base.html
  - `includes/sidebar.html` - Sidebar menu for staff
  - Dashboard, circulation, and other staff pages
- `templates/super_admin/` - Templates for super administrators
  - `base.html` - Extends core/admin_base.html
  - `includes/sidebar.html` - Sidebar menu for super admin
  - Dashboard, libraries, users, and other super admin pages

## Static Files

All static files are organized in the `static` folder:

- `static/css/` - CSS files
- `static/js/` - JavaScript files
- `static/images/` - Image files
- `static/videos/` - Video files

## Development Guidelines

1. Keep all apps in the `apps` folder
2. Place all templates in the appropriate role-based folder in `templates`
3. Store all static files in the `static` folder
4. Follow the naming conventions for files and folders
5. Use the base templates for consistent styling
