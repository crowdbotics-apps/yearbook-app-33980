from posixpath import basename
from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import (
    AnalyticsAPIView,
    PurchaseRecappViewSet,
    RecappViewSet,
    HighSchoolIdViewSet,
    HighSchoolsViewset,
    CreditCardsViewset,
    StudentsViewset,
    MessagesViewset,
    SchoolAdminsViewset,
    YearbookCommitteeViewset,
    CardsListAPIView,
    CardsDetailAPIView
    )

router = DefaultRouter()
router.register(r'highschools',HighSchoolsViewset,basename="high_schools")
router.register(r'id', HighSchoolIdViewSet,basename="id")
router.register(r'recapp',RecappViewSet,basename="recapp")
router.register(r'purchase',PurchaseRecappViewSet,basename="purchase")
router.register(r'cc',CreditCardsViewset,basename="credit_cards")
router.register(r'students',StudentsViewset, basename="students")
router.register(r'messages',MessagesViewset, basename="messages")
router.register(r'school_admins',SchoolAdminsViewset,basename="school_admins")
router.register(r'committee',YearbookCommitteeViewset,basename="yearbook_committee")

urlpatterns = [
    path("",include(router.urls)),
    path('password_reset/', include('django_rest_passwordreset.urls', namespace='password_reset')),
    path(r'analytics/',AnalyticsAPIView.as_view()),
    path(r'cards/',CardsListAPIView.as_view()),
    path(r'cards/<str:pk>',CardsDetailAPIView.as_view())
]
