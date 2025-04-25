from django.urls import path
from . import views

app_name = 'libraries'

urlpatterns = [
    path('', views.library_list, name='library_list'),
    path('<slug:slug>/', views.library_detail, name='library_detail'),
    path('manage/', views.manage_libraries, name='manage_libraries'),
    path('manage/<slug:slug>/', views.manage_library, name='manage_library'),
    path('manage/<slug:slug>/staff/', views.manage_library_staff, name='manage_library_staff'),
    path('manage/<slug:slug>/members/', views.manage_library_members, name='manage_library_members'),
]
