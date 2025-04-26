from django.urls import path
from . import views

app_name = 'accounts'

urlpatterns = [
    path('add/', views.UserCreateView.as_view(), name='user_add'),
    path('list/', views.UserListView.as_view(), name='user_list'),
    path('custom-login/', views.custom_login, name='custom_login'),
]
