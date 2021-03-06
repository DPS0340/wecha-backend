import jwt
import re

from django.http     import JsonResponse

from config.settings import SECRET_KEY
from user.models     import User
from wecha_settings  import TOKEN_ALGORITHM

def password_validation(password):
    # 문자 최소 1개 포함, 숫자 최소 1개 포함, 특수문자 최소 1개 포함, 비밀번호 최소 6자리 이상
    validation_re = re.compile(r'^(?=.*[a-zA-Z])(?=.*[0-9])(?=.*[~!@#$%^&*]).{6,}')
    return validation_re.match(password)

def token_authorization(func):
    def wrapper(self, request, *args, **kwargs) :
        try:
            token        = request.headers.get('Authorization', None)         
            payload      = jwt.decode(token, SECRET_KEY, algorithm=TOKEN_ALGORITHM)  
            user_info    = User.objects.get(id=payload['user_id'])
            request.user = user_info # user 정보를 request에 저장하여 이후 활용

        except jwt.exceptions.DecodeError: #토큰이 없거나 토큰 형태가 유효하지 않는 경우                                    
            request.user = None
        except User.DoesNotExist:          # 해당 토큰에 대한 유저정보가 없는 경우
            request.user = None

        return func(self, request, *args, **kwargs)

    return wrapper 