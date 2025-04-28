"""
URL configuration for library_management project.

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/5.2/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  path('', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  path('', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.urls import include, path
    2. Add a URL to urlpatterns:  path('blog/', include('blog.urls'))
"""
from django.contrib import admin
from django.urls import path, include
from django.conf import settings
from django.conf.urls.static import static
from django.shortcuts import redirect
from apps.accounts import views as accounts_views

urlpatterns = [
    path('admin/accounts/user/add/', lambda request: redirect('accounts:user_add')),
    path('admin/', admin.site.urls),
    # Override specific allauth URLs with our custom views
    path('accounts/signup/', accounts_views.SimpleSignupView.as_view(), name='account_signup'),
    # Include our accounts URLs
    path('accounts/', include('apps.accounts.urls')),
    # Include remaining allauth URLs
    path('accounts/', include('allauth.urls')),
    path('', include('apps.core.urls')),
    path('libraries/', include('apps.libraries.urls')),
    path('books/', include('apps.books.urls')),
    path('transactions/', include('apps.transactions.urls')),

    # Role-based URLs
    path('superadmin/', include('apps.superadmin.urls')),
    path('library-admin/', include('apps.library_admin.urls')),
    path('staff/', include('apps.staff.urls')),
    path('member/', include('apps.member.urls')),
]

# Serve media files in development
if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
    urlpatterns += static(settings.STATIC_URL, document_root=settings.STATIC_ROOT)
