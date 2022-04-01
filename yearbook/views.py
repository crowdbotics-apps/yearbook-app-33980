from django.db.models import Count
from home.api.v1.serializers import UserSerializer
from users.models import User
from rest_framework.viewsets import ModelViewSet
from rest_framework.views import APIView
from rest_framework.response import Response
from .models import CreditCards, HighSchool, HighSchoolID, PurchaseRecapp, Recapp, Messages
from .serializers import CreditCardsSerializer, HighSchoolIdSerializer, HighSchoolSerializer, MessageSerializer,PurchaseRecappSerializer, RecappSerializer, StudentSerializer,SchoolAdminSerializer
from rest_framework.permissions import IsAuthenticated
from django.core.mail import EmailMultiAlternatives
from django.dispatch import receiver
from django.template.loader import render_to_string
from django.urls import reverse
from django_rest_passwordreset.signals import reset_password_token_created
from rest_framework.parsers import  MultiPartParser, FormParser, JSONParser
from django.shortcuts import get_object_or_404
from rest_framework.decorators import action
import stripe
from datetime import datetime, timedelta
from django.core.mail import send_mail

class HighSchoolIdViewSet(ModelViewSet):
    permission_classes = (IsAuthenticated,)

    serializer_class = HighSchoolIdSerializer
    queryset = HighSchoolID.objects.all()

    def perform_create(self,serializer):
        serializer.save(user=self.request.user,file=self.request.data['file'])

    @action(detail=False, methods=["get"],url_path=r'pending')
    def pending(self,request, *args, **kwargs):
        role = request.user.role
        ids = HighSchoolID.objects.filter(status="pending")
        if role == '3':
            ids = ids
        else:
            ids = ids.filter(user__high_school=request.user.high_school)
        ids = HighSchoolID.objects.filter(status="pending")
        seriralizer = self.serializer_class(ids,many=True)
        return Response(seriralizer.data)

    @action(detail=False, methods=["get"],url_path=r'rejected')
    def rejected(self,request, *args, **kwargs):
        ids = HighSchoolID.objects.filter(status="rejected")
        seriralizer = self.serializer_class(ids,many=True)
        return Response(seriralizer.data)

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

    def list(self, request):
        role = request.user.role

        if role == '3':
            queryset = self.queryset
        else:
            queryset = self.queryset.filter(high_school=request.user.high_school)

        serializer = self.serializer_class(queryset, many=True)
        return Response(serializer.data)

    def retrieve(self, request, pk=None):
        role = request.user.role

        if role == '3':
            queryset = self.queryset
        else:
            queryset = self.queryset.filter(high_school=request.user.high_school)
            
        recapps = get_object_or_404(queryset, id=pk)
        serializer = self.serializer_class(recapps)
        return Response(serializer.data)

    @action(detail=False, methods=["get"],url_path=r'highschool/(?P<highschool_id>\d+)')
    def highschool(self,request, *args, **kwargs):
        recapps = self.queryset.filter(high_school=self.kwargs['highschool_id'])
        seriralizer = self.serializer_class(recapps,many=True)
        return Response(seriralizer.data)

    @action(detail=False, methods=["put"],url_path=r'approve/(?P<recapp_id>\d+)')
    def approve(self,request, *args, **kwargs):
        recapp = self.queryset.get(id=self.kwargs['recapp_id'])
        recapp.status="approved"
        recapp.save()
        seriralizer = self.serializer_class(recapp)
        return Response(seriralizer.data)

    @action(detail=False, methods=["put"],url_path=r'reject/(?P<recapp_id>\d+)')
    def reject(self,request, *args, **kwargs):
        recapp = self.queryset.get(id=self.kwargs['recapp_id'])
        recapp.status="rejected"
        recapp.save()
        if request.method == "PUT":
            message = request.PUT["message"]
            send_mail(
                'Your Recapp has been rejected',
                message,
                'swornim.shrestha@crowdbotics.com',
                ['srestaswrnm@gmail.com'],
                fail_silently=False,
            )
        seriralizer = self.serializer_class(recapp)
        return Response(seriralizer.data)

    @action(detail=False, methods=["get"],url_path=r'pending')
    def pending(self,request, *args, **kwargs):
        role = request.user.role

        if role == '3':
            queryset = self.queryset
        else:
            queryset = self.queryset.filter(high_school=request.user.high_school)

        recapps = queryset.filter(status="pending")
        seriralizer = self.serializer_class(recapps,many=True)
        return Response(seriralizer.data)

    @action(detail=False, methods=["get"],url_path=r'rejected')
    def rejected(self,request, *args, **kwargs):
        recapps = Recapp.objects.filter(status="rejected")
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

    # def perform_create(self,serializer):
    #     stripe.api_key = 'sk_test_51KeejWDUTAU1FowaGozzaiy2ghoEY9Eiiv7EiZrXYxuUdEPVffEyZbyjtO3KIrxFLb6VSTor3wKsVlWgcEzejJF2005omCIkWQ'

    #     test_payment_intent = stripe.PaymentIntent.create(
    #                             amount=1000, currency='usd', 
    #                             payment_method_types=['card'],
    #                             receipt_email='test@example.com',
    #                             payment_method="4242 4242 4242 4242",
    #                             confirm=True)
    #     if(test_payment_intent):
    #         serializer.save()
    #     else:
    #         serializer.save()

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

