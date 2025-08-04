# models.py
from django.db import models
from django.contrib.auth.models import User
from django.core.validators import RegexValidator
from django.utils import timezone
import json
from django.conf import settings

class MembershipApplication(models.Model):
    GENDER_CHOICES = [
        ('male', 'Male'),
        ('female', 'Female'),
        ('other', 'Other'),
        ('prefer-not-to-say', 'Prefer not to say'),
    ]
    
    REGION_CHOICES = [
        ('dar-es-salaam', 'Dar es Salaam'),
        ('arusha', 'Arusha'),
        ('dodoma', 'Dodoma'),
        ('mbeya', 'Mbeya'),
        ('mwanza', 'Mwanza'),
        ('other', 'Other'),
    ]
    
    EDUCATION_CHOICES = [
        ('primary', 'Primary School'),
        ('secondary', 'Secondary School'),
        ('diploma', 'Diploma'),
        ('bachelor', 'Bachelor\'s Degree'),
        ('master', 'Master\'s Degree'),
        ('phd', 'PhD'),
        ('other', 'Other'),
    ]
    
    REFERRAL_CHOICES = [
        ('friend', 'Friend/Family'),
        ('social-media', 'Social Media'),
        ('event', 'Community Event'),
        ('search', 'Online Search'),
        ('other', 'Other'),
    ]
    
    STATUS_CHOICES = [
        ('pending', 'Pending'),
        ('approved', 'Approved'),
        ('rejected', 'Rejected'),
    ]
    
    # Personal Information
    first_name = models.CharField(max_length=100)
    last_name = models.CharField(max_length=100)
    email = models.EmailField(unique=True)
    phone = models.CharField(max_length=20)
    date_of_birth = models.DateField()
    gender = models.CharField(max_length=20, choices=GENDER_CHOICES)
    id_number = models.CharField(max_length=50, unique=True)
    
    # Background Information
    current_address = models.TextField()
    region = models.CharField(max_length=50, choices=REGION_CHOICES)
    district = models.CharField(max_length=100)
    education = models.CharField(max_length=50, choices=EDUCATION_CHOICES)
    occupation = models.CharField(max_length=200)
    
    # Experience & Skills (stored as JSON)
    work_experience = models.JSONField(default=list, blank=True)
    skills = models.JSONField(default=list, blank=True)
    languages = models.JSONField(default=list, blank=True)
    
    # Motivation
    why_join = models.TextField()
    contribution = models.TextField()
    expectations = models.TextField()
    referral = models.CharField(max_length=50, choices=REFERRAL_CHOICES, blank=True)
    
    # Agreement and Status
    agree_terms = models.BooleanField(default=False)
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='pending')
    
    # Timestamps
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        db_table = 'membership_applications'
        ordering = ['-created_at']
    
    def __str__(self):
        return f"{self.first_name} {self.last_name} - {self.email}"
    
    @property
    def full_name(self):
        return f"{self.first_name} {self.last_name}"
    
    def get_work_experience_display(self):
        """Return formatted work experience"""
        if not self.work_experience:
            return "No work experience provided"
        
        experiences = []
        for exp in self.work_experience:
            if exp.get('job_title') and exp.get('company'):
                experiences.append(f"{exp['job_title']} at {exp['company']}")
        
        return "; ".join(experiences) if experiences else "No work experience provided"
    
    @property
    def duration(self):
        """Calculate duration of employment"""
        if self.start_date and self.end_date:
            return self.end_date - self.start_date
        return None


# models.py
from django.db import models
from django.contrib.auth.models import User
from django.core.validators import MinValueValidator, MaxValueValidator
from django.utils import timezone
from django.db.models import Avg
import uuid

class Event(models.Model):
    EVENT_STATUS = [
        ('upcoming', 'Upcoming'),
        ('ongoing', 'Ongoing'),
        ('completed', 'Completed'),
        ('cancelled', 'Cancelled'),
    ]
    
    EVENT_TYPE = [
        ('workshop', 'Workshop'),
        ('meetup', 'Meetup'),
        ('seminar', 'Seminar'),
        ('conference', 'Conference'),
        ('networking', 'Networking'),
        ('training', 'Training'),
        ('other', 'Other'),
    ]
    
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    title = models.CharField(max_length=200)
    description = models.TextField()
    date = models.DateField(null=True, blank=True)  
    event_type = models.CharField(max_length=20, choices=EVENT_TYPE, default='meetup')
    date_time = models.DateTimeField(null=True, blank=True)
    deadline = models.DateTimeField(null=True, blank=True)
    location = models.CharField(max_length=300)
    is_online = models.BooleanField(default=False)
    max_participants = models.IntegerField(null=True, blank=True)
    price = models.DecimalField(max_digits=10, decimal_places=2, default=0.00)
    requirements = models.TextField(blank=True, help_text="Any requirements or materials needed")
    status = models.CharField(max_length=20, choices=EVENT_STATUS, default='upcoming')
    created_by = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.SET_NULL, null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        ordering = ['date_time']
        
    def __str__(self):
        return self.title
    
    @property
    def is_expired(self):
        return timezone.now() > self.deadline
    
    @property
    def spots_remaining(self):
        if self.max_participants:
            booked = self.bookings.filter(status='confirmed').count()
            return max(0, self.max_participants - booked)
        return None
    
    @property
    def is_full(self):
        if self.max_participants:
            return self.spots_remaining == 0
        return False
    
    def can_book(self):
        return (not self.is_expired and 
                not self.is_full and 
                self.status == 'upcoming')

