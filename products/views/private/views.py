import json, uuid

from django.http            import JsonResponse
from django.views           import View
from django.db.models       import Q, Prefetch
from django.core.cache      import cache
from django.core.exceptions import ObjectDoesNotExist, ValidationError

from datetime               import datetime
from products.models        import Category, Subcategory, Product, Like
from users.models           import User, Host
from core.views             import query_debugger, confirm_user, upload_data

class PrivateProductsView(View):
    @confirm_user
    def get(self, request):
        try: 
            user        = request.user
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

            products = Product.objects.select_related('host','host__user').prefetch_related(
                Prefetch('likes',queryset=Like.objects.filter(like=True), to_attr='total_likes'),
                Prefetch('likes',queryset=Like.objects.filter(user=user), to_attr='filtered_likes')
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
                'like'      : product.likes.get(user=user).like if len(product.filtered_likes) != 0 else False,
                'like_count': len(product.total_likes)
            } for product in products]

            return JsonResponse({"message":results},status=200)
        except TypeError:
            return JsonResponse({"message":"TYPE_ERROR"},status=400)
        except ValueError:
            return JsonResponse({"message":"VALUE_ERROR"},status=400)

    @confirm_user
    def post(self, request):
        try: 
            data    = json.loads(request.body)
            user    = request.user
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

class PrivateProductDetailView(View): 
    @confirm_user
    def get(self, request, product_id):
        try:
            user     = request.user
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

    @confirm_user
    def post(self, request, product_id):
        try: 
            data    = json.loads(request.body)
            user    = request.user
            product = Product.objects.get(id=product_id)    
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

class HostProductView(View):
    def post(self, request):
        try:
            print(request.FILES.get('background_url'))
            Product.objects.create (
                title           =  request.POST.get('title'),
                region          =  request.POST.get('region'),
                price           =  request.POST.get('price'),
                is_group        =  request.POST.get('is_group'),
                background_url  =  upload_data(request.FILES.get('background_url')),
                is_deleted      =  False,
                host_id         =  request.POST.get('host_id'),
                subcategory_id  =  request.POST.get('subcategory_id')
            )    
            return JsonResponse({'MESSAGE':'SUCCESS'}, status=201)    
        except KeyError:
            return JsonResponse({"MESSAGE": "KEY_ERROR"}, status=404)
        except Product.DoesNotExist:
            return JsonResponse({"MESSAGE": "INVALID_USER"}, status=404)
        except KeyError:
            return JsonResponse({"MESSAGE": "KEY_ERROR"}, status=404)
