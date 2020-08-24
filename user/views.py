import json
import bcrypt
import jwt

from json                   import JSONDecodeError

from django.http            import JsonResponse
from django.views           import View

from .utils                 import password_validation, token_authorization
from .models                import User
from config.settings        import SECRET_KEY
from wecha_settings         import TOKEN_ALGORITHM


class SignUp(View):
    def post(self, request):
        try:
            data = json.loads(request.body)
            signup_email = data['email'] 
            signup_pw    = data['password']
            signup_name  = data['name']

            # duplicate email validation
            if User.objects.filter(email=signup_email).exists() : # duplicate email exists
                return JsonResponse( {"message": "DUPLICATE_EMAIL_ERROR"}, status=401)

            #password validation
            if not password_validation(signup_pw):
                return JsonResponse({"message": "PASSWORD_VALIDATION_ERROR"}, status=401)

            # 비밀번호 암호화
            encrypted_pw = bcrypt.hashpw(signup_pw.encode('utf-8'), bcrypt.gensalt())

            # 기본 유저 프로필 사진
            default_image = 'https://d3sz5r0rl9fxuc.cloudfront.net/assets/default/user/photo_file_name_small-bc8b334acec6a4e386249dedf9e763b5e6aff523fa85cc29211f22e6bed540df.jpg'

            # 회원가입이 성공하면 {"message": "SUCCESS"}, status code 200을 반환합니다.
            User(
                email          = signup_email,
                password       = encrypted_pw.decode('utf-8'),
                name           = signup_name,
                face_image_url = default_image
            ).save()
      
            return JsonResponse({'message':'SUCCESS'}, status=200)

        except JSONDecodeError:
            return JsonResponse({"message":"JSONDecodeError"}, status=401)
        except KeyError:
            return JsonResponse({"message": "KEY_ERROR"}, status=401)

class SignIn(View):
    def post(self, request):
        try:
            data = json.loads(request.body)
            signin_email = data['email'] 
            signin_pw    = data['password']

            # 계정이 존재하지 않을 때, {"message": "INVALID_USER"}, status code 401을 반환
            if not User.objects.filter(email=signin_email).exists():
                return JsonResponse(  {"message": "INVALID_USER"}, status=401)
        
            user_info = User.objects.get(email=signin_email)
        
            # 로그인이 성공하면 토큰발행, status code 200을 반환
            if  bcrypt.checkpw(signin_pw.encode('utf-8'), user_info.password.encode('utf-8')):
                token = jwt.encode({'user_id': user_info.id}, SECRET_KEY, algorithm=TOKEN_ALGORITHM)
                token_decode = token.decode('utf-8')
                return JsonResponse({"access_token":token_decode}, status = 200)

            #비밀번호가 맞지 않을 때, {"message": "WRONG_PASSWORD"}, status code 401을 반환
            return JsonResponse({"message": "WRONG_PASSWORD"}, status=401)

        except JSONDecodeError:
            return JsonResponse({"message":"JSONDecodeError"}, status=401)
        except KeyError:
            return JsonResponse({"message": "KEY_ERROR"}, status=400)