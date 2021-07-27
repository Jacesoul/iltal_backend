from django.db              import models
from django.core.cache      import cache


from users.models import User, Host
from core.models import TimeStampModel

class Category(TimeStampModel): 
    name = models.CharField(max_length=200)

    class Meta: 
        db_table = 'categories'

class Subcategory(TimeStampModel): 
    category = models.ForeignKey(Category, on_delete=models.CASCADE, related_name='sub_categories')
    name     = models.CharField(max_length=200)

    class Meta: 
        db_table = 'subcategories'

class Product(TimeStampModel):
    subcategory    = models.ForeignKey(Subcategory, on_delete=models.CASCADE, related_name='products')
    host           = models.ForeignKey(Host, on_delete=models.CASCADE)
    title          = models.CharField(max_length=200)
    region         = models.CharField(max_length=200)
    price          = models.DecimalField(decimal_places=2, max_digits=10)
    is_group       = models.BooleanField()
    background_url = models.CharField(max_length=2000)
    is_deleted     = models.BooleanField(default=False)
    user           = models.ManyToManyField(User, through='Like')

    class Meta: 
        db_table = 'products'

class Like(TimeStampModel):
    user    = models.ForeignKey(User,on_delete=models.CASCADE)
    product = models.ForeignKey(Product, on_delete=models.CASCADE, related_name='likes')
    like    = models.BooleanField(default=False)

    class Meta:
        db_table = 'likes'