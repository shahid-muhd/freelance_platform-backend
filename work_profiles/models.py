from django.db import models
from accounts.models import CustomUser
from mongoengine import Document, fields,ValidationError

# Create your models here.


class WorkProfile(Document):
    user=fields.IntField(required=True)
    title=fields.StringField(required=True)
    description=fields.StringField(required=True)
    skills=fields.ListField(max_length=10)


class Portfolio(models.Model):
    work_profile=models.CharField(max_length=255,blank=False,null=False)
    title = models.CharField(max_length=100,blank=False)
    description = models.CharField(max_length=255)
    cover_image=models.ImageField(upload_to="portfolio_images")
