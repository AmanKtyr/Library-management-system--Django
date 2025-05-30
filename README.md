# LibraryHub - Modern Library Management System

A comprehensive Django-based library management system designed to efficiently manage multiple libraries, books, users, and transactions.

![LibraryHub](static/images/library-hero.jpg)

## Features

- **Multi-Library Support**: Manage multiple libraries from a single platform
- **User Role Management**: Different access levels for super admins, library admins, staff members, and library members
- **Book Management**: Comprehensive book catalog with details, covers, and availability tracking
- **Transaction System**: Handle book borrowing, returns, and reservations
- **Membership Management**: Track library memberships and user access
- **Modern UI**: Responsive design with dark mode support
- **Search & Filter**: Advanced search capabilities for books, authors, and categories
- **Reporting**: Generate reports on transactions, popular books, and more

## Technology Stack

- **Backend**: Django 
- **Frontend**: HTML5, CSS3, JavaScript
- **CSS Framework**: Bootstrap 5
- **Icons**: Font Awesome
- **Animations**: AOS (Animate On Scroll)
- **Fonts**: Google Fonts (Poppins, Roboto)

## Installation

1. Clone the repository:
   ```bash
   git clone https://github.com/yourusername/libraryhub.git
   cd libraryhub
   ```

2. Create and activate a virtual environment:
   ```bash
   python -m venv venv
   # On Windows
   venv\Scripts\activate
   # On macOS/Linux
   source venv/bin/activate
   ```

3. Install dependencies:
   ```bash
   pip install -r requirements.txt
   ```

4. Apply migrations:
   ```bash
   python manage.py migrate
   ```

5. Create a superuser:
   ```bash
   python manage.py createsuperuser
   ```

6. Run the development server:
   ```bash
   python manage.py runserver
   ```

7. Access the application at http://127.0.0.1:8000/

## User Roles

- **Super Admin**: Full access to all libraries and system settings
- **Library Admin**: Manage a specific library, its books, and staff
- **Staff Member**: Handle day-to-day operations like check-ins and check-outs
- **Library Member**: Browse books, borrow, return, and manage personal account

## Project Structure

```
libraryhub/
├── core/                  # Core functionality and views
├── books/                 # Book management app
├── libraries/             # Library management app
├── transactions/          # Transaction management app
├── users/                 # User management app
├── static/                # Static files (CSS, JS, images)
│   ├── css/               # CSS files
│   ├── js/                # JavaScript files
│   └── images/            # Image files
├── templates/             # HTML templates
│   ├── core/              # Core templates
│   ├── books/             # Book-related templates
│   ├── libraries/         # Library-related templates
│   └── transactions/      # Transaction-related templates
├── media/                 # User-uploaded files
└── manage.py              # Django management script
```

## Customization

The system uses CSS variables for easy theming. You can modify the color scheme and other design elements by editing the `static/css/style.css` file.

## Contributing

1. Fork the repository
2. Create your feature branch (`git checkout -b feature/amazing-feature`)
3. Commit your changes (`git commit -m 'Add some amazing feature'`)
4. Push to the branch (`git push origin feature/amazing-feature`)
5. Open a Pull Request

## License

This project is licensed under the MIT License - see the LICENSE file for details.

## Acknowledgements

- [Django](https://www.djangoproject.com/)
- [Bootstrap](https://getbootstrap.com/)
- [Font Awesome](https://fontawesome.com/)
- [AOS Library](https://michalsnik.github.io/aos/)
- [Google Fonts](https://fonts.google.com/)


super admin
Id aman@gmail.com
pass Aman@#12

Library admin
Id ktyrpro@gmail.com
pass Aman@#12



