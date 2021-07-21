import json

from django.db.models       import Q, Prefetch
from django.core.cache      import cache
from django.core.exceptions import ObjectDoesNotExist, ValidationError

from datetime       import datetime
from .models        import Category, Subcategory, Product, Like
from users.models   import User, Host

from django.test    import TestCase
from django.test    import Client
from unittest.mock  import patch, MagicMock

class ProductsTest(TestCase):
    def setUp(self):
        User.objects.create(
            id       = 1,
            kakao_id = 1234
        )
        Host.objects.create(
            id       = 1,
            user     = User.objects.get(id=1),
            nickname = 'host'
        )
        Category.objects.create(
            id   = 1,
            name = '여행'
        )
        Subcategory.objects.create(
            id       = 1,
            category = Category.objects.get(id=1),
            name     = '캠핑'
        )
        Product.objects.create(
            id             = 1,
            subcategory    = Subcategory.objects.get(id=1),
            host           = Host.objects.get(id=1),
            title          = '상품',
            region         = '서울',
            price          = 1000,
            is_group       = 'True',
            background_url = 'www.test.com'
        )
        Like.objects.create(
            id      = 1,
            user    = User.objects.get(id=1),
            product = Product.objects.get(id=1),
            like    = 'True'
        )

    def tearDown(self):
        User.objects.all().delete()
        Host.objects.all().delete()
        Category.objects.all().delete()
        Subcategory.objects.all().delete()
        Product.objects.all().delete()
        Like.objects.all().delete()

    def test_products_category_get(self):
        client = Client()
        response = client.get('/products/public?category=1&subcategory=1', content_type = 'application/json')
        self.assertEqual(response.json(),{
            'message' : [{
                "id"        : 1,
                "title"     : "상품",
                "price"     : "1000.00",
                "region"    : "서울",
                "is_group"  : True,
                "bgimg"     : "www.test.com",
                "userImg"   : "",
                "name"      : None,
                "nick"      : "host",
                "like_count": 1
            }]
        })
        self.assertEqual(response.status_code, 200)

    def test_products_total_get(self):
        client = Client()
        response = client.get('/products/public', content_type = 'application/json')
        self.assertEqual(response.json(),{
            'message' : [{
                "id"        : 1,
                "title"     : "상품",
                "price"     : "1000.00",
                "region"    : "서울",
                "is_group"  : True,
                "bgimg"     : "www.test.com",
                "userImg"   : "",
                "name"      : None,
                "nick"      : "host",
                "like_count": 1
            }]
        })
        self.assertEqual(response.status_code, 200)

    def test_create_like_post_success(self):
        client = Client()
        like = {
            "productID": 1,
            "like"     : "True"
        }	
        response = client.post('/products/private', json.dumps(like), content_type='application/json')
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.json(), 
            {
                'message' : 'SUCCESS'
            })

    def test_create_like_post_model_error(self):
        client = Client()
        like = {
            "productID": 100,
            "like"     : "True"
        }	
        response = client.post('/products/private', json.dumps(like), content_type='application/json')
        self.assertEqual(response.status_code, 400)
        self.assertEqual(response.json(), 
            {
                'message' : 'MODEL_ERROR'
            })

    def test_create_like_post_validation_error(self):
        client = Client()
        like = {
            "productID": 1,
            "like"     : "e"
        }	
        response = client.post('/products/private', json.dumps(like), content_type='application/json')
        self.assertEqual(response.status_code, 400)
        self.assertEqual(response.json(), 
            {
                'message' : 'VALIDATION_ERROR'
            })

    def test_products_detail_get(self):
        client = Client()
        response = client.get('/products/private/1', content_type = 'application/json')
        self.assertEqual(response.json(),{
            'message' : [{
                "id"      : 1,
                "title"   : "상품",
                "price"   : "1000.00",
                "region"  : "서울",
                "is_group": True,
                "bgimg"   : "www.test.com",
                "userImg" : "",
                "name"    : None,
                "nick"    : "host",
                'like'    : True
            }]
        })
        self.assertEqual(response.status_code, 200)