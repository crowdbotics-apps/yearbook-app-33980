from email import message
from django.db.models import Count
from home.api.v1.serializers import UserSerializer
from users.models import User
from rest_framework.viewsets import ModelViewSet
from rest_framework.views import APIView
from rest_framework.response import Response
from .models import CreditCards, HighSchool, HighSchoolID, PurchaseRecapp, Recapp, Messages, YearbookCommittee
from .serializers import CreditCardsSerializer, HighSchoolIdSerializer, HighSchoolSerializer, MessageSerializer,PurchaseRecappSerializer, RecappSerializer, StudentSerializer,SchoolAdminSerializer, YearbookCommitteeSerializer
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
from django.conf import settings

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
            message = request.data.get("message")
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


class CardsDetailAPIView(APIView):
    stripe.api_key = settings.STRIPE_SECRET_KEY
    def get(self, request,pk):

        user = request.user
        user_stripe_id = user.stripe_id

        card =stripe.Customer.retrieve_source(
        user_stripe_id,
        pk,
        )
        return Response(card)

    # def update(self,request,pk):
    #     user = request.user
    #     user_stripe_id = user.stripe_id
        
    #     card = stripe.Customer.delete_source(
    #     user_stripe_id,
    #     pk,
    #     )

    #     return Response(card)

    def delete(self,request,pk):
        user = request.user
        user_stripe_id = user.stripe_id
        card = stripe.Customer.delete_source(
        user_stripe_id,
        pk,
        )

        return Response(card)

class CardsListAPIView(APIView):
    stripe.api_key = settings.STRIPE_SECRET_KEY
    def post(self,request):
        user = request.user
        token = stripe.Token.create(
            card={
                "name":"Swornim Shrestha",
                "number": "4242424242424242",
                "exp_month": 4,
                "exp_year": 2023,
                "cvc": "314",
            },
            )
        card_details = stripe.Customer.create_source(user.stripe_id,source=token)

        return Response(card_details)

    def get(self, request):

        user = request.user
        user_stripe_id = user.stripe_id
        sources = stripe.Customer.list_sources(user_stripe_id,object="card")
        return Response(sources.data)

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
        queryset_reciever = Messages.objects.filter(receiver=request.user.id)
        queryset_sender = Messages.obejcts.filter(sender=request.user.id)

        
        queryset = queryset_reciever.union(queryset_sender)

        serializer = MessageSerializer(queryset, many=True)
        return Response(serializer.data)

    def perform_create(self,serializer):
        return serializer.save(sender=self.request.user)

    @action(detail=False, methods=["get"],url_path=r'chats')
    def chats(self,request, *args, **kwargs):
        role = request.user.role
        senders = []
        chats = Messages.objects.values('sender_id').filter(receiver=request.user).distinct()
        for s in chats:
            s_temp = User.objects.get(id=s['sender_id'])
            recent_message = Messages.objects.filter(sender=s['sender_id'],receiver=request.user).last()
            #Check if user has uploaded Photo
            if s_temp.photo:
                user_photo = s_temp.photo
            else:
                user_photo = ""

            #Custom Chat Object
            chat_obj = {
                "user_id":s_temp.id,
                "name":str(s_temp.name)+' '+str(s_temp.lname),
                "photo":user_photo,
                "recent_message":recent_message.text,
                "created_at":recent_message.created_at
            }
            senders.append(chat_obj)

        return Response(senders)

    @action(detail=False, methods=["get"],url_path=r'(?P<student_id>\d+)')
    def messages_by_user(self,request, *args, **kwargs):

        queryset_reciever = Messages.objects.filter(receiver=request.user.id,sender=self.kwargs['student_id'])
        queryset_sender = Messages.objects.filter(sender=request.user.id,receiver=self.kwargs['student_id'])
        queryset = queryset_reciever.union(queryset_sender)

        serializer =MessageSerializer(queryset,many=True)
        return Response(serializer.data)

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
        queryset = self.queryset

        if role != 3:
            return Response({'message':'Unauthorized'},status=401)

        school_admins = queryset.filter(status="pending")
        seriralizer = self.serializer_class(school_admins,many=True)
        return Response(seriralizer.data)

    @action(detail=False, methods=["get"],url_path=r'rejected')
    def rejected(self,request, *args, **kwargs):
        recapps = self.queryset.filter(status="rejected")
        seriralizer = self.serializer_class(recapps,many=True)
        return Response(seriralizer.data)

class YearbookCommitteeViewset(ModelViewSet):
    permission_classes = (IsAuthenticated,)

    serializer_class = YearbookCommitteeSerializer
    queryset = YearbookCommittee.objects.all()

    def perform_create(self,serializer):
        user_data = User.objects.get(id=self.request.data['user_id'])

        serializer.save(user=user_data,high_school=self.request.user.high_school)

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

    @action(detail=False,methods=["get"],url_path=r'school/')
    def committee_from_school(self,request):
        school_committee = self.queryset.filter(high_school=request.user.high_school)
        serializer = self.serializer_class(school_committee,many=True)

        return Response(serializer.data)

    @action(detail=False,methods=["delete"],url_path=r'remove_student/(?P<student_id>\d+)')
    def committee_from_school(self,request, *args, **kwargs):
        user = self.queryset.filter(user__id=self.kwargs['student_id'])
        serializer = self.serializer_class(user)
        user.delete()
        return Response(serializer.data)

    @action(detail=False, methods=["put"],url_path=r'approve/(?P<request_id>\d+)')
    def approve(self,request, *args, **kwargs):
        committee_request = self.queryset.get(id=self.kwargs['request_id'])
        committee_request.status="approved"
        committee_request.save()
        seriralizer = self.serializer_class(committee_request)
        return Response(seriralizer.data)

    @action(detail=False, methods=["put"],url_path=r'reject/(?P<request_id>\d+)')
    def reject(self,request, *args, **kwargs):
        committee_request = self.queryset.get(id=self.kwargs['request_id'])
        committee_request.status="rejected"
        committee_request.save()

        if request.method == "PUT":
            message = request.data.get("message")
            send_mail(
                'Your Committee request has been rejected',
                message,
                'swornim.shrestha@crowdbotics.com',
                ['srestaswrnm@gmail.com'],
                fail_silently=False,
            )
        seriralizer = self.serializer_class(committee_request)
        return Response(seriralizer.data)

    @action(detail=False, methods=["get"],url_path=r'pending')
    def pending(self,request, *args, **kwargs):
        role = request.user.role

        if role == '3':
            queryset = self.queryset
        else:
            queryset = self.queryset.filter(high_school=request.user.high_school)

        committee_requests = queryset.filter(status="pending")
        seriralizer = self.serializer_class(committee_requests,many=True)
        return Response(seriralizer.data)