from sys                            import path
import json, bcrypt, jwt, requests

from PIL                            import Image
from io                             import BytesIO

from django.views.generic.base      import View
from django.http.response           import HttpResponse
from django.test                    import RequestFactory
from django.core.files.uploadedfile import SimpleUploadedFile
from django.test                    import TestCase, Client, client, utils
from django.http                    import JsonResponse, cookie, response, request

from users.models                   import Host, User
from unittest.mock                  import patch, MagicMock
from my_settings                    import SECRET_KEY, ALGORITHM

class SignupViewTest(TestCase):
    def setUp(self):
        User.objects.create(
            id          = 1,
            email       = "wlgns432@gmail.com",
            password    = "1234asdf!",
            name        = "dmwkdm"
        )

    def test_signupview_post_success(self):
        client = Client()
        user = {
            'email'     : 'wldkwmd122@gmail.com',
            'password'  : 'a123aaaa!',
            'name'      : 'dmwkdm'
        }
        response = client.post('/users/signup', json.dumps(user), content_type='application/json')

        self.assertEqual(response.status_code, 201)
        self.assertEqual(response.json(),
            {
                "MESSAGE" : "SUCCESS"
            }
        )

    def test_signupview_post_invalid_email(self):
        client = Client()
        user = {
            'email'     : 'wwwwwwgmail.com',
            'password'  : 'a123aaaa!',
            'name'      : 'dmwkdm'
        }
        response = client.post('/users/signup', json.dumps(user), content_type='application/json')
        
        self.assertEqual(response.status_code, 400)
        self.assertEqual(response.json(),
            {
                "MESSAGE" : "INVALID EMAIL"
            }
        )

    def test_signupview_post_invalid_password(self):
        client = Client()
        user = {
            'email'     : 'wwwwww@gmail.com',
            'password'  : 'a123aaaa',
            'name'      : 'dmwkdm' 
        }
        response = client.post('/users/signup', json.dumps(user), content_type='application/json')
        
        self.assertEqual(response.status_code, 400)
        self.assertEqual(response.json(),
            {
                "MESSAGE" : "INVALID PASSWORD"
            }
        )

    def test_signupview_post_duplicated_email(self):
        client = Client()
        user = {
            'email'       : "wlgns432@gmail.com",
            'password'    : "1234asdf!",
            'name'        : "dmwkdm"
        }
        response = client.post('/users/signup', json.dumps(user), content_type='application/json')

        self.assertEqual(response.status_code, 400)
        self.assertEqual(response.json(),
            {
                "MESSAGE" : "EXIST EMAIL"
            }
        )

    def test_signupview_post_invalid_keys(self):
        client = Client()
        user = {
            'ddemail'    : 'wlgns432@gmail.com',
            'password'   : '1234asdf!',
            'name'       : 'dmwkdm',
        }
        response = client.post('/users/signup', json.dumps(user), content_type='application/json')
        print(response)
        self.assertEqual(response.status_code, 400)
        self.assertEqual(response.json(),
            {
                "MESSAGE": "KEY_ERROR"
            }
        )

    def tearDown(self):
        User.objects.all().delete()

