from django.urls import path
from . import views
from django.conf import settings
from django.conf.urls.static import static
urlpatterns = [
    path('', views.index, name='index'),
    path('logout', views.logout, name='logout'),
    path('inventory', views.inventory, name='inventory'),
    path('category', views.category, name='category'),
    path('products', views.products, name='products'),
    path('sells', views.sells, name='sells'),
    path('add_products', views.add_products, name='add_products'),
    path('del_category/<int:id>', views.del_category, name='del_category'),
    path('sell_product/<int:id>', views.sell_product, name='sell_product'),
    path('edit_product/<int:id>', views.edit_product, name='edit_product'),
    path('deliverd/<int:id>', views.deliverd, name='deliverd'),
    path('reports', views.reports, name='reports'),
    path('edit_product/del_product/<int:id>',
         views.del_product, name='del_product'),


]
if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL,
                          document_root=settings.MEDIA_ROOT)
