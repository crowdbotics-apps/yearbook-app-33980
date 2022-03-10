from rest_framework import serializers
from .models import (
    HighSchool,
    HighSchoolID,
    PurchaseRecapp,
    Recapp,
    RecappQuotes,
    RecappVideos
)

class HighSchoolSerializer(serializers.ModelSerializer):
    class Meta:
        model=HighSchool
        fields='__all__'

class HighSchoolIdSerializer(serializers.ModelSerializer):
    
    class Meta:
        model=HighSchoolID
        fields=['user','file']
        extra_kwargs = {
            'user': {'read_only': True},
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

    class Meta:
        model=Recapp
        fields=['user','high_school','recapp','recapp_cover','recapp_year','zip_code','is_approved']
        
        extra_kwargs ={
            'user':{'read_only':True},
            'is_approved':{'read_only':True}
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
    recapp = RecappSerializer()
    class Meta:
        model=PurchaseRecapp
        fields=('__all__')
        extra_kwargs = {
            'user': {'read_only': True},
            'status':{'read_only': True},
        }
    
    def create(self,validated_data):
        user = self.context['request'].user

        purchase = PurchaseRecapp.objects.create(user=user,**validated_data,status='pending')
        
        return purchase