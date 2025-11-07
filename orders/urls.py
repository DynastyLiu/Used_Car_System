from django.urls import path, include
from rest_framework.routers import DefaultRouter
from . import views

router = DefaultRouter()
router.register(r'', views.OrderViewSet, basename='order')
router.register(r'messages', views.OrderMessageViewSet, basename='message')
router.register(r'reviews', views.OrderReviewViewSet, basename='review')

urlpatterns = [path('', include(router.urls))]

