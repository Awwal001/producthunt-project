from django.conf import settings
from django.conf.urls.static import static
from django.urls import path
from . import views

urlpatterns = [
    path('create', views.create, name='create'),
    path('<int:product_id>', views.detail, name='detail'),
    path('edit/<int:product_id>', views.edit_product, name='edit_product'),
    path('<int:product_id>', views.delete_product, name='delete_product'),
    path('vote', views.vote, name='vote'),
    path('addcomment/', views.addcomment, name='addcomment'),
    path('search/', views.search, name='search'),
    path('user_products/', views.user_products, name='user_products'),
   
    path("collection", views.collection, name="collections"),
    path("collection/add_to_collection/<int:id>", views.add_to_collection, name="add_collection"),
    
    path("offers", views.offer, name="offers"),
    path("offer/make_offer", views.make_offer, name="make_offer"),
]
if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)