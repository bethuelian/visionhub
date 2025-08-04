# views.py
from django.shortcuts import render, redirect
from django.contrib import messages
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
from django.utils.decorators import method_decorator
from django.views import View
from django.core.mail import send_mail
from django.conf import settings
import json
import logging

logger = logging.getLogger(__name__)

def index(request):
    """Home page with latest upcoming events"""
    # Get next 3 upcoming events
    upcoming_events = Event.objects.filter(
        deadline__gte=timezone.now(),
        status='upcoming'
    ).order_by('date_time')[:3]
    
    context = {
        'upcoming_events': upcoming_events,
    }
    
    return render(request, 'pages/index.html', context)

def about(request):
    """Dynamic about page"""
    # Get active team members
    team_members = TeamMember.objects.filter(is_active=True).order_by('order', 'name')
    
    # Get community stats for impact section
    stats = CommunityStats.get_current_stats()
    
    # Calculate additional stats
    total_members = CustomUser.objects.filter(is_community_member=True).count()
    mentorship_count = 85  # You can implement actual mentorship tracking
    projects_count = 32    # You can implement actual project tracking
    
    context = {
        'team_members': team_members,
        'total_members': total_members,
        'mentorship_count': mentorship_count,
        'projects_count': projects_count,
        'events_this_year': stats.total_events,
    }
    
    return render(request, 'pages/about.html', context)

# views.py
from django.shortcuts import render, get_object_or_404, redirect
from django.http import JsonResponse
from django.contrib.auth.decorators import login_required
from django.contrib.auth import authenticate, login
from django.contrib import messages
from django.utils import timezone
from django.core.paginator import Paginator
from django.db.models import Q
import json
from .models import Event, EventBooking, CommunityReview, CommunityStats, TeamMember, CustomUser

def community(request):
    """Community hub view with events, stats, and reviews"""
    # Get upcoming events (not expired)
    events = Event.objects.filter(
        deadline__gte=timezone.now(),
        status='upcoming'
    ).order_by('date_time')
    
    # Get community statistics
    stats = CommunityStats.get_current_stats()
    
    # Get recent reviews (public only)
    reviews = CommunityReview.objects.filter(
        is_public=True
    ).select_related('user')[:6]
    
    # Get user's bookings if authenticated
    user_bookings = []
    if request.user.is_authenticated:
        try:
            custom_user = request.user.customuser
            user_bookings = EventBooking.objects.filter(
                user=custom_user,
                status='confirmed'
            ).values_list('event_id', flat=True)
        except CustomUser.DoesNotExist:
            user_bookings = []
    
    context = {
        'events': events,
        'stats': stats,
        'reviews': reviews,
        'user_bookings': user_bookings,
    }
    
    return render(request, 'pages/community.html', context)

@login_required
def book_event_view(request):
    """Handle event booking"""
    if request.method != 'POST':
        return JsonResponse({'success': False, 'message': 'Invalid request method'})
    
    try:
        # Check if user is a community member
        custom_user = request.user.customuser
        if not custom_user.is_community_member:
            return JsonResponse({
                'success': False, 
                'message': 'You must be a community member to book events'
            })
        
        data = json.loads(request.body)
        event_id = data.get('event_id')
        
        event = get_object_or_404(Event, id=event_id)
        
        # Check if event can be booked
        if not event.can_book():
            return JsonResponse({
                'success': False,
                'message': 'This event cannot be booked (expired, full, or cancelled)'
            })
        
        # Check if user already booked this event
        existing_booking = EventBooking.objects.filter(
            event=event,
            user=custom_user
        ).first()
        
        if existing_booking:
            return JsonResponse({
                'success': False,
                'message': 'You have already booked this event'
            })
        
        # Create booking
        booking = EventBooking.objects.create(
            event=event,
            user=custom_user,
            status='confirmed'
        )
        
        return JsonResponse({
            'success': True,
            'message': 'Event booked successfully!',
            'booking_id': str(booking.id)
        })
        
    except CustomUser.DoesNotExist:
        return JsonResponse({
            'success': False,
            'message': 'User profile not found. Please complete your profile.'
        })
    except Exception as e:
        return JsonResponse({
            'success': False,
            'message': 'An error occurred while booking the event'
        })

@login_required
def submit_review_view(request):
    """Handle community review submission"""
    if request.method != 'POST':
        return JsonResponse({'success': False, 'message': 'Invalid request method'})
    
    try:
        # Check if user is a community member
        custom_user = request.user.customuser
        if not custom_user.is_community_member:
            return JsonResponse({
                'success': False,
                'message': 'You must be a community member to submit reviews'
            })
        
        rating = int(request.POST.get('rating', 0))
        comment = request.POST.get('comment', '').strip()
        
        if rating < 1 or rating > 5:
            return JsonResponse({
                'success': False,
                'message': 'Rating must be between 1 and 5 stars'
            })
        
        if not comment:
            return JsonResponse({
                'success': False,
                'message': 'Comment is required'
            })
        
        # Check if user already has a review (update if exists)
        review, created = CommunityReview.objects.update_or_create(
            user=custom_user,
            defaults={
                'rating': rating,
                'comment': comment,
                'is_public': True
            }
        )
        
        return JsonResponse({
            'success': True,
            'message': 'Review submitted successfully!' if created else 'Review updated successfully!'
        })
        
    except CustomUser.DoesNotExist:
        return JsonResponse({
            'success': False,
            'message': 'User profile not found'
        })
    except ValueError:
        return JsonResponse({
            'success': False,
            'message': 'Invalid rating value'
        })
    except Exception as e:
        return JsonResponse({
            'success': False,
            'message': 'An error occurred while submitting your review'
        })





