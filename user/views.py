import json
import bcrypt
import jwt

from json                   import JSONDecodeError

from django.http            import JsonResponse
from django.views           import View
from django.core.exceptions import ObjectDoesNotExist

from .utils                 import password_validation, token_authorization
from .models                import  User
from config.settings        import SECRET_KEY
from wecha_settings         import TOKEN_ALGORITHM

class EmaliDuplicationCheck(View):
    def post(self, request):
        try:
            data = json.loads(request.body)
        except JSONDecodeError:
            return JsonResponse({"message":"JSONDecodeError"}, status=401)
            
        for key in data:
            if key == 'email':
                break
            else:
                return JsonResponse({"message": "KEY_ERROR"}, status=401)
        
        email = data['email']

        cnt = User.objects.filter(email=email).count()
        if cnt == 0: # no duplication
            return JsonResponse( {"message": "SUCCESS"}, status=200)
        else:
            return JsonResponse( {"message": "DUPLICATE_EMAIL_ERROR"}, status=401)

class SignUp(View):
    def post(self, request):
        try:
            data = json.loads(request.body)
        except JSONDecodeError:
            return JsonResponse({"message":"JSONDecodeError"}, status=401)
            
        key_chk = 0
        for key in data:
            if key == 'email' or key =='password' or key == 'name':
                key_chk+=1
        if key_chk < 3:
            return JsonResponse({"message": "KEY_ERROR"}, status=401)
        
        signup_email = data['email'] 
        signup_pw = data['password']
        signup_name = data['name']

        # password validation
        if not password_validation(signup_pw):
            return JsonResponse({"message": "PASSWORD_VALIDATION_ERROR"}, status=401)

        # 비밀번호 암호화
        encrypted_pw = bcrypt.hashpw(signup_pw.encode('utf-8'), bcrypt.gensalt())

        # 기본 유저 프로필 사진
        default_image = 'https://d3sz5r0rl9fxuc.cloudfront.net/assets/default/user/photo_file_name_small-bc8b334acec6a4e386249dedf9e763b5e6aff523fa85cc29211f22e6bed540df.jpg'

        # 회원가입이 성공하면 {"message": "SUCCESS"}, status code 200을 반환합니다.
        User(
            email = signup_email,
            password = encrypted_pw.decode('utf-8'),
            name = signup_name,
            face_image_url = default_image
        ).save()
      
        return JsonResponse({'message':'SUCCESS'}, status=200)


class SignIn(View):
    def post(self, request):
        try:
            data = json.loads(request.body)
        except JSONDecodeError:
            return JsonResponse({"message":"JSONDecodeError"}, status=401)
            
        key_chk = 0
        for key in data:
            if key == 'email' or key =='password' :
                key_chk+=1
        if key_chk < 2:
            return JsonResponse({"message": "KEY_ERROR"}, status=401)
        
        signin_email = data['email'] 
        signin_pw = data['password']


         # 계정이 존재하지 않을 때, {"message": "INVALID_USER"}, status code 401을 반환
        try:
            user_info = User.objects.get(email=signin_email)
        except ObjectDoesNotExist: 
            return JsonResponse( {"message": "INVALID_USER"}, status=401)
        
        # 로그인이 성공하면 토큰발행, status code 200을 반환
        if  bcrypt.checkpw(signin_pw.encode('utf-8'), user_info.password.encode('utf-8')):
            token = jwt.encode({'user_email': user_info.email}, SECRET_KEY, algorithm=TOKEN_ALGORITHM)
            return JsonResponse({'access_token':token.decode('utf-8')}, status = 200)
        else: #비밀번호가 맞지 않을 때, {"message": "WRONG_PASSWORD"}, status code 401을 반환
            return JsonResponse({"message": "WRONG_PASSWORD"}, status=401)
