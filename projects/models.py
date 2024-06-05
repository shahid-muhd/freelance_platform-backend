from django.db import models
from django.utils import timezone
from accounts.models import CustomUser
from django.contrib.postgres.fields import ArrayField

# Create your models here.


class Project(models.Model):
    STATUS_CHOICES = [
        ("recruiting", "Recruiting"),
        ("progressing", "In Progress"),
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

    title = models.CharField(max_length=155, blank=False)
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
        CustomUser,
        on_delete=models.DO_NOTHING,
        related_name="freelancer_projects",
        null=True,
    )
    freelancer_expertise = models.CharField(
        max_length=20, choices=EXPERTISE_CHOICES, null=True, default="intermediate"
    )

    is_verified = models.BooleanField(default=False)
    is_sample_completed = models.BooleanField(default=False)
    is_final_completed = models.BooleanField(default=False)
    is_blocked = models.BooleanField(default=False)
    is_archived = models.BooleanField(default=False)
    is_advance_paid = models.BooleanField(default=False)

    def get_freelancer_expertise_display(self):
        return dict(self.EXPERTISE_CHOICES).get(self.freelancer_expertise, "")

    def __str__(self):
        return self.title


class SavedProjects(models.Model):

    user = models.ForeignKey(CustomUser, on_delete=models.CASCADE)
    project = models.ForeignKey(Project, on_delete=models.CASCADE)


class Proposals(models.Model):

    STATUS_CHOICES = [
        ("unanswered", "Unanswered"),
        ("responded", "Responded"),
        ("accepted", "Accepted"),
    ]

    applicant = models.ForeignKey(CustomUser, on_delete=models.CASCADE)
    work_profile = models.CharField(max_length=255, blank=False)
    project = models.ForeignKey(Project, on_delete=models.CASCADE)
    created_date = models.DateTimeField(default=timezone.now)
    bid_amount = models.IntegerField()
    cover_letter = models.TextField(null=True)
    document = models.FileField(upload_to="project_applications/", null=True)
    status = models.CharField(
        max_length=20, choices=STATUS_CHOICES, default="unanswered"
    )
    is_advance_paid = models.BooleanField(default=False)