class CustomUser(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    phone = models.CharField(max_length=20, blank=True)
    bio = models.TextField(blank=True)
    profile_image = models.ImageField(upload_to='profiles/', blank=True, null=True)
    date_joined_community = models.DateTimeField(auto_now_add=True)
    is_community_member = models.BooleanField(default=False)
    is_admin = models.BooleanField(default=False)
    
    def __str__(self):
        return f"{self.user.first_name} {self.user.last_name}"
    
    @property
    def full_name(self):
        return f"{self.user.first_name} {self.user.last_name}"

class EventBooking(models.Model):
    BOOKING_STATUS = [
        ('pending', 'Pending'),
        ('confirmed', 'Confirmed'),
        ('cancelled', 'Cancelled'),
        ('attended', 'Attended'),
    ]
    
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    event = models.ForeignKey(Event, on_delete=models.CASCADE, related_name='bookings')
    user = models.ForeignKey(CustomUser, on_delete=models.CASCADE, related_name='bookings')
    status = models.CharField(max_length=20, choices=BOOKING_STATUS, default='confirmed')
    booked_at = models.DateTimeField(auto_now_add=True)
    notes = models.TextField(blank=True, help_text="Additional notes or requirements")
    
    class Meta:
        unique_together = ['event', 'user']
        ordering = ['-booked_at']
        
    def __str__(self):
        return f"{self.user.full_name} - {self.event.title}"

class CommunityReview(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    user = models.ForeignKey(CustomUser, on_delete=models.CASCADE, related_name='reviews')
    rating = models.IntegerField(
        validators=[MinValueValidator(1), MaxValueValidator(5)],
        help_text="Rating from 1 to 5 stars"
    )
    comment = models.TextField()
    is_public = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        ordering = ['-created_at']
        unique_together = ['user']  # One review per user
        
    def __str__(self):
        return f"{self.user.full_name} - {self.rating} stars"

class TeamMember(models.Model):
    POSITION_CHOICES = [
        ('founder', 'Founder & Director'),
        ('coordinator', 'Programs Coordinator'),
        ('manager', 'Community Manager'),
        ('mentor', 'Senior Mentor'),
        ('advisor', 'Advisor'),
        ('other', 'Other'),
    ]
    
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    name = models.CharField(max_length=100)
    position = models.CharField(max_length=50, choices=POSITION_CHOICES)
    bio = models.TextField()
    quote = models.TextField(help_text="Personal quote or message")
    image = models.ImageField(upload_to='team/', blank=True, null=True)
    email = models.EmailField(blank=True)
    linkedin = models.URLField(blank=True)
    order = models.IntegerField(default=0, help_text="Display order")
    is_active = models.BooleanField(default=True)
    
    class Meta:
        ordering = ['order', 'name']
        
    def __str__(self):
        return f"{self.name} - {self.position}"

class CommunityStats(models.Model):
    """Model to cache community statistics"""
    active_members = models.IntegerField(default=0)
    total_events = models.IntegerField(default=0)
    mentorship_pairs = models.IntegerField(default=0)
    active_projects = models.IntegerField(default=0)
    last_updated = models.DateTimeField(auto_now=True)
    
    class Meta:
        verbose_name_plural = "Community Statistics"
        
    def __str__(self):
        return f"Stats updated: {self.last_updated}"
    
    @classmethod
    def get_current_stats(cls):
        """Get or create current statistics"""
        stats, created = cls.objects.get_or_create(pk=1)
        
        # Update stats if they're older than 1 hour
        if (timezone.now() - stats.last_updated).seconds > 3600 or created:
            stats.active_members = CustomUser.objects.filter(is_community_member=True).count()
            stats.total_events = Event.objects.filter(
                created_at__year=timezone.now().year
            ).count()
            # You can add logic for mentorship pairs and active projects
            stats.save()
            
        return stats

# Management command to clean expired events
# Create this in management/commands/clean_expired_events.py
"""
from django.core.management.base import BaseCommand
from django.utils import timezone
from myapp.models import Event

class Command(BaseCommand):
    help = 'Remove expired events'

    def handle(self, *args, **options):
        expired_events = Event.objects.filter(
            deadline__lt=timezone.now(),
            status='upcoming'
        )
        count = expired_events.count()
        expired_events.delete()
        self.stdout.write(
            self.style.SUCCESS(f'Successfully removed {count} expired events')
        )
"""
