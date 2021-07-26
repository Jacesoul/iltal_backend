import json

from django.http            import JsonResponse
from django.views           import View
from django.db.models       import Q, Prefetch
from django.core.cache      import cache
from django.core.exceptions import ObjectDoesNotExist, ValidationError

from datetime       import datetime
from .models        import Category, Subcategory, Product, Like
from users.models   import User, Host
from core.views     import query_debugger, confirm_user

class ProductsView(View):
    @confirm_user
    @query_debugger 
    def get(self, request):
        try: 
            category    = request.GET.get('category',None)
            subcategory = request.GET.get('subcategory',None)
            region      = request.GET.get('region',None)
            group       = request.GET.get('group',None)
            ordering    = request.GET.get('ordering','?')

            q_object = Q() 

            if request.user: 
                if category or subcategory or region or group: 
                    if category: 
                        q_object &= Q(subcategory__category=category)
                    if subcategory: 
                        q_object &= Q(subcategory_id=subcategory)
                    if region:
                        q_object &= Q(region=region)
                    if group:
                        q_object &= Q(is_group=group)

                    products = Product.objects.select_related('host','host__user').prefetch_related(
                        Prefetch('likes',queryset=Like.objects.all(), to_attr='total_likes'),
                        Prefetch('likes',queryset=Like.objects.filter(user=request.user), to_attr='filtered_likes')
                        ).filter(q_object).order_by(ordering)

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
                        'like'      : product.likes.get(user=request.user).like if len(product.filtered_likes) != 0 else False,
                        'like_count': len(product.total_likes)
                    } for product in products]

                elif not cache.get('user_products'):  

                    products = Product.objects.select_related('host','host__user').prefetch_related(
                        Prefetch('likes',queryset=Like.objects.all(), to_attr='total_likes'),
                        Prefetch('likes',queryset=Like.objects.filter(user=request.user), to_attr='filtered_likes')
                        ).all().order_by(ordering)
                    
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
                        'like'      : product.likes.get(user=request.user).like if len(product.filtered_likes) != 0 else False,
                        'like_count': len(product.total_likes)
                    } for product in products]

                    cache.set('user_products',results)
                    results = cache.get('user_products')
                else: 
                    results = cache.get('user_products')

                return JsonResponse({"message":results},status=200)

            else: 
                if category or subcategory or region or group: 
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

                elif not cache.get('products'):                    
                    products = Product.objects.select_related('host','host__user').prefetch_related(Prefetch('likes',queryset=Like.objects.all())).all().order_by(ordering)

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

                    cache.set('products',results)
                    results = cache.get('products')
                else: 
                    results = cache.get('products')

                return JsonResponse({"message":results},status=200)

        except TypeError:
            return JsonResponse({"message":"TYPE_ERROR"},status=400)
        except ValueError:
            return JsonResponse({"message":"VALUE_ERROR"},status=400)

    def post(self, request):
        try: 
            data    = json.loads(request.body)
            # user    = request.user
            user = User.objects.get(id=1)
            product = Product.objects.get(id=data['productID'])    
            Like.objects.update_or_create(user=user, product=product, defaults={'like':data['like']})    
            return JsonResponse({'message' : 'SUCCESS'}, status=200)
        
        except ObjectDoesNotExist:
            return JsonResponse({'message' : 'MODEL_ERROR'}, status=400)
        except KeyError:
            return JsonResponse({'message' : 'KEY_ERROR'}, status=400)
        except ValueError:
            return JsonResponse({'message' : 'VALUE_ERROR'}, status=400)
        except TypeError:
            return JsonResponse({"message":"TYPE_ERROR"},status=400)
        except ValidationError:
            return JsonResponse({"message":"VALIDATION_ERROR"},status=400)
            

class ProductDetailView(View): 
    @query_debugger
    def get(self, request, product_id):
        try:
            user = User.objects.get(id=1)
            products = Product.objects.select_related('host','host__user').prefetch_related(Prefetch('likes',queryset=Like.objects.filter(user=user))).filter(id=product_id)
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
                'like'    : product.likes.get(user=user).like if product.likes.filter(user=user).count() != 0 else False
            }for product in products]
            
            return JsonResponse({"message":results},status=200)
        except TypeError:
            return JsonResponse({"message":"TYPE_ERROR"},status=400)
        except Product.DoesNotExist:
            return JsonResponse({"message":"INVAILD_PRODUCT"},status=400)
        except ValueError:
            return JsonResponse({"message":"VALUE_ERROR"},status=400)