# Admin Panel Views
@login_required
def dashboard(request):
    """Admin panel dashboard - only for admins"""
    try:
        custom_user = request.user.customuser
        if not custom_user.is_admin and not request.user.is_superuser:
            messages.error(request, 'Access denied. Admin privileges required.')
            return redirect('home')
    except CustomUser.DoesNotExist:
        messages.error(request, 'Access denied. User profile not found.')
        return redirect('home')
    
    # Get dashboard statistics
    total_members = CustomUser.objects.filter(is_community_member=True).count()
    pending_applications = MembershipApplication.objects.filter(status='pending').count()
    total_events = Event.objects.count()
    upcoming_events = Event.objects.filter(deadline__gte=timezone.now()).count()
    total_bookings = EventBooking.objects.filter(status='confirmed').count()
    total_reviews = CommunityReview.objects.count()
    
    # Recent activity
    recent_applications = MembershipApplication.objects.filter(
        status='pending'
    ).order_by('-created_at')[:5]
    
    recent_bookings = EventBooking.objects.filter(
        status='confirmed'
    ).select_related('user', 'event').order_by('-booked_at')[:5]
    
    context = {
        'total_members': total_members,
        'pending_applications': pending_applications,
        'total_events': total_events,
        'upcoming_events': upcoming_events,
        'total_bookings': total_bookings,
        'total_reviews': total_reviews,
        'recent_applications': recent_applications,
        'recent_bookings': recent_bookings,
    }
    
    return render(request, 'pages/dashboard.html', context)

@login_required
def admin_events_view(request):
    """Admin events management"""
    try:
        custom_user = request.user.customuser
        if not custom_user.is_admin and not request.user.is_superuser:
            return redirect('home')
    except CustomUser.DoesNotExist:
        return redirect('home')
    
    events = Event.objects.all().order_by('-created_at')
    
    context = {
        'events': events,
    }
    
    return render(request, 'admin/events.html', context)

@login_required
def admin_members_view(request):
    """Admin members management"""
    try:
        custom_user = request.user.customuser
        if not custom_user.is_admin and not request.user.is_superuser:
            return redirect('home')
    except CustomUser.DoesNotExist:
        return redirect('home')
    
    members = CustomUser.objects.filter(is_community_member=True).select_related('user')
    pending_applications = MembershipApplication.objects.filter(status='pending')
    
    context = {
        'members': members,
        'pending_applications': pending_applications,
    }
    
    return render(request, 'admin/members.html', context)

@login_required
def admin_team_view(request):
    """Admin team management"""
    try:
        custom_user = request.user.customuser
        if not custom_user.is_admin and not request.user.is_superuser:
            return redirect('home')
    except CustomUser.DoesNotExist:
        return redirect('home')
    
    team_members = TeamMember.objects.all().order_by('order', 'name')
    
    context = {
        'team_members': team_members,
    }
    
    return render(request, 'admin/team.html', context)

@login_required
def create_event_view(request):
    """Create new event"""
    try:
        custom_user = request.user.customuser
        if not custom_user.is_admin and not request.user.is_superuser:
            return redirect('home')
    except CustomUser.DoesNotExist:
        return redirect('home')
    
    if request.method == 'POST':
        try:
            event = Event.objects.create(
                title=request.POST.get('title'),
                description=request.POST.get('description'),
                event_type=request.POST.get('event_type'),
                date_time=request.POST.get('date_time'),
                deadline=request.POST.get('deadline'),
                location=request.POST.get('location'),
                is_online=request.POST.get('is_online') == 'on',
                max_participants=int(request.POST.get('max_participants') or 0) or None,
                price=float(request.POST.get('price') or 0),
                requirements=request.POST.get('requirements', ''),
                created_by=custom_user
            )
            
            messages.success(request, 'Event created successfully!')
            return redirect('admin_events')
            
        except Exception as e:
            messages.error(request, f'Error creating event: {str(e)}')
    
    return render(request, 'admin/create_event.html')

# Utility function to clean expired events (can be called via cron job)
def clean_expired_events():
    """Remove expired events"""
    expired_events = Event.objects.filter(
        deadline__lt=timezone.now(),
        status='upcoming'
    )
    count = expired_events.count()
    expired_events.delete()
    return count

from django.shortcuts import render, redirect
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
from django.views.decorators.http import require_http_methods
from django.contrib import messages
import json
from .models import MembershipApplication