class SigninViewTest(TestCase):
    def setUp(self):
        password    = 'wlaa1234!'

        User.objects.create(
            id          = 1,
            password    = bcrypt.hashpw(password.encode('utf-8'), bcrypt.gensalt()).decode('utf-8'),
            email       = 'BrendanEich@gmail.com',
            name        = 'gimgimgim'
        )

        access_token= jwt.encode({"user_id": 1}, SECRET_KEY, ALGORITHM)

    def tearDown(self):
         User.objects.all().delete()

    # token 검증
    def test_signinview_post_success(self):

        client = Client()
        user = {
            'email'    : 'BrendanEich@gmail.com',
            'password' : 'wlaa1234!'
        }

        response       = client.post('/users/signin', json.dumps(user), content_type="application/json")
        access_token   = response.json()['access_token']

        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.json(), 
            {
                'message'       : 'success',
                'access_token'  : access_token
            }
        )

    # keyerror
    def test_signinview_post_keyerror(self):

        client = Client()

        user = {
            'password' : 'wlaa1234!'
        }

        response = client.post('/users/signin', json.dumps(user), content_type="application/json")

        self.assertEqual(response.status_code, 400)
        self.assertEqual(response.json(), 
            {
                "message" : "KEY_ERROR"
            }
        )

    # password error
    def test_signinview_post_not_password(self):

        client = Client()

        user = {
            'password'  : 'wlaa1232!',
            'email'     : 'BrendanEich@gmail.com',
        }

        response = client.post('/users/signin', json.dumps(user), content_type="application/json")

        self.assertEqual(response.status_code, 401)
        self.assertEqual(response.json(), 
            {
                "message" : "INVALID_USER"
            }
        )

    # email error
    def test_signinview_post_does_not_existed_email(self):

        client = Client()

        user = {
            'password'  : 'wlaa1234!',
            'email'     : 'Brendah@gmail.com',
        }

        response = client.post('/users/signin', json.dumps(user), content_type="application/json")

        self.assertEqual(response.status_code, 401)
        self.assertEqual(response.json(), 
            {
                "message" : "INVALID_USER"
            }
        )

class KakaoSigninTest(TestCase):
    def setUp(self):
        User.objects.create(
            id              = 1,
            kakao_id        = "1234567899",
            email           = "kakao@kakakak.com",
        )

    def tearDown(self):
        User.objects.all().delete()

    @patch('users.views.requests')
    def test_kakao_signin_success(self, mocked_requests):
        client = Client()

        class MockedResponse:
            def json(self):
                return {
                    'id': "1234567899",
                    'connected_at': '2021-07-26T22:29:32Z',
                    'properties' : {
                        'nickname' : "test",
                        'profile_image' : "http://k.kakaocdn.net/dn/bRMq9X/btq5Q6IaoP7/yYLcgclYwEje2FlgN6uIO1/img_640x640.jpg"
                    }, 
                    'kakao_account': {
                        'has_email'            : True, 
                        'email_needs_agreement': False, 
                        'is_email_valid'       : True, 
                        'is_email_verified'    : True, 
                        'email'                : 'kakao@kakao.com'
                        }
                }

        mocked_requests.get = MagicMock(return_value = MockedResponse())
        headers             = {"Authoriazation":"kakao_token"}
        response            = client.get("/users/kakao/signin", **headers)       
        access_token        = response.json()['TOKEN']
        
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.json(),
            {
                'message'   : 'success',
                'TOKEN'     : access_token
            }
        )

    @patch('users.views.requests')
    def test_kakao_signin_user_success(self, mocked_requests):
        client = Client()

        class MockedResponse:
            def json(self):
                return {
                    'id': "1234567899",
                    'connected_at': '2021-07-26T22:29:32Z',
                    'properties' : {
                        'nickname' : "이이이",
                        'profile_image' : "http://k.kakaocdn.net/dn/bRMq9X/btq5Q6IaoP7/yYLcgclYwEje2FlgN6uIO1/img_640x640.jpg"
                    }, 
                    'kakao_account': {
                        'has_email'            : True, 
                        'email_needs_agreement': False, 
                        'is_email_valid'       : True, 
                        'is_email_verified'    : True, 
                        'email'                : "lee@kakao.com"
                        }
                }

        mocked_requests.get = MagicMock(return_value = MockedResponse())
        headers             = {"Authoriazation":"kakao_token"}
        response            = client.get("/users/kakao/signin", **headers)       
        access_token        = response.json()['TOKEN']
        
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.json(),
            {
                'message'   : 'success',
                'TOKEN'     : access_token
            }
        )

    @patch('users.views.requests')
    def test_kakao_signin_exist_user_success(self, mocked_requests):
        client = Client()

        class MockedResponse:
            def json(self):
                return {
                    'id': "1234567899",
                    'connected_at': '2021-07-26T22:29:32Z',
                    'properties' : {
                        'nickname' : "mumu",
                        'profile_image' : "http://k.kakaocdn.net/dn/bRMq9X/btq5Q6IaoP7/yYLcgclYwEje2FlgN6uIO1/img_640x640.jpg"
                    }, 
                    'kakao_account': {
                        'has_email'            : True, 
                        'email_needs_agreement': False, 
                        'is_email_valid'       : True, 
                        'is_email_verified'    : True, 
                        'email'                : "kakao@kakakak.com"
                        }
                }

        mocked_requests.get = MagicMock(return_value = MockedResponse())
        headers             = {"Authoriazation":"kakao_token"}
        response            = client.get("/users/kakao/signin", **headers)       
        access_token        = response.json()['TOKEN']
        
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.json(),
            {
                'message'   : 'success',
                'TOKEN'     : access_token
            }
        )

