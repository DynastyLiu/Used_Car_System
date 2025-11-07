from django.urls import path, include
from rest_framework.routers import DefaultRouter
from . import views

router = DefaultRouter()
router.register(r'brands', views.CarBrandViewSet, basename='brand')
router.register(r'types', views.CarTypeViewSet, basename='type')
router.register(r'favorites', views.FavoriteViewSet, basename='favorite')
router.register(r'', views.VehicleViewSet, basename='vehicle')

urlpatterns = [path('', include(router.urls))]

