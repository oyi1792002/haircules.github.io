import os
import uuid
import json
import requests
import base64
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt

# ⚠️ TAMPAL GEMINI API KEY ANDA!
GEMINI_API_KEY = 'AIzaSyAcCReIQGejMPSwT-989-4lEbPXqDFuknM'

def analyze_face_with_gemini(image_path):
    """Guna Gemini API terus untuk analyze face"""
    
    # Baca dan encode gambar ke base64
    with open(image_path, 'rb') as f:
        image_data = base64.b64encode(f.read()).decode('utf-8')
    
    # Gemini API endpoint
    url = f"https://generativelanguage.googleapis.com/v1/models/gemini-pro-vision:generateContent?key={GEMINI_API_KEY}"
    
    # Request payload
    payload = {
        "contents": [
            {
                "parts": [
                    {
                        "text": """Analyze this face photo and return ONLY JSON:
{
    "face_shape": "Oval/Round/Square/Long/Heart",
    "gender": "Male/Female",
    "age": 25
}
Face shape must be ONE of: Oval, Round, Square, Long, Heart"""
                    },
                    {
                        "inline_data": {
                            "mime_type": "image/jpeg",
                            "data": image_data
                        }
                    }
                ]
            }
        ]
    }
    
    try:
        response = requests.post(url, json=payload)
        result = response.json()
        
        print("Gemini Response:", json.dumps(result, indent=2))
        
        # Extract text dari response
        if 'candidates' in result and len(result['candidates']) > 0:
            text = result['candidates'][0]['content']['parts'][0]['text']
            
            # Clean JSON
            text = text.strip()
            if '```json' in text:
                text = text.split('```json')[1].split('```')[0]
            elif '```' in text:
                text = text.split('```')[1].split('```')[0]
            
            # Parse JSON
            face_data = json.loads(text)
            
            return {
                'success': True,
                'face_shape': face_data.get('face_shape', 'Oval'),
                'gender': face_data.get('gender', 'Unknown'),
                'age': face_data.get('age', 25),
                'confidence': 85
            }
        else:
            return {'success': False, 'error': 'No face detected'}
            
    except Exception as e:
        print("Error:", str(e))
        return {'success': False, 'error': str(e)}

@csrf_exempt
def analyze_face(request):
    """API endpoint untuk analyze gambar"""
    if request.method == 'POST' and request.FILES.get('photo'):
        photo = request.FILES['photo']
        
        # Buat folder temp
        temp_dir = 'media/temp/'
        os.makedirs(temp_dir, exist_ok=True)
        
        # Save gambar
        temp_path = os.path.join(temp_dir, f"{uuid.uuid4()}.jpg")
        with open(temp_path, 'wb+') as f:
            for chunk in photo.chunks():
                f.write(chunk)
        
        # Analyze dengan Gemini
        result = analyze_face_with_gemini(temp_path)
        
        # Delete temp file
        os.remove(temp_path)
        
        if result['success']:
            return JsonResponse({
                'status': 'success',
                'face_shape': result['face_shape'],
                'gender': result['gender'],
                'age': result['age'],
                'confidence': result['confidence']
            })
        else:
            return JsonResponse({
                'status': 'error',
                'message': result.get('error', 'Cannot analyze face')
            })
    
    return JsonResponse({
        'status': 'error', 
        'message': 'Sila upload gambar dengan POST method'
    })