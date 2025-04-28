from django.urls import path
from . import views

app_name = 'books'

urlpatterns = [
    path('', views.book_list, name='book_list'),
    path('authors/', views.author_list, name='author_list'),
    path('authors/<slug:slug>/', views.author_detail, name='author_detail'),
    # Category routes removed - now handled in library_admin app
    path('manage/', views.manage_books, name='manage_books'),
    path('manage/add/', views.add_book, name='add_book'),
    path('manage/edit/<slug:slug>/', views.edit_book, name='edit_book'),
    path('delete/<int:pk>/', views.delete_book, name='delete_book'),
    path('manage/copies/', views.manage_book_copies, name='manage_book_copies'),
    path('copies/delete/<int:pk>/', views.delete_book_copy, name='delete_book_copy'),
    path('<slug:slug>/', views.book_detail, name='book_detail'),

    # API endpoints for autocomplete
    path('api/authors/autocomplete/', views.autocomplete_authors, name='autocomplete_authors'),
    path('api/categories/autocomplete/', views.autocomplete_categories, name='autocomplete_categories'),
]
