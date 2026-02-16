from django.urls import path
from . import views

urlpatterns = [
    path('register/', views.register, name='register'),
    path('login/', views.login_view, name='login'),
    path('logout/', views.logout_view, name='logout'),
    path('dashboard/', views.customer_dashboard, name='customer_dashboard'),
    path('barber-dashboard/', views.barber_dashboard, name='barber_dashboard'),
]