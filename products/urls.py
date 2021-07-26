from django.urls    import path

from products.views.public.views  import PublicProductsView, PublicProductDetailView
from products.views.private.views import PrivateProductsView, PrivateProductDetailView, HostProductView

urlpatterns = [
    path('/public', PublicProductsView.as_view()),
    path('/private', PrivateProductsView.as_view()),
    path('/public/<int:product_id>', PublicProductDetailView.as_view()),
    path('/private/<int:product_id>', PrivateProductDetailView.as_view()),
    path('/private/host', HostProductView.as_view())
]