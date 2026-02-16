from django.contrib import admin
from .models import Barber, Hairstyle, Appointment, Feedback  # ← Tambah Feedback!

@admin.register(Feedback)
class FeedbackAdmin(admin.ModelAdmin):
    list_display = ['customer_name', 'barber', 'rating', 'appointment', 'created_at']
    list_filter = ['rating', 'barber', 'created_at']
    search_fields = ['customer_name', 'comment']

@admin.register(Barber)
class BarberAdmin(admin.ModelAdmin):
    list_display = ['name', 'phone', 'is_active']
    list_editable = ['is_active']

@admin.register(Hairstyle)
class HairstyleAdmin(admin.ModelAdmin):
    list_display = ['name', 'face_shape', 'price', 'is_popular']
    list_filter = ['face_shape', 'is_popular']
    list_editable = ['price', 'is_popular']

@admin.register(Appointment)
class AppointmentAdmin(admin.ModelAdmin):
    list_display = ['customer_name', 'date', 'time', 'barber', 'status']
    list_filter = ['status', 'date', 'barber']
    list_editable = ['status']
    search_fields = ['customer_name', 'customer_phone']