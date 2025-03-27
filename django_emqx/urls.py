## django_emqx/urls.py

from django.urls import path, include

from rest_framework.routers import DefaultRouter

from django_emqx.views import NotificationViewSet, EMQXDeviceViewSet, EMQXTokenViewSet


router = DefaultRouter()
router.register(r'devices', EMQXDeviceViewSet, basename='devices')
router.register(r'token', EMQXTokenViewSet, basename='token')
router.register(r'notifications', NotificationViewSet, basename='notifications')

urlpatterns = [

    path('', include(router.urls)),
]