class StudentsViewset(ModelViewSet):
    permission_classes = (IsAuthenticated,)
    serializer_class= StudentSerializer
    queryset = User.objects.filter(is_superuser=False, is_staff=False)

    @action(detail=False, methods=["put"],url_path=r'suspend/(?P<student_id>\d+)')
    def suspend(self,request, *args, **kwargs):
        student = self.queryset.get(id=self.kwargs['student_id'])
        student.status="suspended"
        student.save()
        seriralizer = self.serializer_class(student)
        return Response(seriralizer.data)
    
    @action(detail=False, methods=["put"],url_path=r'active/(?P<student_id>\d+)')
    def active(self,request, *args, **kwargs):
        student = self.queryset.get(id=self.kwargs['student_id'])
        student.status="active"
        student.save()
        seriralizer = self.serializer_class(student)
        return Response(seriralizer.data)

    @action(detail=False, methods=["put"],url_path=r'approve_id/(?P<student_id>\d+)')
    def approve_id(self,request, *args, **kwargs):
        student = HighSchoolID.objects.get(user=self.kwargs['student_id'])
        student.status="approved"
        student.save()
        seriralizer = HighSchoolIdSerializer(student)
        return Response(seriralizer.data)

    @action(detail=False, methods=["put"],url_path=r'reject_id/(?P<student_id>\d+)')
    def reject_id(self,request, *args, **kwargs):
        student = HighSchoolID.objects.get(user=self.kwargs['student_id'])
        student.status="rejected"
        student.save()
        seriralizer = HighSchoolIdSerializer(student)
        return Response(seriralizer.data)

    def list(self, request):
        role = request.user.role

        if role == '3':
            queryset = self.queryset
        else:
            queryset = self.queryset.filter(high_school=request.user.high_school)

        serializer = self.serializer_class(queryset, many=True)
        return Response(serializer.data)

    def retrieve(self, request, pk=None):
        role = request.user.role

        if role == '3':
            queryset = self.queryset
        else:
            queryset = self.queryset.filter(high_school=request.user.high_school)
            
        students = get_object_or_404(queryset, id=pk)
        serializer = self.serializer_class(students)
        return Response(serializer.data)

class MessagesViewset(ModelViewSet):
    permission_classes = (IsAuthenticated,)

    serializer_class = MessageSerializer
    queryset = Messages.objects.all()

    def list(self, request):
        queryset = Messages.objects.filter(receiver=request.user.id)
        serializer = MessageSerializer(queryset, many=True)
        return Response(serializer.data)

    def perform_create(self,serializer):
        return serializer.save(sender=self.request.user)


class AnalyticsAPIView(APIView):

    def get(self, request):
        role = request.user.role

        if role == '3':
            active_users = User.objects.filter(is_active=True).count()
            new_users = User.objects.filter(date_joined__lt=datetime.today()- timedelta(30)).count()
            sold_recapps = PurchaseRecapp.objects.filter(status='completed').count()
            registration = User.objects.extra(
                    select={'date_joined': 'date( date_joined )'}
                    ).values('date_joined').annotate(
                        total= Count('id',distinct=True)).order_by('date_joined'
                        )

        else:
            active_users = User.objects.filter(is_active=True,high_school=request.user.high_school).count()
            new_users = User.objects.filter(high_school=request.user.high_school,date_joined__lt=datetime.today()- timedelta(30)).count()
            sold_recapps = PurchaseRecapp.objects.filter(recapp__high_school=request.user.high_school,status='completed').count()
            registration = User.objects.filter(high_school=request.user.high_school).extra(
                select={'date_joined': 'date( date_joined )'}
                ).values('date_joined').annotate(
                    total= Count('id',distinct=True)).order_by('date_joined'
                    )

        online_users = 20

        return Response({"active_users":active_users,"online_users":online_users,"new_users":new_users,"sold_recapps":sold_recapps,"registration":registration})


class SchoolAdminsViewset(ModelViewSet):
    permission_classes = (IsAuthenticated,)

    serializer_class = SchoolAdminSerializer
    queryset = User.objects.filter(role=2)

    @action(detail=False, methods=["put"],url_path=r'approve/(?P<admin_id>\d+)')
    def approve(self,request, *args, **kwargs):
        recapp = self.queryset.get(id=self.kwargs['admin_id'])
        recapp.status="approved"
        recapp.save()
        seriralizer = self.serializer_class(recapp)
        return Response(seriralizer.data)

    @action(detail=False, methods=["put"],url_path=r'reject/(?P<admin_id>\d+)')
    def reject(self,request, *args, **kwargs):
        recapp = self.queryset.get(id=self.kwargs['admin_id'])
        recapp.status="rejected"
        recapp.save()
        seriralizer = self.serializer_class(recapp)
        return Response(seriralizer.data)

    @action(detail=False, methods=["get"],url_path=r'pending')
    def pending(self,request, *args, **kwargs):
        role = request.user.role

        if role == '3':
            queryset = self.queryset
        else:
            queryset = self.queryset.filter(high_school=request.user.high_school)
        recapps = queryset.filter(status="pending")
        seriralizer = self.serializer_class(recapps,many=True)
        return Response(seriralizer.data)

    @action(detail=False, methods=["get"],url_path=r'rejected')
    def rejected(self,request, *args, **kwargs):
        recapps = self.queryset.filter(status="rejected")
        seriralizer = self.serializer_class(recapps,many=True)
        return Response(seriralizer.data)