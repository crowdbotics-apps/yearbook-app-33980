from django.shortcuts import render
from rest_framework.viewsets import ModelViewSet, ViewSet
from rest_framework.response import Response
from .models import CreditCards, HighSchool, HighSchoolID, PurchaseRecapp, Recapp
from .serializers import CreditCardsSerializer, HighSchoolIdSerializer, HighSchoolSerializer, PurchaseRecappSerializer, RecappSerializer
from rest_framework.permissions import IsAuthenticated
from django.core.mail import EmailMultiAlternatives
from django.dispatch import receiver
from django.template.loader import render_to_string
from django.urls import reverse
from django_rest_passwordreset.signals import reset_password_token_created
from rest_framework.parsers import  MultiPartParser, FormParser, JSONParser
from django.shortcuts import get_object_or_404
from rest_framework.decorators import action

class UploadHighSchoolIdViewSet(ModelViewSet):
    permission_classes = (IsAuthenticated,)

    serializer_class = HighSchoolIdSerializer
    queryset = HighSchoolID.objects.all()
    http_method_names = ['post']

    def perform_create(self,serializer):
        serializer.save(user=self.request.user,file=self.request.data['file'])

@receiver(reset_password_token_created)
def password_reset_token_created(sender, instance, reset_password_token, *args, **kwargs):
    # send an e-mail to the user
    context = {
        'current_user': reset_password_token.user,
        'username': reset_password_token.user.username,
        'email': reset_password_token.user.email,
        'reset_password_url': "{}?token={}".format(
            instance.request.build_absolute_uri(reverse('password_reset:reset-password-confirm')),
            reset_password_token.key),
        'reset_token':reset_password_token.key
    }

    # render email text
    email_html_message = render_to_string('email/user_reset_password.html', context)
    email_plaintext_message = render_to_string('email/user_reset_password.txt', context)

    msg = EmailMultiAlternatives(
        # title:
        "Password Reset for {title}".format(title="Re-capp"),
        # message:
        email_plaintext_message,
        # from:
        "swornim.shrestha@crowdbotics.com",
        # to:
        [reset_password_token.user.email]
    )
    msg.attach_alternative(email_html_message, "text/html")
    msg.send()


class RecappViewSet(ModelViewSet):
    permission_classes = (IsAuthenticated,)
    parser_classes = (MultiPartParser, FormParser, JSONParser)
    serializer_class = RecappSerializer
    queryset = Recapp.objects.all()
    # http_method_names=['post']

    @action(detail=False, methods=["get"],url_path=r'highschool/(?P<highschool_id>\d+)')
    def highschool(self,request, *args, **kwargs):
        recapps = self.queryset.filter(high_school=self.kwargs['highschool_id'])
        seriralizer = self.serializer_class(recapps,many=True)
        return Response(seriralizer.data)

class HighSchoolsViewset(ModelViewSet):
    serializer_class = HighSchoolSerializer
    queryset = HighSchool.objects.all()

    def list(self, request):
        queryset = HighSchool.objects.all()
        serializer = HighSchoolSerializer(queryset, many=True)
        return Response(serializer.data)

    def retrieve(self, request, pk=None):
        queryset = HighSchool.objects.all()
        highschool = get_object_or_404(queryset, id=pk)
        serializer = HighSchoolSerializer(highschool)
        return Response(serializer.data)


class PurchaseRecappViewSet(ModelViewSet):
    permission_classes = (IsAuthenticated,)

    serializer_class = PurchaseRecappSerializer
    queryset = PurchaseRecapp.objects.all()

    def list(self, request):
        queryset = PurchaseRecapp.objects.filter(user=request.user)
        serializer = PurchaseRecappSerializer(queryset, many=True)
        return Response(serializer.data)

    def retrieve(self, request, pk=None):
        queryset = PurchaseRecapp.objects.all()
        purchase = get_object_or_404(queryset, id=pk)
        serializer = PurchaseRecappSerializer(purchase)
        return Response(serializer.data)

class CreditCardsViewset(ModelViewSet):
    permission_classes = (IsAuthenticated,)

    serializer_class = CreditCardsSerializer
    queryset = CreditCards.objects.all()

    def list(self, request):
        queryset = CreditCards.objects.filter(user=request.user)
        serializer = CreditCardsSerializer(queryset, many=True)
        return Response(serializer.data)

    def retrieve(self, request, pk=None):
        queryset = CreditCards.objects.all()
        purchase = get_object_or_404(queryset, id=pk)
        serializer = CreditCardsSerializer(purchase)
        return Response(serializer.data)