class HostTest(TestCase):
    def setUp(self):
        User.objects.create(
            id          = 1,
            kakao_id    = 1,
            name        = 'anhesu',
            profile_url = 'testurl',
            email       ='anhesu1@naver.com',
            password    = bcrypt.hashpw("1234".encode('utf-8'), bcrypt.gensalt()).decode()
        )
        self.client.head

    def test_hostview_get_success(self):
        client = Client()

        Host.objects.create (
            id          = 1,
            nickname    = 'anhesu',
            profile_url = 'testurl',
            user_id     = 1
        )
        user = {'email' : 'anhesu1@naver.com', 'password' : '1234'}

        login_response  = client.post('/users/signin', json.dumps(user), content_type="application/json")
        access_token   = login_response.json()['access_token']
        headers = {"HTTP_Authorization" : access_token}
        response = client.get('/users/host', content_type='application/json', **headers)
        
        self.assertEquals(response.status_code,200)
        self.assertEquals(response.json(),{"id":1,"user_id":1,"nickname":"anhesu","profile_url":"testurl"})
    
    def test_hostview_get_Host_Not_Exists(self):    
        client = Client()
        
        Host.objects.create (
            id          = 1,
            nickname    = 'anhesu',
            profile_url = 'testurl',
            user_id     = 1
        )
        user = {'email' : 'anhesu1@naver.com', 'password' : '12345'}

        access_token   = jwt.encode({"user_id": 2}, SECRET_KEY, ALGORITHM)
        headers = {"HTTP_Authorization" : access_token}
        response = client.get('/users/host', content_type='application/json', **headers)
        
        self.assertEquals(response.status_code,401)
        self.assertEquals(response.json(),{'message': 'INVALID_USER'})
    
    @patch("core.views.AWSAPI.upload_file")
    def test_hostview_post_success(self, mocked_request):
        client = Client()
        mocked_request.return_value = 'sss'

        User.objects.create(
            id          = 2,
            kakao_id    = 1,
            name        = 'anhesu',
            profile_url = 'testurl',
            email       ='anhesu11@naver.com',
            password    = bcrypt.hashpw("12345".encode('utf-8'), bcrypt.gensalt()).decode()
        )
        user = {'email' : 'anhesu11@naver.com', 'password' : '12345'}
        host = {'nickname':'anhesu11', 'profile_url':'test_url2'}
        
        login_response  = client.post('/users/signin', json.dumps(user), content_type="application/json")
        access_token   = login_response.json()['access_token']
        headers = {"HTTP_Authorization" : access_token}

        stream = BytesIO()
        image = Image.new('RGB', (100, 100))
        image.save(stream, format='jpeg')
        image_file  = SimpleUploadedFile("test.jpg", stream.getvalue(), content_type="image/jpg")
        
        response = client.post(
            '/users/host',
            {'background_url' : image_file, "nickname" : "anhesu"},
            format = 'multipart',
            **{'HTTP_Authorization' : access_token }
        )

        self.assertEqual(response.status_code, 201)