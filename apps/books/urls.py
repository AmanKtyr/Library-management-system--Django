from django.urls import path
from . import views

app_name = 'books'

urlpatterns = [
    path('', views.book_list, name='book_list'),
    path('authors/', views.author_list, name='author_list'),
    path('authors/<slug:slug>/', views.author_detail, name='author_detail'),
    path('categories/', views.category_list, name='category_list'),
    path('categories/<slug:slug>/', views.category_detail, name='category_detail'),
    path('manage/', views.manage_books, name='manage_books'),
    path('manage/add/', views.add_book, name='add_book'),
    path('manage/edit/<slug:slug>/', views.edit_book, name='edit_book'),
    path('manage/copies/', views.manage_book_copies, name='manage_book_copies'),
    path('<slug:slug>/', views.book_detail, name='book_detail'),
]
