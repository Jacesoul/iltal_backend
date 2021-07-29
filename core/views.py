import functools, time, jwt, boto3, uuid, logging

from django.db   import connection, reset_queries
from django.conf import settings
from django.http import JsonResponse

from iltal.settings  import AWS_ACCESS_KEY_ID,AWS_SECRET_ACCESS_KEY
from logging         import error
from my_settings     import SECRET_KEY, ALGORITHM
from users.models    import User 

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

class AWSAPI:
    def __init__(self, aws_access_key, aws_secret_key, bucket):
        self.bucket = bucket
        self.storage_url = 'https://' + bucket + '.s3.us-east-2.amazonaws.com/'
        self.client = boto3.client(
            's3',
            aws_access_key_id = aws_access_key,
            aws_secret_access_key = aws_secret_key
        )

    def upload_file(self, file):
        try :
            filename = uuid.uuid4().hex
            self.client.upload_fileobj(
                file,
                self.bucket,
                filename,
                ExtraArgs = {
                    "ContentType": file.content_type,
                }
            )

        except Exception as e:
            logging.error(f"message : {e}")

            return JsonResponse({"MESSAGE": "FAIL_TO_UPLOAD"}, status=404)

        return self.storage_url + filename