def join(request):
    """Render the membership form"""
    if request.method == 'GET':
        return render(request, 'pages/join.html')
    
    elif request.method == 'POST':
        try:
            # Handle JSON data from AJAX request
            if request.content_type == 'application/json':
                data = json.loads(request.body)
            else:
                # Handle regular form submission
                data = request.POST.dict()
            
            # Process work experience data
            work_experiences = []
            experience_count = 1
            
            while f'job_title_{experience_count}' in data:
                if data.get(f'job_title_{experience_count}'):
                    work_exp = {
                        'job_title': data.get(f'job_title_{experience_count}', ''),
                        'company': data.get(f'company_{experience_count}', ''),
                        'start_date': data.get(f'start_date_{experience_count}', ''),
                        'end_date': data.get(f'end_date_{experience_count}', ''),
                        'responsibilities': data.get(f'responsibilities_{experience_count}', ''),
                    }
                    work_experiences.append(work_exp)
                experience_count += 1
            
            # Process skills
            skills = []
            if 'skills' in data:
                if isinstance(data['skills'], str):
                    try:
                        skills = json.loads(data['skills'])
                    except json.JSONDecodeError:
                        skills = [data['skills']] if data['skills'] else []
                elif isinstance(data['skills'], list):
                    skills = data['skills']
            
            # Process languages
            languages = []
            if 'languages' in data:
                if isinstance(data['languages'], list):
                    languages = data['languages']
                else:
                    languages = [data['languages']] if data['languages'] else []
            
            # Create membership application
            application = MembershipApplication.objects.create(
                first_name=data.get('first_name', ''),
                last_name=data.get('last_name', ''),
                email=data.get('email', ''),
                phone=data.get('phone', ''),
                date_of_birth=data.get('date_of_birth'),
                gender=data.get('gender', ''),
                id_number=data.get('id_number', ''),
                current_address=data.get('current_address', ''),
                region=data.get('region', ''),
                district=data.get('district', ''),
                education=data.get('education', ''),
                occupation=data.get('occupation', ''),
                work_experience=work_experiences,
                skills=skills,
                languages=languages,
                why_join=data.get('why_join', ''),
                contribution=data.get('contribution', ''),
                expectations=data.get('expectations', ''),
                referral=data.get('referral', ''),
                agree_terms=data.get('agree_terms') == 'on' or data.get('agree_terms') is True,
            )
            
            # Return success response
            if request.content_type == 'application/json':
                return JsonResponse({
                    'success': True,
                    'message': 'Application submitted successfully!',
                    'application_id': application.id
                })
            else:
                messages.success(request, 'Your application has been submitted successfully!')
                return redirect('join_success')
                
        except Exception as e:
            print(f"Error processing membership application: {str(e)}")
            
            if request.content_type == 'application/json':
                return JsonResponse({
                    'success': False,
                    'message': 'There was an error submitting your application. Please try again.'
                }, status=400)
            else:
                messages.error(request, 'There was an error submitting your application. Please try again.')
                return render(request, 'pages/join.html')

def join_success(request):
    """Thank you page after successful submission"""
    return render(request, 'pages/join_success.html')

@csrf_exempt
def api_chat_message(request):
    """API endpoint for chat messages (if you want to implement real-time chat)"""
    if request.method == 'POST':
        try:
            data = json.loads(request.body)
            message = data.get('message', '').strip()
            
            if not message:
                return JsonResponse({'error': 'Message is required'}, status=400)
            
            # Here you would typically save the message and broadcast it
            # For now, we'll just return a simple response
            
            response_message = generate_chat_response(message)
            
            return JsonResponse({
                'success': True,
                'response': response_message
            })
            
        except json.JSONDecodeError:
            return JsonResponse({'error': 'Invalid JSON'}, status=400)
        except Exception as e:
            logger.error(f"Error processing chat message: {str(e)}")
            return JsonResponse({'error': 'Internal server error'}, status=500)
    
    return JsonResponse({'error': 'Method not allowed'}, status=405)

def generate_chat_response(message):
    """Generate a simple chat response (you could make this more sophisticated)"""
    message_lower = message.lower()
    
    if any(word in message_lower for word in ['hello', 'hi', 'hey']):
        return "Hello! Welcome to Vision Hub Tanzania. How can we help you today?"
    elif any(word in message_lower for word in ['event', 'events']):
        return "We have several upcoming events! Check out our events section for more details and booking information."
    elif any(word in message_lower for word in ['join', 'membership']):
        return "Great to hear you're interested in joining us! Please fill out our membership application form to get started."
    elif any(word in message_lower for word in ['help', 'support']):
        return "Our community moderators are here to help! You can also reach out to us directly via email."
    else:
        return "Thanks for your message! A community moderator will respond to you soon."

# Error handlers
def handler404(request, exception):
    """Custom 404 error handler"""
    return render(request, '404.html', status=404)

def handler500(request):
    """Custom 500 error handler"""
    return render(request, '500.html', status=500)