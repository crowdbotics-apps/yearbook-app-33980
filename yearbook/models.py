from django.db import models
import random

def code_generator():
    return ''.join(random.choice('0123456789ABCDEF') for i in range(16))

class HighSchool(models.Model):
    name = models.CharField(max_length=30)

class HighSchoolID(models.Model):
    user = models.ForeignKey('users.User',on_delete=models.CASCADE)
    file = models.FileField(blank=True,default='')
    code = models.CharField(max_length=16,default=code_generator)
    status = models.CharField(max_length=16,default='pending')

class Recapp(models.Model):
    user = models.ForeignKey('users.User',on_delete=models.CASCADE)
    high_school = models.ForeignKey('HighSchool',on_delete=models.CASCADE)
    recapp = models.FileField(blank=True,default='')
    recapp_cover = models.ImageField(blank=True,default='')
    recapp_year = models.CharField(max_length=10)
    zip_code = models.IntegerField(blank=True)
    price = models.DecimalField(max_digits=6, decimal_places=2)
    status = models.CharField(max_length=10,default='pending')

class RecappQuotes(models.Model):
    recapp = models.ForeignKey('Recapp',on_delete=models.CASCADE)
    quotes = models.FileField()

class RecappVideos(models.Model):
    recapp = models.ForeignKey('Recapp',on_delete=models.CASCADE)
    videos = models.FileField()

class PurchaseRecapp(models.Model):
    user = models.ForeignKey('users.User',on_delete=models.CASCADE)
    status = models.CharField(max_length=10)
    recapp = models.ForeignKey('Recapp',on_delete=models.CASCADE)
    purchased_at = models.DateTimeField(auto_now_add=True)

class CreditCards(models.Model):
    user = models.ForeignKey('users.User',on_delete=models.CASCADE)
    first_name = models.CharField(max_length=20)
    last_name = models.CharField(max_length=20)
    cardholder_name = models.CharField(max_length=50)
    card_number = models.CharField(max_length=16)
    expiry = models.DateField()
    cvc= models.CharField(max_length=4)

class Messages(models.Model):
    sender = models.ForeignKey('users.User',on_delete=models.CASCADE,related_name="sender")
    receiver = models.ForeignKey('users.User',on_delete=models.CASCADE,related_name="receiver")
    text = models.CharField(max_length=500)
    read_at = models.DateTimeField(null=True)
    created_at = models.DateTimeField(auto_now_add=True)

class YearbookCommittee(models.Model):
    user = models.ForeignKey('users.User',on_delete=models.CASCADE)
    high_school = models.ForeignKey('HighSchool',on_delete=models.CASCADE)