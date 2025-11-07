# apps/users/views.py
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt

@csrf_exempt
def login_view(request):
    if request.method == 'POST':
        return JsonResponse({"message": "로그인 요청을 받았습니다."})
    return JsonResponse({"detail": "로그인 API 입니다. POST로 email, password를 보내세요."})
