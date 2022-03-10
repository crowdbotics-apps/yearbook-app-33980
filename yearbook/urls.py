from django.urls import path, include
from rest_framework.routers import DefaultRouter

from .views import RecappViewSet, UploadHighSchoolIdViewSet,HighSchoolsViewset

router = DefaultRouter()
router.register(r'highschools',HighSchoolsViewset,basename="high_schools")
router.register(r'upload_id', UploadHighSchoolIdViewSet,basename="upload_id")
router.register(r'recapp',RecappViewSet,basename="recapp")
urlpatterns = [
    path("",include(router.urls)),
    path('password_reset/', include('django_rest_passwordreset.urls', namespace='password_reset')),

]
