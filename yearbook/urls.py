from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import (
    PurchaseRecappViewSet,
    RecappViewSet,
    UploadHighSchoolIdViewSet,
    HighSchoolsViewset,
    CreditCardsViewset,
    StudentsViewset,
    MessagesViewset
    )

router = DefaultRouter()
router.register(r'highschools',HighSchoolsViewset,basename="high_schools")
router.register(r'upload_id', UploadHighSchoolIdViewSet,basename="upload_id")
router.register(r'recapp',RecappViewSet,basename="recapp")
router.register(r'purchase',PurchaseRecappViewSet,basename="purchase")
router.register(r'cc',CreditCardsViewset,basename="credit_cards")
router.register(r'students',StudentsViewset, basename="students")
# router.register(r'messages',MessagesViewset, basename="messages")
urlpatterns = [
    path("",include(router.urls)),
    path('password_reset/', include('django_rest_passwordreset.urls', namespace='password_reset')),

]
