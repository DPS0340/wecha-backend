import jwt
from functools     import wraps

from django.http     import JsonResponse

from config.settings import SECRET_KEY
from user.models     import User
from wecha_settings  import TOKEN_ALGORITHM


def password_validation(password):
    # 비밀번호 최소 6자리 이상
    if len(password) <6 :
        return False

    # 숫자 최소 1개 포함
    if not any([char.isdigit() for char in password]):
        return False
    
    # 문자 최소 1개 포함
    if not any([char.isalpha() for char in password]):
        return False
    
    # 특수문자 최소 1개 포함
    symbols = ['~','!','@','#','$','%','^','&','*','(',')','-','+','_','=']
    if not any([char in symbols for char in password]):
        return False

    return True


def token_authorization(func):
    def wrapper(self, request, *args, **kwargs) :
        try:
            token = request.headers.get('Authorization', None)          
            payload = jwt.decode(token, SECRET_KEY, algorithm=TOKEN_ALGORITHM)  
            user_info = User.objects.get(email=payload['user_email'])                 
            request.user = user_info # user 정보를 request에 저장하여 이후 활용

        except jwt.exceptions.DecodeError:                                     
            return JsonResponse({'message' : 'INVALID_TOKEN' }, status=400)

        except User.DoesNotExist:                                           
            return JsonResponse({'message' : 'INVALID_USER'}, status=400)
        return func(self, request, *args, **kwargs)

    return wrapper 


