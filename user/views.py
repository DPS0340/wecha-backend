import json
import bcrypt
import jwt

from json                   import JSONDecodeError

from django.http            import JsonResponse
from django.views           import View

from .utils                 import password_validation, token_authorization
from film.models            import Film
from .models                import User, Review, ReviewType
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
            default_image = 'https://ca.slack-edge.com/TH0U6FBTN-U014K5JLSQP-3fa65eb31d7f-512'

            # 회원가입이 성공하면 {"message": "SUCCESS"}, status code 200을 반환합니다.
            User(
                email          = signup_email,
                password       = encrypted_pw.decode('utf-8'),
                name           = signup_name,
                face_image_url = default_image
            ).save()
      
            return JsonResponse({'message':'SIGNUP_SUCCESS'}, status=200)

        except JSONDecodeError:
            return JsonResponse({"message":"JSONDecodeError"}, status=401)
        except KeyError:
            return JsonResponse({"message": "KEY_ERROR"}, status=401)

class SignIn(View):
    def post(self, request):
        try:
            data         = json.loads(request.body)
            signin_email = data['email'] 
            signin_pw    = data['password']

            # 계정이 존재하지 않을 때, {"message": "INVALID_USER"}, status code 401을 반환
            if not User.objects.filter(email=signin_email).exists():
                return JsonResponse(  {"message": "INVALID_USER"}, status=401)
        
            user_info = User.objects.get(email=signin_email)
        
            # 로그인이 성공하면 토큰발행, status code 200을 반환
            if  bcrypt.checkpw(signin_pw.encode('utf-8'), user_info.password.encode('utf-8')):
                token        = jwt.encode({'user_id': user_info.id}, SECRET_KEY, algorithm=TOKEN_ALGORITHM)
                token_decode = token.decode('utf-8')
                return JsonResponse({"access_token":token_decode, "profile_url":user_info.face_image_url}, status = 200)

            #비밀번호가 맞지 않을 때, {"message": "WRONG_PASSWORD"}, status code 401을 반환
            return JsonResponse({"message": "WRONG_PASSWORD"}, status=401)

        except JSONDecodeError:
            return JsonResponse({"message":"JSONDecodeError"}, status=401)
        except KeyError:
            return JsonResponse({"message": "KEY_ERROR"}, status=401)

class HandleReview(View):
    @token_authorization
    def post(self,request): # 리뷰 등록, 수정
        try:
            data             = json.loads(request.body)
            film_id          = data['film_id']
            film_info        = Film.objects.get(id=film_id)
            review_text      = data['review_text']
            review_rating    = data['review_rating']
            review_type      = data['review_type'] # 'R' : rated, 'W' " wish", 'M' : middle of wathcing
            review_type_info = ReviewType.objects.get(name = review_type)
            user_info        = request.user            
            if not user_info: # 유저 정보가 없는 경우
                return JsonResponse({"message": "INVALIDE_USER"}, status=400) 

            already_posted_review = Review.objects.filter(film = film_info).filter(user = user_info)
     
            if already_posted_review.exists(): # 리뷰수정
                posted_review             = already_posted_review.get()
                posted_review.score       = review_rating
                posted_review.comment     = review_text
                posted_review.review_type = review_type_info
                posted_review.save()

            else: # 리뷰등록
                Review(
                    score       = review_rating,
                    comment     = review_text,
                    review_type = review_type_info,
                    film        = film_info,
                    user        = user_info
                ).save()

            # 해당 영화의 평균별점 재계산
            review_set        = Review.objects.filter(film = film_info)
            review_set_number = review_set.count()
            total_rating      = 0

            for review_element in review_set:
                total_rating += review_element.score

            film_info.avg_rating = total_rating / review_set_number
            film_info.save()

            return JsonResponse({"message":"POST_REVIEW_SUCCESS"}, status=200)

        except JSONDecodeError:
            return JsonResponse({"message":"JSONDecodeError"}, status=400)
        except KeyError:
            return JsonResponse({"message": "KEY_ERROR"}, status=400)
        except Review.DoesNotExist:
            return JsonResponse({"message":"NOT_EXISTS_REVIEW"}, status=400)


    @token_authorization
    def delete(self,request): # 리뷰 삭제
        try:
            data      = json.loads(request.body)
            film_id   = data['film_id']
            film_info = Film.objects.get(id=film_id)
            user_info = request.user            

            if not user_info: # 유저 정보가 없는 경우
                return JsonResponse({"message": "INVALIDE_USER"}, status=400) 

            Review.objects.get(film = film_info, user = user_info).delete()
            
            # 해당 영화의 평균별점 재계산
            review_set        = Review.objects.filter(film = film_info)
            review_set_number = review_set.count()
            total_rating      = 0

            for review_element in review_set:
                total_rating += review_element.score
            
            if review_set_number == 0:
                film_info.avg_rating = 0
            else:
                film_info.avg_rating = total_rating / review_set_number

            film_info.save()        

            return JsonResponse({"message": "DELETE_REVIEW_SUCCESS"}, status=200)

        except JSONDecodeError:
            return JsonResponse({"message":"JSONDecodeError"}, status=401)
        except KeyError:
            return JsonResponse({"message": "KEY_ERROR"}, status=400)
        except Review.DoesNotExist:
            return JsonResponse({"message":"NOT_EXISTS_REVIEW"}, status=401)

class ReviewCount(View):
    def get(self, request):
        review_count = Review.objects.all().count()
        return JsonResponse({"review_count":review_count}, status=200)

class ReviewLike(View):
    @token_authorization
    def post(self, request):
        try:
            data         = json.loads(request.body)
            comment_id   = data['comment_id']
            commnet_like = data['like_count']

            comment            = Review.objects.get(id= comment_id)
            comment.like_count = commnet_like
            comment.save()

            return JsonResponse({"message": "COMMENT_LIKE_SUCCESS"}, status=200)
            
        except JSONDecodeError:
            return JsonResponse({"message":"JSONDecodeError"}, status=401)
        except KeyError:
            return JsonResponse({"message": "KEY_ERROR"}, status=400)
        except Review.DoesNotExist:
            return JsonResponse({"message":"NOT_EXISTS_REVIEW"}, status=401)

class UserInfo(View):
    @token_authorization
    def get(self, request):
        user_name = request.user.name
        user_profile = request.user.face_image_url
        user_review_films = []

        reviewed_films = Review.objects.filter(user = request.user).select_related('film')[0:10]
        
        for reviewed_film in reviewed_films:
            reviewed_film_info = []
            reviewed_film_info.append(reviewed_film.film.korean_title)
            reviewed_film_info.append(reviewed_film.film.avg_rating)
            reviewed_film_info.append(reviewed_film.film.poster_url)
            user_review_films.append(reviewed_film_info)

        user_info = {
            "user_name":user_name,
            "user_profile": user_profile,
            "user_review_films":user_review_films
        }

        return JsonResponse(user_info, status=200)