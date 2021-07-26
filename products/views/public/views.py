import json

from django.http            import JsonResponse
from django.views           import View
from django.db.models       import Q, Prefetch
from django.core.cache      import cache
from django.core.exceptions import ObjectDoesNotExist, ValidationError

from datetime               import datetime
from products.models        import Category, Subcategory, Product, Like
from users.models           import User, Host
from core.views             import query_debugger, confirm_user

class PublicProductsView(View):
    def get(self, request):
        try: 
            category    = request.GET.get('category',None)
            subcategory = request.GET.get('subcategory',None)
            region      = request.GET.get('region',None)
            group       = request.GET.get('group',None)
            ordering    = request.GET.get('ordering','?')

            q_object = Q() 

            if category: 
                q_object &= Q(subcategory__category=category)
            if subcategory: 
                q_object &= Q(subcategory_id=subcategory)
            if region:
                q_object &= Q(region=region)
            if group:
                q_object &= Q(is_group=group)

            products = Product.objects.select_related('host','host__user').prefetch_related(Prefetch('likes',queryset=Like.objects.all())).filter(q_object).order_by(ordering)

            results = [{
                'id'        : product.id,
                'title'     : product.title,
                'price'     : product.price,
                'region'    : product.region,
                'is_group'  : product.is_group,
                'bgimg'     : product.background_url,
                'userImg'   : product.host.profile_url,
                'name'      : product.host.user.name,
                'nick'      : product.host.nickname,
                'like_count': product.likes.all().count()
            } for product in products]

            return JsonResponse({"message":results},status=200)
        except TypeError:
            return JsonResponse({"message":"TYPE_ERROR"},status=400)
        except ValueError:
            return JsonResponse({"message":"VALUE_ERROR"},status=400)

class PublicProductDetailView(View): 
    def get(self, request, product_id):
        try:
            product = Product.objects.select_related('host','host__user').get(id=product_id)
            results = [{
                'id'      : product.id,
                'title'   : product.title,
                'price'   : product.price,
                'region'  : product.region,
                'is_group': product.is_group,
                'bgimg'   : product.background_url,
                'userImg' : product.host.profile_url,
                'name'    : product.host.user.name,
                'nick'    : product.host.nickname,
            }]
            
            return JsonResponse({"message":results},status=200)
        except TypeError:
            return JsonResponse({"message":"TYPE_ERROR"},status=400)
        except Product.DoesNotExist:
            return JsonResponse({"message":"INVAILD_PRODUCT"},status=400)
        except ValueError:
            return JsonResponse({"message":"VALUE_ERROR"},status=400)