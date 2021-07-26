import functools, time, jwt

from django.db   import connection, reset_queries
from django.conf import settings
from django.http import JsonResponse

from my_settings  import SECRET_KEY, ALGORITHM
from users.models import User 

def query_debugger(func):
    @functools.wraps(func)
    def wrapper(*args, **kwargs):
        reset_queries()
        number_of_start_queries = len(connection.queries)
        start  = time.perf_counter()
        result = func(*args, **kwargs)
        end    = time.perf_counter()
        number_of_end_queries = len(connection.queries)
        print(f"-------------------------------------------------------------------")
        print(f"Function : {func.__name__}")
        print(f"Number of Queries : {number_of_end_queries-number_of_start_queries}")
        print(f"Finished in : {(end - start):.2f}s")
        print(f"-------------------------------------------------------------------")
        return result
    return wrapper

def confirm_user(func):
    def wrapper(self, request, *args, **kwargs):
        try:
            if request.headers.get('Authorization',None):
                payload      = jwt.decode(request.headers.get('Authorization'), SECRET_KEY, ALGORITHM)
                user         = User.objects.get(id = payload['id'])
                request.user = user
            else: 
                request.user = None
                # request.user = User.objects.get(id=1)
            return func(self, request, *args, **kwargs)
        except jwt.DecodeError:
            return JsonResponse({'message': 'INVAILD_USER'}, status=400)

    return wrapper