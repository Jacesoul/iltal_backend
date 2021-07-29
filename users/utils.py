import jwt

from django.http    import JsonResponse

from users.models   import User
from my_settings    import SECRET_KEY, ALGORITHM

def user_validator(function):
    def wrapper(self, request, *args, **kwargs):
        try:

            access_token = request.headers.get('Authorization', None)
            
            if not access_token:
                return JsonResponse({"message": "NEED_ACCESS_TOKEN"}, status=401)
            
            payload = jwt.decode(access_token, SECRET_KEY, ALGORITHM)
            
            if not User.objects.filter(id=payload["user_id"]).exists():
                request.user = None
                return function(self, request, *args, **kwargs)

            request.user = User.objects.get(id=payload["user_id"])
            
            return function(self, request, *args, **kwargs)

        except jwt.DecodeError:
            return JsonResponse({"message": "INVALID_TOKEN"}, status=401)

        except jwt.ExpiredSignatureError:
            return JsonResponse({"message": "EXPIRED_TOKEN"}, status=401)

        except User.DoesNotExist:
            return JsonResponse({"message": "INVALID_USER"}, status=401)

    return wrapper