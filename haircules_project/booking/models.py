from django.db import models
from django.contrib.auth.models import User

class Barber(models.Model):
    """Model untuk barber/staff"""
    user = models.OneToOneField(User, on_delete=models.CASCADE, null=True, blank=True)
    name = models.CharField(max_length=100)
    phone = models.CharField(max_length=15)
    photo = models.ImageField(upload_to='barbers/', null=True, blank=True)
    is_active = models.BooleanField(default=True)
    
    def __str__(self):
        return self.name

class Hairstyle(models.Model):
    """Model untuk gaya rambut"""
    FACE_SHAPES = [
        ('Oval', 'Oval'),
        ('Round', 'Round'),
        ('Square', 'Square'),
        ('Long', 'Long'),
        ('Heart', 'Heart'),
    ]
    
    name = models.CharField(max_length=100)
    description = models.TextField(blank=True)
    face_shape = models.CharField(max_length=20, choices=FACE_SHAPES)
    image = models.ImageField(upload_to='hairstyles/', null=True, blank=True)
    price = models.DecimalField(max_digits=6, decimal_places=2, default=0)
    is_popular = models.BooleanField(default=False)
    
    def __str__(self):
        return f"{self.name} - {self.face_shape}"

class Appointment(models.Model):
    """Model untuk tempahan"""
    STATUS_CHOICES = [
        ('pending', 'Pending'),
        ('confirmed', 'Confirmed'),
        ('completed', 'Completed'),
        ('cancelled', 'Cancelled'),
    ]
    
    customer = models.ForeignKey(User, on_delete=models.CASCADE, null=True, blank=True)
    customer_name = models.CharField(max_length=100)
    customer_phone = models.CharField(max_length=15)
    customer_email = models.EmailField(blank=True)
    
    barber = models.ForeignKey(Barber, on_delete=models.SET_NULL, null=True)
    hairstyle = models.ForeignKey(Hairstyle, on_delete=models.SET_NULL, null=True)
    
    date = models.DateField()
    time = models.TimeField()
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='pending')
    
    face_shape_detected = models.CharField(max_length=20, blank=True)
    user_photo = models.ImageField(upload_to='appointments/', null=True, blank=True)
    preview_photo = models.ImageField(upload_to='previews/', null=True, blank=True)
    
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    def __str__(self):
        return f"{self.customer_name} - {self.date} {self.time}"

# ✅ FEEDBACK CLASS - MESTI DI LUAR!
class Feedback(models.Model):
    """Feedback untuk barber dari customer"""
    RATING_CHOICES = [
        (1, '1 ⭐'),
        (2, '2 ⭐⭐'),
        (3, '3 ⭐⭐⭐'),
        (4, '4 ⭐⭐⭐⭐'),
        (5, '5 ⭐⭐⭐⭐⭐'),
    ]
    
    appointment = models.OneToOneField(Appointment, on_delete=models.CASCADE, related_name='feedback')
    barber = models.ForeignKey(Barber, on_delete=models.CASCADE, related_name='feedbacks')
    customer_name = models.CharField(max_length=100)
    rating = models.IntegerField(choices=RATING_CHOICES, default=5)
    comment = models.TextField(blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    
    def __str__(self):
        return f"{self.customer_name} - {self.barber.name} - {self.rating}⭐"