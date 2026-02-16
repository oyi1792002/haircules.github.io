from django.shortcuts import render, redirect
from django.http import HttpResponse, JsonResponse
from django.shortcuts import get_object_or_404 
from django.db.models import Avg, Count
from django.contrib.auth.decorators import login_required
from django.views.decorators.csrf import csrf_exempt
from .models import Barber, Hairstyle, Appointment, Feedback

def home(request):
    """Halaman utama Haircules dengan design premium"""
    return render(request, 'booking/home.html')

def test_face(request):
    """Halaman test Face++ API"""
    return render(request, 'test_face.html')

# ===== TAMBAH @login_required PADA BOOKING FORM =====
@login_required
def booking_form(request):
    """Form tempahan gunting rambut dengan rating barber - WAJIB LOGIN"""
    barbers = Barber.objects.filter(is_active=True)
    hairstyles = Hairstyle.objects.all()
    
    for barber in barbers:
        feedbacks = Feedback.objects.filter(barber=barber)
        avg = feedbacks.aggregate(Avg('rating'))['rating__avg']
        barber.avg_rating = avg if avg else 5.0
        barber.review_count = feedbacks.count()
    
    return render(request, 'booking/booking_form.html', {
        'barbers': barbers,
        'hairstyles': hairstyles
    })

def check_availability(date, time, barber_id):
    """Check if slot sudah dibooking"""
    return Appointment.objects.filter(
        date=date,
        time=time,
        barber_id=barber_id,
        status__in=['pending', 'confirmed']
    ).exists()

# ===== UPDATE BOOKING_SUBMIT - TERUS SAVE KALAU USER DAH LOGIN =====
def booking_submit(request):
    """Proses tempahan - kalau user dah login, terus simpan. Kalau tak, simpan dalam session"""
    if request.method == 'POST':
        booking_data = {
            'name': request.POST.get('name'),
            'phone': request.POST.get('phone'),
            'date': request.POST.get('date'),
            'time': request.POST.get('time'),
            'barber_id': request.POST.get('barber_id'),
            'hairstyle_id': request.POST.get('hairstyle_id'),
            'face_shape': request.POST.get('face_shape'),
        }
        
        # ===== KALAU USER DAH LOGIN, TERUS SAVE! =====
        if request.user.is_authenticated:
            # CHECK AVAILABILITY!
            if check_availability(
                booking_data['date'], 
                booking_data['time'], 
                booking_data['barber_id']
            ):
                return render(request, 'booking/error.html', {
                    'error_message': 'Maaf, slot ini sudah dibooking. Sila pilih masa lain.',
                    'back_url': '/booking/'
                })
            
            # Simpan ke database terus
            appointment = Appointment(
                customer_name=booking_data['name'],
                customer_phone=booking_data['phone'],
                date=booking_data['date'],
                time=booking_data['time'],
                barber_id=booking_data['barber_id'],
                hairstyle_id=booking_data['hairstyle_id'],
                face_shape_detected=booking_data['face_shape'],
                customer=request.user,
                status='pending'
            )
            appointment.save()
            
            return render(request, 'booking/success.html', {
                'appointment': appointment
            })
        else:
            # ===== USER TAK LOGIN - SIMPAN DALAM SESSION =====
            request.session['pending_booking'] = booking_data
            return redirect('/accounts/login/?next=/booking/confirm/')
    
    return redirect('/booking/')

@login_required
def booking_confirm(request):
    """Confirm booking lepas user login (untuk user yang sebelum ni tak login)"""
    booking_data = request.session.get('pending_booking')
    
    if not booking_data:
        return redirect('/booking/')
    
    if check_availability(
        booking_data['date'], 
        booking_data['time'], 
        booking_data['barber_id']
    ):
        return render(request, 'booking/error.html', {
            'error_message': 'Maaf, slot ini sudah dibooking. Sila pilih masa lain.',
            'back_url': '/booking/'
        })
    
    appointment = Appointment(
        customer_name=booking_data['name'],
        customer_phone=booking_data['phone'],
        date=booking_data['date'],
        time=booking_data['time'],
        barber_id=booking_data['barber_id'],
        hairstyle_id=booking_data['hairstyle_id'],
        face_shape_detected=booking_data['face_shape'],
        customer=request.user,
        status='pending'
    )
    appointment.save()
    
    del request.session['pending_booking']
    
    return render(request, 'booking/success.html', {
        'appointment': appointment
    })

# ===== FUNCTION FOR SLOT AVAILABILITY =====
@csrf_exempt
def get_available_slots(request):
    """API untuk dapatkan masa yang available"""
    if request.method == 'GET':
        date = request.GET.get('date')
        barber_id = request.GET.get('barber_id')
        
        if not date or not barber_id:
            return JsonResponse({'error': 'Missing parameters'}, status=400)
        
        all_slots = [
            '09:00', '10:00', '11:00', '12:00',
            '14:00', '15:00', '16:00', '17:00'
        ]
        
        booked_slots = Appointment.objects.filter(
            date=date,
            barber_id=barber_id,
            status__in=['pending', 'confirmed']
        ).values_list('time', flat=True)
        
        booked_slots = [t.strftime('%H:%M') if hasattr(t, 'strftime') else str(t) for t in booked_slots]
        available_slots = [slot for slot in all_slots if slot not in booked_slots]
        
        return JsonResponse({
            'date': date,
            'barber_id': barber_id,
            'all_slots': all_slots,
            'booked_slots': booked_slots,
            'available_slots': available_slots
        })
    
    return JsonResponse({'error': 'Invalid method'}, status=405)

def feedback_form(request, appointment_id):
    """Form untuk customer bagi feedback"""
    appointment = get_object_or_404(Appointment, id=appointment_id, status='completed')
    
    try:
        existing_feedback = Feedback.objects.get(appointment=appointment)
        return render(request, 'booking/feedback_form.html', {
            'submitted': True,
            'feedback': existing_feedback
        })
    except Feedback.DoesNotExist:
        pass
    
    if request.method == 'POST':
        rating = request.POST.get('rating', 5)
        comment = request.POST.get('comment', '')
        
        feedback = Feedback.objects.create(
            appointment=appointment,
            barber=appointment.barber,
            customer_name=appointment.customer_name,
            rating=rating,
            comment=comment
        )
        
        return render(request, 'booking/feedback_form.html', {
            'submitted': True,
            'feedback': feedback
        })
    
    return render(request, 'booking/feedback_form.html', {
        'appointment': appointment,
        'submitted': False
    })

def barber_reviews(request, barber_id):
    """Tunjuk semua feedback untuk barber tertentu"""
    barber = get_object_or_404(Barber, id=barber_id)
    feedbacks = Feedback.objects.filter(barber=barber).order_by('-created_at')
    
    avg_rating = 0
    if feedbacks.exists():
        avg_rating = sum(f.rating for f in feedbacks) / feedbacks.count()
    
    return render(request, 'booking/barber_reviews.html', {
        'barber': barber,
        'feedbacks': feedbacks,
        'avg_rating': avg_rating,
        'total_reviews': feedbacks.count()
    })