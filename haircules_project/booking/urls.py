from django.urls import path
from . import views

urlpatterns = [
    path('', views.home, name='home'),
    path('test-face/', views.test_face, name='test_face'),
    path('booking/', views.booking_form, name='booking_form'),
    path('booking/submit/', views.booking_submit, name='booking_submit'),
    path('booking/confirm/', views.booking_confirm, name='booking_confirm'),  # ← TAMBAH INI!
    path('booking/feedback/<int:appointment_id>/', views.feedback_form, name='feedback_form'),
    path('booking/barber/<int:barber_id>/reviews/', views.barber_reviews, name='barber_reviews'),
    path('booking/get-slots/', views.get_available_slots, name='get_slots'),
        path('booking/get-slots/', views.get_available_slots, name='get_slots'),  # ← TAMBAH INI!

]