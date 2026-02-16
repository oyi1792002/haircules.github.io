from django.shortcuts import render, redirect
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.models import User
from django.contrib import messages
from django.contrib.auth.decorators import login_required
from .models import Profile

def register(request):
    """Halaman pendaftaran user"""
    if request.method == 'POST':
        username = request.POST.get('username')
        email = request.POST.get('email')
        password = request.POST.get('password')
        password2 = request.POST.get('password2')
        phone = request.POST.get('phone')
        role = request.POST.get('role', 'customer')
        
        if password != password2:
            messages.error(request, 'Password tidak sama!')
            return redirect('register')
        
        if User.objects.filter(username=username).exists():
            messages.error(request, 'Username sudah digunakan!')
            return redirect('register')
        
        # Create user
        user = User.objects.create_user(
            username=username,
            email=email,
            password=password
        )
        
        # Update profile
        user.profile.phone = phone
        user.profile.role = role
        user.profile.save()
        
        messages.success(request, 'Pendaftaran berjaya! Sila login.')
        return redirect('login')
    
    return render(request, 'accounts/register.html')

def login_view(request):
    """Halaman login"""
    if request.method == 'POST':
        username = request.POST.get('username')
        password = request.POST.get('password')
        
        user = authenticate(request, username=username, password=password)
        
        if user is not None:
            login(request, user)
            
            # ===== CHECK PENDING BOOKING =====
            # Kalau ada pending booking, pergi confirm dulu
            if 'pending_booking' in request.session:
                return redirect('/booking/confirm/')
            # ==================================
            
            # ===== TIADA PENDING BOOKING =====
            # Redirect based on role
            if user.is_superuser or user.profile.role == 'admin':
                return redirect('/admin/')  # Admin pergi admin panel
            elif user.profile.role == 'barber':
                return redirect('barber_dashboard')  # Barber pergi dashboard
            else:
                return redirect('customer_dashboard')  # Customer pergi dashboard
            # ==================================
        else:
            messages.error(request, 'Username atau password salah!')
    
    return render(request, 'accounts/login.html')

def logout_view(request):
    """Logout user"""
    logout(request)
    messages.success(request, 'Anda telah logout.')
    return redirect('home')

@login_required
def customer_dashboard(request):
    """Dashboard untuk customer - dengan statistik lengkap"""
    from booking.models import Appointment
    
    # Filter booking untuk customer yang sedang login GUNA CUSTOMER FIELD!
    bookings = Appointment.objects.filter(customer=request.user).order_by('-date', '-time')
    
    # Kira statistik berdasarkan booking SEBENAR
    total_bookings = bookings.count()
    pending_bookings = bookings.filter(status='pending').count()
    confirmed_bookings = bookings.filter(status='confirmed').count()
    completed_bookings = bookings.filter(status='completed').count()
    cancelled_bookings = bookings.filter(status='cancelled').count()
    
    return render(request, 'accounts/customer_dashboard.html', {
        'bookings': bookings,
        'total_bookings': total_bookings,
        'pending_bookings': pending_bookings,
        'confirmed_bookings': confirmed_bookings,
        'completed_bookings': completed_bookings,
        'cancelled_bookings': cancelled_bookings,
    })

@login_required
def barber_dashboard(request):
    """Dashboard untuk barber"""
    from booking.models import Barber, Appointment
    
    # Handle kalau barber name tak sama dengan username
    try:
        barber = Barber.objects.get(name=request.user.username)
    except Barber.DoesNotExist:
        # Kalau tak jumpa, cuba cari Barber yang first
        barber = Barber.objects.first()
        if not barber:
            # Kalang langsung takde barber, redirect ke home
            messages.error(request, 'Barber profile not found!')
            return redirect('home')
    
    appointments = Appointment.objects.filter(barber=barber).order_by('date', 'time')
    
    # Kira statistik untuk barber
    total_appointments = appointments.count()
    today_appointments = appointments.filter(date__date='2026-02-12').count()  # Boleh adjust
    pending_appointments = appointments.filter(status='pending').count()
    completed_appointments = appointments.filter(status='completed').count()
    
    return render(request, 'accounts/barber_dashboard.html', {
        'appointments': appointments,
        'barber': barber,
        'total_appointments': total_appointments,
        'today_appointments': today_appointments,
        'pending_appointments': pending_appointments,
        'completed_appointments': completed_appointments,
    })