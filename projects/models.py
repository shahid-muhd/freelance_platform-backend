from django.db import models
from django.utils import timezone
from accounts.models import CustomUser
from django.contrib.postgres.fields import ArrayField

# Create your models here.


class Project(models.Model):
    STATUS_CHOICES = [
        ("recruiting", "Recruiting"),
        ("progress", "In Progress"),
        ("completed", "Completed"),
        ("cancelled", "Cancelled"),
        ("hold", "On Hold"),
    ]
    EXPERTISE_CHOICES = [
        ("entry_level", "Entry Level"),
        ("intermediate", "Intermediate"),
        ("expert", "Expert"),
    ]

    def default_deadline():
        return timezone.now().date() + timezone.timedelta(days=30)

    
    title = models.CharField(max_length=155,blank=False)
    description = models.TextField(blank=False)
    budget = models.IntegerField()
    skills = ArrayField(models.CharField(max_length=115), null=True)
    features = ArrayField(models.CharField(max_length=115), null=True)
    client = models.ForeignKey(CustomUser, on_delete=models.DO_NOTHING)
    created_date = models.DateTimeField(default=timezone.now)
    deadline = models.DateField(default=default_deadline)
    status = models.CharField(
        max_length=20, choices=STATUS_CHOICES, default="recruiting"
    )
    freelancer = models.ForeignKey(
        CustomUser, on_delete=models.DO_NOTHING, related_name="freelancer_projects",null=True
    )
    freelancer_expertise = models.CharField(
        max_length=20, choices=EXPERTISE_CHOICES, null=True
    )
    is_verified = models.BooleanField(default=False)
    is_blocked = models.BooleanField(default=False)

    def __str__(self):
        return self.title



class SavedProjects(models.Model):

    user=models.ForeignKey(CustomUser,on_delete=models.CASCADE)
    project=models.ForeignKey(Project,on_delete=models.CASCADE)

    


