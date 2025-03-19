from django.urls import path, include
from rest_framework.routers import DefaultRouter
from . import views

router = DefaultRouter()
router.register(r"plan", views.PlanViewSet, basename='plan')

urlpatterns = [
    path('', include(router.urls)),
]
