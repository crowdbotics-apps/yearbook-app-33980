from rest_framework import serializers
from .models import (
    CreditCards,
    HighSchool,
    HighSchoolID,
    Messages,
    PurchaseRecapp,
    Recapp,
    RecappQuotes,
    RecappVideos,
    YearbookCommittee
)

from users.models import User
from home.api.v1.serializers import UserSerializer

class HighSchoolSerializer(serializers.ModelSerializer):
    class Meta:
        model=HighSchool
        fields='__all__'

class StudentSerializer(serializers.ModelSerializer):
    high_school_code = serializers.SerializerMethodField('get_high_school_code')
    high_school_id = serializers.IntegerField(write_only=True)
    high_school = HighSchoolSerializer()
    class Meta:
        model = User
        fields = ["id", "email", "name","lname","username","dob","high_school","high_school_id","address","zip_code","status","photo","high_school_code","role"]
        extra_kwargs ={
            'high_school_code':{'read_only':True},
            'high_school_id':{'write_only': True},

        }
    def get_high_school_code(self,student):
        try:
            code = HighSchoolID.objects.get(user=student.id).code
            return code
        except:
            return ""

class SchoolAdminSerializer(serializers.ModelSerializer):
    high_school_id = serializers.IntegerField(write_only=True)
    high_school = HighSchoolSerializer()

    class Meta:
        model = User
        fields = ["id", "email", "name","lname","username","dob","high_school","high_school_id","address","zip_code","status","photo","role"]
        extra_kwargs ={
            'high_school_id':{'write_only': True},
        }

class HighSchoolIdSerializer(serializers.ModelSerializer):
    user = StudentSerializer(read_only=True)
    class Meta:
        model=HighSchoolID
        fields=['user','file','code','status']
        extra_kwargs = {
            'user': {'read_only': True},
            'code': {'read_only': True},
        }

class RecappQuotesSerializer(serializers.ModelSerializer):
    class Meta:
        model=RecappQuotes
        fields=('__all__')

class RecappVideosSerializer(serializers.ModelSerializer):
    class Meta:
        model=RecappVideos
        fields=('__all__')


class RecappSerializer(serializers.ModelSerializer):
    # quotes = RecappQuotesSerializer(many=True)
    # videos = RecappVideosSerializer(many=True)
    high_school = HighSchoolSerializer(read_only=True)
    high_school_id = serializers.IntegerField(write_only=True)

    class Meta:
        model=Recapp
        fields=['id','user','high_school','high_school_id','recapp','recapp_cover','price','recapp_year','zip_code','status']
        
        extra_kwargs ={
            'user':{'read_only':True},
            'status':{'read_only':True},
            'high_school_id':{'write_only': True},
        }

    def create(self, validated_data):
        user = self.context['request'].user
        # quotes_data = validated_data.pop('quotes')
        # videos_data = validated_data.pop('videos')

        recapp = Recapp.objects.create(
            user=user, 
            **validated_data
        )

        # print(validated_data)

        # for quote in quotes_data:
        #     q= RecappQuotes.objects.create(recapp=recapp,quotes=quote)
        #     recapp.quotes.add(q)

        # for video in videos_data:
        #     v = RecappVideos.objects.create(recapp=recapp,videos=video)
        #     recapp.videos.add(v)
        
        return recapp

class HighSchoolSerializer(serializers.ModelSerializer):

    class Meta:
        model=HighSchool
        fields=('__all__')

class PurchaseRecappSerializer(serializers.ModelSerializer):
    recapp = RecappSerializer(read_only=True)
    recapp_id = serializers.IntegerField(write_only=True)

    first_name = serializers.CharField(write_only=True)
    last_name = serializers.CharField(write_only=True)
    cvc = serializers.CharField(write_only=True)
    expiry = serializers.DateField(write_only=True,input_formats=['%m/%y'])
    card_number = serializers.CharField(write_only=True)
    cardholder_name = serializers.CharField(write_only=True)

    class Meta:
        model=PurchaseRecapp
        fields=('id','first_name','last_name','cvc','expiry','card_number','cardholder_name','recapp','recapp_id','user','status','purchased_at')
        extra_kwargs = {
            'user': {'read_only': True},
            'status':{'read_only': True},
            'recapp_id':{'write_only': True},
            'purchased_at':{'read_only':True}
        }
    
    def create(self,validated_data):
        user = self.context['request'].user
        first_name = validated_data.pop('first_name')
        last_name = validated_data.pop('last_name')
        cvc = validated_data.pop('cvc')
        expiry = validated_data.pop('expiry')
        card_number = validated_data.pop('card_number')
        cardholder_name = validated_data.pop('cardholder_name')

        CreditCards.objects.create(first_name=first_name,last_name=last_name,cvc=cvc,expiry=expiry,card_number=card_number,cardholder_name=cardholder_name,user=user)

        purchase = PurchaseRecapp.objects.create(user=user,**validated_data,status='done')
        
        return purchase

class CreditCardsSerializer(serializers.ModelSerializer):
    expiry = serializers.DateField(format='%m/%y')
    card_number_hidden = serializers.SerializerMethodField('get_card_number')
    
    class Meta:
        model=CreditCards
        fields=('__all__')
        extra_kwargs ={
            'first_name':{'required':False},
            'last_name':{'required':False},
            'user':{'read_only':True},
            'is_approved':{'read_only':True},
            'card_number':{'write_only':True},
            'cvc':{'write_only':True},
            'card_number_hidde':{'read_only':True}
        }
    
    def get_card_number(self,cc):
        return 'XXXXXXXXXXXX'+cc.card_number[12:]


    def create(self, validated_data):
        user = self.context['request'].user

        cc = CreditCards.objects.create(
            user=user, 
            **validated_data
        )
        return cc

class MessageSerializer(serializers.ModelSerializer):
    sender = UserSerializer(read_only=True)
    receiver = UserSerializer(read_only=True)
    receiver_id = serializers.IntegerField(write_only=True)

    class Meta:
        model = Messages
        fields = ["id","sender","receiver","text","created_at","read_at","receiver_id"]
        extra_kwargs ={
            'read_at':{'read_only':True},
        }

class YearbookCommitteeSerializer(serializers.ModelSerializer):
    high_school_id = serializers.IntegerField(write_only=True)
    high_school = HighSchoolSerializer(read_only=True)
    user_id = serializers.IntegerField(write_only=True)
    user = StudentSerializer(read_only=True)

    class Meta:
        model = YearbookCommittee
        fields = ['id','user','high_school','user_id','high_school_id']