import json
import logging
import os
import random
from datetime import timedelta
from django.conf import settings
from django.contrib import messages
from django.contrib.auth import authenticate, logout, login as auth_login
from django.contrib.auth.decorators import login_required
from django.contrib.auth.hashers import check_password, make_password
from django.contrib.auth.models import AbstractUser
from django.db import models
from django.db.models import Q
from django.http import HttpResponse, HttpResponseRedirect, JsonResponse
from django.shortcuts import render, redirect, get_object_or_404
from django.template.loader import render_to_string
from django.utils import timezone
from django.views.decorators.csrf import csrf_exempt, csrf_protect
from twilio.rest import Client
from .models import (
    Login, Notification, Message, Post, Like, Comment, Story, StoryMessage,
    StoryViewer, SharedPost, Follow
)
from django.contrib.auth import get_user_model
from django.http import JsonResponse, HttpResponseForbidden






import random
from django.shortcuts import render, redirect
from django.core.mail import send_mail
from django.contrib.auth.hashers import make_password
from .models import Login, PendingOTP

def register(request):
    if request.method == 'POST':
        if 'otp' in request.POST:
            return verify_otp(request)

        username = request.POST.get('username')
        password = request.POST.get('password')
        email = request.POST.get('gmail')

        if Login.objects.filter(username=username).exists():
            return render(request, 'register.html', {'error': 'Username already exists'})
        if Login.objects.filter(email=email).exists():
            return render(request, 'register.html', {'error': 'Email already registered'})

        # Optional: remove old OTPs
        PendingOTP.objects.filter(email=email).delete()

        otp = str(random.randint(100000, 999999))

        PendingOTP.objects.create(
            email=email,
            otp=otp,
            username=username,
            password=password
        )

        send_mail(
            'Kitchat OTP Verification',
            f'Your OTP is: {otp}',
            'yourgmail@gmail.com',
            [email],
            fail_silently=False,
        )

        return render(request, 'register.html', {'email': email})

    return render(request, 'register.html')


from django.contrib.auth.hashers import make_password

def verify_otp(request):
    if request.method == 'POST':
        email = request.POST.get('email')
        entered_otp = request.POST.get('otp')

        # Safely get the latest OTP entry
        record = PendingOTP.objects.filter(email=email).order_by('-id').first()

        if not record:
            return render(request, 'register.html', {'error': 'Invalid email'})

        if record.otp == entered_otp:
            hashed_password = make_password(record.password)

            Login.objects.create(
                username=record.username,
                password=hashed_password,
                email=record.email
            )

            PendingOTP.objects.filter(email=email).delete()
            return redirect('loginform')

        else:
            return render(request, 'register.html', {'email': email, 'error': 'Incorrect OTP'})

    return redirect('register')









def success(request):
    return render(request, 'success.html')


from django.contrib.auth import authenticate, login as auth_login
from django.contrib import messages
from django.shortcuts import render, redirect
from django.http import JsonResponse
import random, string
from django.contrib.auth.models import User

def loginform(request):
    if 'captcha_text' not in request.session:
        request.session['captcha_text'] = generate_captcha()

    if request.method == 'POST':
        identifier = request.POST.get('username')  # could be username or email
        password = request.POST.get('password')
        user_captcha = request.POST.get('captcha', '').upper()
        server_captcha = request.session.get('captcha_text', '')

        # CAPTCHA validation
        if not user_captcha:
            messages.error(request, 'CAPTCHA not entered.')
        elif user_captcha != server_captcha:
            messages.error(request, 'Invalid CAPTCHA. Please try again.')
        else:
            # Try to find user by username or email
            user = User.objects.filter(Q(username=identifier) | Q(email=identifier)).first()
            if not user:
                messages.error(request, 'User does not exist.')
            elif not check_password(password, user.password):
                messages.error(request, 'Incorrect password.')
            else:
                # Authenticate and login using username
                user = authenticate(request, username=user.username, password=password)
                if user:
                    auth_login(request, user)
                    del request.session['captcha_text']
                    return redirect('loginsuccess')
                else:
                    messages.error(request, 'Authentication failed.')

        # regenerate CAPTCHA if there was any error
        request.session['captcha_text'] = generate_captcha()

    return render(request, 'loginform.html', {'captcha_text': request.session['captcha_text']})

def generate_captcha():
    # Create a 6-character CAPTCHA with 4 letters and 2 numbers
    letters = ''.join(random.choices(string.ascii_uppercase, k=4))
    numbers = ''.join(random.choices(string.digits, k=2))
    captcha = list(letters + numbers)
    random.shuffle(captcha)
    return ''.join(captcha)

def refresh_captcha(request):
    if request.method == 'GET' and request.headers.get('X-Requested-With') == 'XMLHttpRequest':
        captcha_text = generate_captcha()
        request.session['captcha_text'] = captcha_text
        return JsonResponse({'captcha_text': captcha_text})
    return JsonResponse({}, status=400)







def forget(request):
    if request.method == 'POST':
        step = request.POST.get('step')

        if step == 'send_otp':
            email = request.POST.get('email')
            user = Login.objects.filter(email=email).first()

            if user:
                otp = str(random.randint(100000, 999999))
                request.session['reset_email'] = email
                request.session['reset_otp'] = otp

                send_mail(
                    'Your OTP for Password Reset',
                    f'Your OTP is: {otp}',
                    settings.DEFAULT_FROM_EMAIL,
                    [email],
                    fail_silently=False,
                )

                return render(request, 'forget.html', {'step': 'verify_otp', 'email': email})
            else:
                return render(request, 'forget.html', {'error': 'Email not registered', 'step': 'send_otp'})

        elif step == 'verify_otp':
            otp = request.POST.get('otp')
            if otp == request.session.get('reset_otp'):
                return render(request, 'forget.html', {'step': 'reset_password'})
            else:
                return render(request, 'forget.html', {'error': 'Invalid OTP', 'step': 'verify_otp'})

        elif step == 'reset_password':
            new_password = request.POST.get('new_password')
            confirm_password = request.POST.get('confirm_password')

            if new_password != confirm_password:
                return render(request, 'forget.html', {'error': 'Passwords do not match', 'step': 'reset_password'})

            email = request.session.get('reset_email')
            user = Login.objects.filter(email=email).first()

            if user:
                user.set_password(new_password)  # Assumes you have set_password method or use make_password
                user.save()
                request.session.flush()
                return redirect('success')

    return render(request, 'forget.html', {'step': 'send_otp'})



def otp(request):
    return render(request, 'otp.html')

def newpass(request):
    return render(request, 'newpass.html')
from django.views.decorators.http import require_POST


from django.contrib.auth.decorators import login_required
from django.utils import timezone
from django.shortcuts import render
import random
from .models import Follow, Post, Story

@login_required(login_url='/loginform/')
def loginsuccess(request):
    current_user = request.user

    # Step 1: Get IDs of users the current user follows
    following_ids = set(Follow.objects.filter(follower=current_user).values_list('followed_id', flat=True))

    # Step 2: Get IDs of users who follow the current user
    followers_ids = set(Follow.objects.filter(followed=current_user).values_list('follower_id', flat=True))

    # Step 3: Calculate mutual follows (users you follow AND they follow you back)
    mutual_follow_ids = following_ids.intersection(followers_ids)

    # Step 4: Fetch unexpired stories only from mutual follows
    stories = Story.objects.filter(
        expires_at__gt=timezone.now(),
        user__id__in=mutual_follow_ids
    ).select_related('user')

    # Group stories by user
    stories_by_user = {}
    for story in stories:
        if story.user.username not in stories_by_user:
            stories_by_user[story.user.username] = {
                'user': story.user,
                'stories': []
            }
        stories_by_user[story.user.username]['stories'].append(story)

    # Build story data for template
    story_details = []
    for username, data in stories_by_user.items():
        story_details.append({
            'username': username,
            'user_image_url': data['user'].image.url if data['user'].image else '/static/default-avatar.png',
            'stories': [{
                'id': story.id,
                'image_url': story.image.url if story.image else None,
                'video_url': story.video.url if story.video else None,
                'text_content': story.text_content if story.type == 'text' else None,
                'type': story.type,
            } for story in data['stories']]
        })

    # Fetch all posts and filter by privacy settings
    all_posts = Post.objects.select_related('user')
    filtered_posts = []

    for post in all_posts:
        user = post.user
        if not user.private_account:
            # Public account: show the post
            filtered_posts.append(post)
        else:
            # Private account: show only if mutual follow
            if (Follow.objects.filter(follower=request.user, followed=user).exists() and
                    Follow.objects.filter(follower=user, followed=request.user).exists()):
                filtered_posts.append(post)

    random.shuffle(filtered_posts)

    # Build post data for template
    post_details = []
    for post in filtered_posts:
        post_details.append({
            'id': post.id,
            'user': post.user,
            'user_image_url': post.user.image.url if post.user.image else '/static/default-avatar.png',
            'image_url': post.image.url if post.image else '/static/default-post.png',
            'video_url': post.video.url if post.video else None,
            'caption': post.caption,
            'likes_count': post.likes_count,
            'comments_count': post.comments_count,
            'shares_count': post.shares_count,
        })

    # Get IDs of users the current user is following
    current_user_following_ids = set()
    if request.user.is_authenticated:
        current_user_following_ids = set(Follow.objects.filter(follower=request.user).values_list('followed_id', flat=True))

    return render(request, 'loginsuccess.html', {
        'username': current_user.username,
        'image_url': current_user.image.url if current_user.image else '/static/default-avatar.png',
        'posts': post_details,  # ✅ Correctly pass filtered and processed posts
        'stories': story_details,
        'current_user_following_ids': current_user_following_ids,
    })

def get_stories_by_user(request):
    username = request.GET.get('username')
    if not username:
        return JsonResponse({"status": "error", "message": "Username required"}, status=400)

    user_stories = Story.objects.filter(user__username=username, expires_at__gt=timezone.now()).order_by('created_at')

    stories_list = [{
        "id": story.id,
        "image_url": story.image.url if story.image else None,
        "video_url": story.video.url if story.video else None,
        "text_content": story.text_content if story.type == "text" else None,
        "type": story.type,
    } for story in user_stories]
    
    return JsonResponse({"status": "success", "stories": stories_list})
@csrf_exempt
@login_required
@require_POST
def react_to_story(request, story_id):
    story = get_object_or_404(Story, id=story_id)
    reaction_type = request.POST.get('reaction_type')
    
    if reaction_type not in dict(StoryReaction.REACTION_CHOICES):
        return JsonResponse({'status': 'error', 'message': 'Invalid reaction type'})
    
    # Create or update reaction
    reaction, created = StoryReaction.objects.update_or_create(
        viewer=request.user,
        story=story,
        defaults={'reaction_type': reaction_type}
    )
    
    # Create message for the reaction
    reaction_emoji = dict(StoryReaction.REACTION_CHOICES)[reaction_type]
    reaction_message = f"Reacted with {reaction_emoji} to your story"
    
    message = Message.objects.create(
        sender=request.user,
        recipient=story.user,
        content=reaction_message,
        related_story=story,
        is_reaction=True,
        reaction_type=reaction_type
    )
    
    # Return the message ID for potential WebSocket use
    return JsonResponse({
        'status': 'success', 
        'reaction_id': reaction.id,
        'message_id': message.id,
        'reaction_emoji': reaction_emoji
    })
@csrf_exempt
def send_story_message(request, story_id):
    if request.method == 'POST':
        user_id = request.session.get('user_id')
        user = Login.objects.get(id=user_id)
        story = get_object_or_404(Story, id=story_id)
        content = request.POST.get('content', '').strip()
        if content:
            message = StoryMessage.objects.create(user=user, story=story, content=content)
            return JsonResponse({'success': True, 'message_id': message.id})
        return JsonResponse({'success': False, 'message': 'Empty content'}, status=400)
    return JsonResponse({'success': False, 'message': 'Invalid request method'}, status=400)


@login_required
def get_all_stories(request):
    try:
        users_stories = []
        users = Login.objects.prefetch_related("story")  # ✅ Correct related name

        for user in users:
            user_stories = list(user.story.values("id", "image", "created_at"))  # ✅ Fetch related stories
            if user_stories:
                users_stories.append({
                    "username": user.username,
                    "user_image_url": user.image.url if user.image else "",
                    "stories": user_stories
                })

        return JsonResponse({"users_stories": users_stories}, safe=False)

    except Exception as e:
        return JsonResponse({"error": str(e)}, status=500)

User = get_user_model()

def story_list(request):
    users_with_stories = User.objects.filter(stories__isnull=False).distinct()
    user_stories = {user: user.stories.order_by("created_at") for user in users_with_stories}
    
    return render(request, "story_list.html", {"user_stories": user_stories})

from .utils import notify_new_message
def latest_story(request):
    last_story = Story.objects.order_by('-created_at').first()  # Get latest story
    return render(request, 'latest_story.html', {'last_story': last_story})
@login_required
@require_POST
def send_story_message(request, story_id):
    story = get_object_or_404(Story, id=story_id)
    content = request.POST.get('message', '').strip()
    
    if content:
        # Create new message
        message = Message.objects.create(
            sender=request.user,
            recipient=story.user,  # Story creator
            content=content,
            related_story=story
        )
        
        # Include story context in the message
        story_preview = f"Story from {story.created_at.strftime('%d %b %Y')}"
        
        # Send notification through websocket if implemented
        notify_new_message(story.user.id, {
            'type': 'new_message',
            'message_id': message.id,
            'sender_name': request.user.username,
            'sender_pic': request.user.profile_picture.url if hasattr(request.user, 'profile_picture') and request.user.profile_picture else '/static/images/default_profile.jpg',
            'content': content,
            'timestamp': message.timestamp.isoformat(),
            'story_context': story_preview
        })
        
        return JsonResponse({'status': 'success', 'message_id': message.id})
    
    return JsonResponse({'status': 'error', 'message': 'Empty message'})
from .models import StoryMessage,StoryReaction
# Add to views.py - Function to react to a story
@login_required
@require_POST
def react_to_story(request, story_id):
    story = get_object_or_404(Story, id=story_id)
    reaction_type = request.POST.get('reaction_type')
    
    if reaction_type not in dict(StoryReaction.REACTION_CHOICES):
        return JsonResponse({'status': 'error', 'message': 'Invalid reaction type'})
    
    # Create or update reaction
    reaction, created = StoryReaction.objects.update_or_create(
        viewer=request.user,
        story=story,
        defaults={'reaction_type': reaction_type}
    )
    
    # Create message for the reaction
    reaction_emoji = dict(StoryReaction.REACTION_CHOICES)[reaction_type]
    reaction_message = f"Reacted with {reaction_emoji} to your story"
    
    message = Message.objects.create(
        sender=request.user,
        recipient=story.user,
        content=reaction_message,
        related_story=story,
        is_reaction=True,
        reaction_type=reaction_type
    )
    
    # Send notification through websocket if implemented
    notify_new_message(story.user.id, {
        'type': 'new_message',
        'message_id': message.id,
        'sender_name': request.user.username,
        'sender_pic': request.user.profile_picture.url if hasattr(request.user, 'profile_picture') and request.user.profile_picture else '/static/images/default_profile.jpg',
        'content': reaction_message,
        'timestamp': message.timestamp.isoformat(),
        'is_reaction': True,
        'reaction_type': reaction_type
    })
    
    return JsonResponse({
        'status': 'success', 
        'reaction_id': reaction.id,
        'message_id': message.id
    })

@login_required
def view_story(request, username):
    # Calculate the time 24 hours ago
    twenty_four_hours_ago = timezone.now() - timedelta(hours=24)
    
    # Get user and their stories
    user_story = get_object_or_404(User, username=username)
    stories = Story.objects.filter(
        user=user_story,
        created_at__gte=twenty_four_hours_ago
    ).order_by('created_at')

    viewers_data = {}
    reactions_data = {}

    # Mark stories as viewed if the current user is viewing them
    if request.user.is_authenticated:
        for story in stories:
            story_viewer, created = StoryViewer.objects.get_or_create(
                viewer=request.user,
                story=story,
                defaults={'viewed_at': timezone.now()}
            )
            if created:
                story_viewer.viewed_at = timezone.now()
                story_viewer.save()
            
            # Fetch all viewers for the story
            viewers = []
            for viewer in story.viewers.all():
                viewed_at_entry = StoryViewer.objects.filter(viewer=viewer, story=story).first()
                viewed_at = viewed_at_entry.viewed_at if viewed_at_entry else None
                
                # Get reaction for this viewer if any
                reaction = StoryReaction.objects.filter(viewer=viewer, story=story).first()
                reaction_emoji = dict(StoryReaction.REACTION_CHOICES).get(reaction.reaction_type, '') if reaction else ''
                
                viewers.append({
                    "username": viewer.username,
                    "profile_pic": viewer.profile_picture.url if hasattr(viewer, 'profile_picture') and viewer.profile_picture else "/static/images/default_profile.jpg",
                    "viewed_at": viewed_at.strftime('%Y-%m-%d %H:%M:%S') if viewed_at else None,
                    "reaction": reaction_emoji,
                    "reaction_type": reaction.reaction_type if reaction else None
                })
            
            viewers_data[story.id] = viewers
            
            # Get reaction counts for each story
            reaction_counts = StoryReaction.objects.filter(story=story).values('reaction_type').annotate(count=models.Count('id'))
            reactions_data[story.id] = {
                item['reaction_type']: item['count'] for item in reaction_counts
            }

    if not stories.exists():
        return render(request, 'stories/no_stories.html', {
            'message': f"{username} has no active stories (stories disappear after 24 hours)"
        })

    context = {
        'stories': stories,
        'username': username,
        'user_story': user_story,  # Pass the user who posted the story
        'viewers_data': viewers_data,
        'reactions_data': reactions_data
    }
    
    return render(request, 'view_story.html', context)
from django.views.decorators.http import require_POST
# views.py
@login_required
def story_viewers(request, story_id):
    story = get_object_or_404(Story, id=story_id)
    viewers = StoryViewer.objects.filter(story=story).select_related('viewer')
    
    viewers_data = []
    for viewer in viewers:
        # Get reaction for this viewer
        reaction = StoryReaction.objects.filter(
            viewer=viewer.viewer, 
            story=story
        ).first()
        
        viewers_data.append({
            'username': viewer.viewer.username,
            'profile_pic': viewer.viewer.profile_picture.url if viewer.viewer.profile_picture else '/static/images/default_profile.jpg',
            'viewed_at': viewer.viewed_at.strftime('%Y-%m-%d %H:%M:%S'),
            'reaction': reaction.emoji if reaction else None,
            'reaction_type': reaction.reaction_type if reaction else None
        })
    
    return JsonResponse({
        'viewers': viewers_data
    })
    
from django.http import HttpResponseForbidden

# views.py
from django.views.decorators.http import require_POST


@require_POST 
@login_required 
def delete_story(request, story_id):
    try:
        story = get_object_or_404(Story, id=story_id)
        
        # Verify user owns the story 
        if story.user != request.user: 
            return JsonResponse({'error': 'You are not allowed to delete this story.'}, status=403) 
         
        story.delete() 
        return JsonResponse({'status': 'success'})
        
    except Exception as e:
        # Log the error for debugging
        print(f"Error deleting story: {e}")
        return JsonResponse({'error': 'Internal server error'}, status=500)





def edit_profile(request):
    return render(request, 'edit_profile.html')
def get_story(request, story_id):
    story = get_object_or_404(Story, id=story_id)
    return JsonResponse({
        'id': story.id,
        'user': story.user.username,
        'image': story.image.url if story.image else '',
        'video': story.video.url if story.video else '',
        'created_at': story.created_at.strftime("%Y-%m-%d %H:%M:%S")
    })
from .models import SearchHistory

@login_required(login_url='/loginform/')
def search(request):
    if request.method == "GET" and "query" in request.GET:
        query = request.GET.get("query", "").strip()
        
        if not query:
            return JsonResponse({"success": False, "error": "No query provided"})

        users = Login.objects.filter(username__icontains=query)
        # 2. Save search history (original query)
        if request.user.is_authenticated and users.exists():
          try:
            SearchHistory.objects.create(
            user=request.user,
            query=query,
            created_at=timezone.now()
        )
          except Exception as e:
              print("Error saving search history:", e)
  
        current_user_following_ids = []
        if request.user.is_authenticated:
            current_user_following_ids = Follow.objects.filter(
                follower=request.user
            ).values_list('followed_id', flat=True)

        results = [
            {
                "id": user.id,
                "username": user.username,
                "image_url": user.image.url if user.image else "/static/default-avatar.png",
                "is_following": user.id in current_user_following_ids,
            }
            for user in users
        ]
       
        return JsonResponse({"success": True, "results": results})

    return render(request, "search.html")


from django.views.decorators.http import require_POST
# views.py
from django.views.decorators.http import require_POST
from django.http import JsonResponse

@login_required
@require_POST
def save_search_history(request):
    query = request.POST.get("query", "").strip()

    # Enforce minimum length
    if len(query) < 3:
        return JsonResponse({"success": False, "error": "Query too short"})

    # Optional: prevent duplicates
    from .models import SearchHistory
    if not SearchHistory.objects.filter(user=request.user, query=query).exists():
        SearchHistory.objects.create(user=request.user, query=query)

    return JsonResponse({"success": True})




@login_required
def get_search_history(request):
    history = SearchHistory.objects.filter(user=request.user).order_by('-created_at')[:10]
    data = []

    for item in history:
        try:
            matched_user = Login.objects.get(username__iexact=item.query)
            data.append({
                "id": item.id,
                "username": matched_user.username,
                "image_url": matched_user.image.url if matched_user.image else "/static/default-avatar.png",
                "user_id": matched_user.id,
                "timestamp": item.created_at.strftime('%Y-%m-%d %H:%M:%S')
            })
        except Login.DoesNotExist:
            # fallback to raw query if user no longer exists
            data.append({
                "id": item.id,
                "username": item.query,
                "image_url": "/static/default-avatar.png",
                "user_id": None,
                "timestamp": item.created_at.strftime('%Y-%m-%d %H:%M:%S')
            })

    return JsonResponse({"success": True, "history": data})




@require_POST
@login_required
def delete_search_history(request, history_id):
    try:
        history = SearchHistory.objects.get(id=history_id, user=request.user)
        history.delete()
        return JsonResponse({"success": True})
    except SearchHistory.DoesNotExist:
        return JsonResponse({"success": False, "error": "Item not found"})


@login_required
def unfollow_user(request, user_id):
    user_to_unfollow = get_object_or_404(Login, id=user_id)
    
    if request.user.is_following(user_to_unfollow):
        # Remove follow relationship
        Follow.objects.filter(
            follower=request.user,
            followed=user_to_unfollow
        ).delete()
        
        # Create unfollow notification
        Notification.objects.create(
            user=user_to_unfollow,
            triggered_by=request.user,
            notification_type='unfollow',
            message=f"{request.user.username} unfollowed you"
        )
        
        return JsonResponse({
            'success': True,
            'action': 'unfollowed',
            'followers_count': user_to_unfollow.followers.count()
        })
    else:
        return JsonResponse({
            'success': False,
            'error': 'Not following this user'
        }, status=400)
# User Profile


@login_required(login_url='/loginform/')
def notifications(request):
    notifications = Notification.objects.filter(user=request.user).select_related('triggered_by')
    notification_data = []
    
    # Mark all notifications as seen when the page is loaded
    Notification.objects.filter(user=request.user, is_seen=False).update(is_seen=True)
    
    unseen_count = Notification.objects.filter(user=request.user, is_seen=False).count()
    
    for notification in notifications:
        username = "System"
        profile_image = "/media/default-profile.png"
        
        if notification.triggered_by:
            username = notification.triggered_by.username
            if hasattr(notification.triggered_by, 'image') and notification.triggered_by.image:
                profile_image = notification.triggered_by.image.url
            else:
                print(f"⚠️ No image found for {username}")

        notification_data.append({
            "id": notification.id,
            "message": notification.message,
            "timestamp": notification.timestamp.strftime('%Y-%m-%d %H:%M:%S'),
            "username": username,
            "user_profile_image": profile_image,
            "notification_type": notification.notification_type,
            "is_seen": notification.is_seen,
        })

    return render(request, "notifications.html", {
        "notifications": notification_data,
        "unseen_count": unseen_count,
    })
@login_required
def check_new_notifications(request):
    unseen_count = Notification.objects.filter(
        user=request.user, 
        is_seen=False
    ).count()
    return JsonResponse({'unseen_count': unseen_count})
@login_required
def mark_notifications_seen(request):
    Notification.objects.filter(user=request.user, is_seen=False).update(is_seen=True)
    return JsonResponse({'success': True})

@login_required
def mark_notification_seen(request, notification_id):
    try:
        notification = Notification.objects.get(id=notification_id, user=request.user)
        notification.is_seen = True
        notification.save()
        return JsonResponse({'success': True})
    except Notification.DoesNotExist:
        return JsonResponse({'success': False}, status=404)
@login_required
def check_new_messages(request):
    unseen_count = Message.objects.filter(recipient=request.user, is_seen=False).count()
    return JsonResponse({'unseen_count': unseen_count})
@csrf_exempt
@login_required(login_url='/loginform/')
def delete_notification(request, notification_id):
    notification = get_object_or_404(Notification, id=notification_id, user=request.user)
    notification.delete()
    return JsonResponse({'success': True, 'message': 'Notification deleted successfully.'})



# @csrf_exempt
# def delete_notification(request, notification_id):
#     notification = Notification.objects.get(id=notification_id)
#     notification.delete()
#     return JsonResponse({'success': True, 'message': 'Notification deleted successfully.'})

# views.py
from django.http import JsonResponse
from django.views.decorators.http import require_POST
from django.contrib.auth.decorators import login_required

@require_POST
@login_required
def mark_story_viewed(request, story_id):
    story = get_object_or_404(Story, id=story_id)

    # Mark story as viewed
    StoryViewer.objects.get_or_create(
        story=story,
        viewer=request.user,
        defaults={'viewed_at': timezone.now()}
    )

    return JsonResponse({'status': 'success'})

@login_required(login_url='/loginform/')
def follow_user(request, user_id):
    user_to_follow = get_object_or_404(Login, id=user_id)
    current_user = request.user

    follow_relationship, created = Follow.objects.get_or_create(
        follower=current_user,
        followed=user_to_follow
    )

    if not created:
        follow_relationship.delete()
        followed = False
    else:
        followed = True
        # Create notification
        create_notification(
            user=user_to_follow,
            triggered_by=current_user,
            message=f"{current_user.username} started following you",
            notification_type='follow'
        )

    # Check if mutual
    is_followed_back = Follow.objects.filter(follower=user_to_follow, followed=current_user).exists()

    followers_count = Follow.objects.filter(followed=user_to_follow).count()

    return JsonResponse({
        'success': True,
        'followed': followed,
        'is_followed_back': is_followed_back,
        'followers_count': followers_count,
    })
@login_required(login_url='/loginform/')
def profile1(request, user_id):
    user = get_object_or_404(Login, id=user_id)
    posts = Post.objects.filter(user=user)
    followers_count = Follow.objects.filter(followed=user).count()
    following_count = Follow.objects.filter(follower=user).count()
    bio = user.bio or "No bio yet."
    image_url = user.image.url if user.image else "/static/default-avatar.png"

    is_following = False
    follows_you = False
    is_mutual = False
    if request.user.is_authenticated:
        is_following = Follow.objects.filter(follower=request.user, followed=user).exists()
        follows_you = Follow.objects.filter(follower=user, followed=request.user).exists()
        is_mutual = is_following and follows_you

    # If account is private and not mutual, hide posts
    if user.private_account and not is_mutual and request.user != user:
        posts = []
        private_account_message = "This account is private. Follow and get followed back to see posts."
    else:
        private_account_message = ""

    return render(request, "profile1.html", {
        "username": user.username,
        "image_url": image_url,
        "posts": posts,
        "followers_count": followers_count,
        "following_count": following_count,
        "bio": bio,
        "user": user,
        "is_following": is_following,
        "follows_you": follows_you,
        "is_mutual": is_mutual,
        "private_account_message": private_account_message,
        "current_user_following_ids": list(Follow.objects.filter(follower=request.user).values_list('followed_id', flat=True)) if request.user.is_authenticated else [],
    })

    
@login_required(login_url='/loginform/')
def update_privacy_settings(request):
    if request.method == 'POST':
        user = request.user
        private_account = request.POST.get('private_account') == 'on'
        user.private_account = private_account
        user.save()
        return redirect('profile1', user_id=user.id)    
    
User = get_user_model()
from django.views.decorators.http import require_http_methods
import logging

logger = logging.getLogger(__name__)

@login_required
@require_http_methods(["GET"])
@login_required
def get_followers(request, user_id):
    try:
        user = get_object_or_404(Login, id=user_id)
        followers = Follow.objects.filter(followed=user).select_related('follower')
        
        followers_list = []
        for follow in followers:
            follower = follow.follower
            followers_list.append({
                'id': follower.id,
                'username': follower.username,
                'name': f"{follower.first_name} {follower.last_name}".strip() or follower.username,
                'image_url': request.build_absolute_uri(follower.image.url) if follower.image else request.build_absolute_uri('/static/default-avatar.png'),
                'is_following': Follow.objects.filter(follower=request.user, followed=follower).exists() if request.user.is_authenticated else False
            })
        
        return JsonResponse({
            'success': True,
            'followers': followers_list
        })
        
    except Exception as e:
        return JsonResponse({
            'success': False,
            'error': str(e)
        }, status=400)

@login_required
def get_following(request, user_id):
    try:
        user = get_object_or_404(Login, id=user_id)
        following = Follow.objects.filter(follower=user).select_related('followed')
        
        following_list = []
        for follow in following:
            followed_user = follow.followed
            following_list.append({
                'id': followed_user.id,
                'username': followed_user.username,
                'name': f"{followed_user.first_name} {followed_user.last_name}".strip() or followed_user.username,
                'image_url': request.build_absolute_uri(followed_user.image.url) if followed_user.image else request.build_absolute_uri('/static/default-avatar.png'),
                'is_following': Follow.objects.filter(follower=request.user, followed=followed_user).exists() if request.user.is_authenticated else False
            })
        
        return JsonResponse({
            'success': True,
            'following': following_list
        })
        
    except Exception as e:
        return JsonResponse({
            'success': False,
            'error': str(e)
        }, status=400)
# views.py
@login_required(login_url='/loginform/')
def profile(request):
    current_user = request.user  # Get the logged-in user

    posts = Post.objects.filter(user=current_user)
    followers_count = current_user.get_followers_count()
    following_count = current_user.get_following_count()
    bio = current_user.bio or "No bio yet."
    image_url = current_user.image.url if current_user.image else "/static/default-avatar.png"

    return render(request, "profile.html", {
        "username": current_user.username,
        "image_url": image_url,
        "posts": posts,
        "followers_count": followers_count,
        "following_count": following_count,
        "bio": bio,
    })
    
    
def edit_profile(request):
    if request.method == 'POST':
        user = request.user
        new_username = request.POST.get('new_username')
        new_bio = request.POST.get('new_bio')

        if new_username:
            user.username = new_username

        if new_bio is not None:
            user.bio = new_bio.strip()  # Even if empty, allow clearing bio

        user.save()
        messages.success(request, 'Profile updated successfully.')

    return redirect('profile')

    if request.method == 'POST':
        data = json.loads(request.body)
        new_bio = data.get('bio')
        
        # Update the user's bio in the database
        user_profile = request.user.profile
        user_profile.bio = new_bio
        user_profile.save()
        
        return JsonResponse({"success": True})
    return JsonResponse({"success": False}, status=400)


@csrf_exempt
def delete_account(request):
    if request.method == 'POST':
        user = request.user
        if user.is_authenticated:
            user.delete()  # Delete the user account
            logout(request)  # Log the user out
            return JsonResponse({'success': True})
        else:
            return JsonResponse({'success': False, 'error': 'User not authenticated'})
    return JsonResponse({'success': False, 'error': 'Invalid request method'})

def delete_post(request, post_id):
    if request.method == 'POST':
        post = get_object_or_404(Post, id=post_id)
        
        # Delete the associated media file if it exists
        if post.image:
            image_path = os.path.join(settings.MEDIA_ROOT, post.image.name)
            if os.path.exists(image_path):
                os.remove(image_path)
        
        if post.video:
            video_path = os.path.join(settings.MEDIA_ROOT, post.video.name)
            if os.path.exists(video_path):
                os.remove(video_path)
        
        # Delete the post
        post.delete()
        
        return JsonResponse({"success": True})
    return JsonResponse({"success": False}, status=400)
@login_required
def changepass(request):
    if request.method == 'POST':
        new_password = request.POST.get('new_password')
        user = request.user
        user.password = make_password(new_password)
        user.save()
        return redirect('success')  # Replace with your success URL or page
    return render(request, 'changepass.html', {'username': request.user.username})

@login_required
def verify_old_password(request):
    if request.method == 'POST':
        old_password = request.POST.get('old_password')
        user = authenticate(username=request.user.username, password=old_password)
        return JsonResponse({'valid': user is not None})

# views.py
# views.py
from django.db.models import Subquery, OuterRef, Max

@login_required(login_url='/loginform/')
def message(request):
    user = request.user
    post_id = request.GET.get('post_id')
    post = None
    if post_id:
        post = get_object_or_404(Post, id=post_id)

    # Mark all messages as seen
    Message.objects.filter(recipient=user, is_seen=False).update(is_seen=True)

    # Get mutual follows with latest message timestamp
    user_following = Follow.objects.filter(follower=user).values_list('followed_id', flat=True)
    mutual_follow_ids = Follow.objects.filter(
        follower_id__in=user_following,
        followed=user
    ).values_list('follower_id', flat=True)

    # Annotate with latest message timestamp
    contacts = Login.objects.filter(id__in=mutual_follow_ids).exclude(id=user.id).annotate(
    latest_message=Subquery(
        Message.objects.filter(
            Q(sender=user, recipient=OuterRef('pk')) |
            Q(sender=OuterRef('pk'), recipient=user)
        ).order_by('-timestamp').values('timestamp')[:1]
    )
).order_by('-latest_message')

    message_users = Login.objects.filter(
      Q(sent_messages__recipient=user) | Q(received_messages__sender=user)
).exclude(id__in=mutual_follow_ids).exclude(id=user.id).annotate(
      latest_message=Subquery(
        Message.objects.filter(
            Q(sender=user, recipient=OuterRef('pk')) |
            Q(sender=OuterRef('pk'), recipient=user)
        ).order_by('-timestamp').values('timestamp')[:1]
    )
).distinct().order_by('-latest_message')

    if request.method == 'POST':
        recipient_id = request.POST.get('recipient_id')
        recipient = get_object_or_404(Login, id=recipient_id)
        
        message = Message.objects.create(
            sender=user,
            recipient=recipient,
            content=f"{user.username} shared a post with you!",
            file=post.image if post else None
        )
        return redirect('chat', recipient_id=recipient.id)

    return render(request, 'messages.html', {
        'contacts': contacts,
        'message_users': message_users,
        'post': post,
    })



def send_message(request):
    if request.method == 'POST':
        recipient_id = request.POST.get('recipient_id')
        content = request.POST.get('message')
        post_id = request.POST.get('post_id')

        recipient = get_object_or_404(Login, id=recipient_id)
        post = get_object_or_404(Post, id=post_id) if post_id else None

        message = Message.objects.create(
            sender=request.user,
            recipient=recipient,
            content=content,
            post=post
        )

        # Create notification for recipient
        create_notification(
            user=recipient,
            triggered_by=request.user,
            message=f"{request.user.username} sent you a message",
            notification_type='message'
        )

        messages.success(request, "Message sent successfully!")
        return redirect('messages')

    return redirect('messages')

@login_required(login_url='/loginform/')
def upload_story(request):
    if request.method == 'POST':
        image = request.FILES.get('image')
        video = request.FILES.get('video')

        if not (image or video):
            messages.error(request, "Please upload an image or video.")
            return redirect('upload_story')

        Story.objects.create(
            user=request.user,  
            image=image,
            video=video,
            expires_at=timezone.now() + timezone.timedelta(hours=24)
        )

        messages.success(request, "Story uploaded successfully!")
        return redirect('loginsuccess')

    return render(request, 'upload_story.html')


from .models import ChatUserDelete
def debug_host(request):
    return HttpResponse(f"Host: {request.get_host()}")

@login_required
def delete_chat_user(request, recipient_id):
    if request.method == 'POST':
        recipient = get_object_or_404(Login, id=recipient_id)
        ChatUserDelete.objects.get_or_create(deleter=request.user, deleted_user=recipient)
        return JsonResponse({'message': 'Deleted'})
    return JsonResponse({'error': 'Invalid method'}, status=405)
@login_required(login_url='/loginform/')
def chat(request, recipient_id):
    current_user = request.user  
    recipient = get_object_or_404(Login, id=recipient_id)

    # Mark messages as seen
    Message.objects.filter(
        sender=recipient,
        recipient=current_user,
        is_seen=False
    ).update(is_seen=True)

    # Get messages including story reactions
    chat_messages = Message.objects.filter(
        (Q(sender_id=current_user.id) & Q(recipient_id=recipient.id)) |
        (Q(sender_id=recipient.id) & Q(recipient_id=current_user.id))
    ).select_related('related_story').order_by('timestamp')

    if request.method == 'POST':
        content = request.POST.get('message', '').strip()
        file = request.FILES.get('file', None)

        if content or file:
            Message.objects.create(
                sender=current_user,
                recipient=recipient,
                content=content,
                file=file
            )
            return redirect('chat', recipient_id=recipient.id)

    return render(request, 'chat.html', {
        'recipient': recipient,
        'messages': chat_messages,
        'current_user': current_user,
    })
@login_required
def check_new_messages(request):
    unseen_count = Message.objects.filter(
        recipient=request.user,
        is_seen=False
    ).count()
    return JsonResponse({'unseen_count': unseen_count})
from django.views.decorators.http import require_POST



@login_required
def delete_message(request, message_id):
    if request.method == 'POST':
        message = get_object_or_404(Message, id=message_id)
        if message.sender_id == request.user.id:
            message.delete()
            return JsonResponse({'status': 'success'})
        return JsonResponse({'status': 'error', 'message': 'Unauthorized'}, status=403)
    return JsonResponse({'status': 'error', 'message': 'Invalid request'}, status=400)

def react_to_message(request, message_id):
    if request.method == 'POST':
        data = json.loads(request.body)
        emoji = data.get('emoji')
        message = get_object_or_404(Message, id=message_id)
        message.reactions = emoji
        message.save()
        return JsonResponse({'status': 'success', 'emoji': emoji})

def share_message(request, message_id):
    if request.method == 'POST':
        data = json.loads(request.body)
        recipient_id = data.get('recipient_id')
        message = get_object_or_404(Message, id=message_id)
        new_message = Message.objects.create(
            sender_id=request.user.id,
            sender_username=request.user.username,
            recipient_id=recipient_id,
            recipient_username=User.objects.get(id=recipient_id).username,
            content=message.content,
            file=message.file,
            color=message.color
        )
        return JsonResponse({'status': 'success'})
@csrf_exempt



@csrf_exempt
def edit_message(request, message_id):
    if request.method == "POST":
        try:
            data = json.loads(request.body)
            new_content = data.get('content', '').strip()
            msg = Message.objects.get(id=message_id, sender=request.user)
            msg.content = new_content
            msg.save()
            return JsonResponse({'status': 'success'})
        except Message.DoesNotExist:
            return JsonResponse({'status': 'error', 'message': 'Message not found'})
    return JsonResponse({'status': 'error', 'message': 'Invalid request'})

@login_required
def get_story_viewers(request, story_id):
    story = get_object_or_404(Story, id=story_id)
    if story.user != request.user:
        return HttpResponseForbidden("You can't view viewers of this story.")
    
    viewers = StoryViewer.objects.filter(story=story).select_related('viewer')
    viewer_names = [viewer.viewer.username for viewer in viewers]
    
    return JsonResponse({'viewers': viewer_names})

# views.py
@csrf_exempt
@login_required
@require_http_methods(["POST"])
def update_last_seen(request):
    # When checkbox is unchecked, it doesn't send any value
    # When checked, it sends the value 'show'
    last_seen = request.POST.get('last_seen')
    
    # Set to True only if checkbox was checked (sent 'show')
    request.user.last_seen_visible = (last_seen == 'show')
    request.user.save()
    
    return JsonResponse({
        'success': True,
        'last_seen_visible': request.user.last_seen_visible  # For debugging
    })

# Alternative approach using different field names for clarity
@csrf_exempt
@login_required
@require_http_methods(["POST"])
def update_last_seen_alternative(request):
    # Check if the checkbox was checked
    show_status = 'last_seen' in request.POST
    
    request.user.last_seen_visible = show_status
    request.user.save()
    
    return JsonResponse({
        'success': True,
        'last_seen_visible': request.user.last_seen_visible
    })

def can_view_last_seen(viewer, profile_user):
    # Make sure you're checking the correct field name
    # Your form updates 'last_seen_visible' but this function checks 'show_online_status'
    if not profile_user.last_seen_visible:  # Changed from show_online_status
        return False
 
    # If you have a separate last_seen_visibility field, keep this logic
    if hasattr(profile_user, 'last_seen_visibility'):
        if profile_user.last_seen_visibility == 'Everyone':
            return True
        
        if profile_user.last_seen_visibility == 'Following':
            return Follow.objects.filter(follower=profile_user, followed=viewer).exists()
    
    return False


temp_storage = {}
@csrf_exempt
@login_required
def clear_chat(request, recipient_id):
    if request.method == "POST":
        sender = request.user
        messages = Message.objects.filter(
            (Q(sender_id=sender.id) & Q(recipient_id=recipient_id)) |
            (Q(sender_id=recipient_id) & Q(recipient_id=sender.id))
        )
        temp_storage[request.user.id] = list(messages.values())  # backup
        messages.delete()
        return JsonResponse({"status": "success"})
    return JsonResponse({"status": "failed"})

@csrf_exempt
@login_required
def undo_clear_chat(request, recipient_id):
    if request.method == "POST":
        user_id = request.user.id
        from .models import Message
        if user_id in temp_storage:
            Message.objects.bulk_create([
                Message(**msg) for msg in temp_storage[user_id]
            ])
            del temp_storage[user_id]
            return JsonResponse({"status": "success"})
    return JsonResponse({"status": "failed"})

 # Example in a view or template context
def can_view_last_seen(viewer, target_user):
    # If either viewer OR target has last_seen hidden, return False
    return viewer.last_seen_visible and target_user.last_seen_visible





logger = logging.getLogger(__name__)



User = get_user_model()

# @login_required  # Ensures only logged-in users can create/edit posts
def create_post(request, post_id=None):
    current_user = request.user  # This should be the authenticated user

    # Debug: Print the current user
    print(f"Current User: {current_user.username}")

    if not current_user.is_authenticated:
        return JsonResponse({"error": "You must be logged in to create a post."}, status=401)

    if request.method == 'POST':
        image = request.FILES.get("image")
        video = request.FILES.get("video")
        caption = request.POST.get("caption", "").strip()

        # **Updating an existing post**
        if post_id:
            post = get_object_or_404(Post, id=post_id)

            # Ensure the logged-in user is the owner of the post
            if post.user != current_user:
                return JsonResponse({"error": "You can only edit your own posts."}, status=403)

            if image:
                post.image = image
            if video:
                post.video = video
            post.caption = caption or post.caption
            post.save()

            return redirect("profile")

        # **Creating a new post**
        else:
            if not (image or video):
                return JsonResponse({"error": "Please upload an image or video."}, status=400)

            # Ensure the post is saved with the correct user
            post = Post.objects.create(user=current_user, image=image, video=video, caption=caption)

            # Debug: Print the post creator
            print(f"Post created by: {post.user.username}")

            # Notify other users
            users_to_notify = User.objects.exclude(id=current_user.id)
            for recipient in users_to_notify:
                Notification.objects.create(
                    user=recipient,
                    message=f"{current_user.username} posted something new!",
                    notification_type='post',
                )

            return redirect("profile")

    return render(request, 'create_post.html')
#kk
def is_user_online(user):
    if not user.last_seen:
        return False
    return timezone.now() - user.last_seen < timedelta(minutes=5)
# @login_required
@login_required
def delete_post(request, post_id):
    current_user = request.user  # Get the logged-in user
    post = get_object_or_404(Post, id=post_id, user=current_user)

    # Delete associated media files
    if post.media:  # Assuming 'media' is the file field in the Post model
        media_path = os.path.join(settings.MEDIA_ROOT, str(post.media))
        if os.path.exists(media_path):
            os.remove(media_path)  # Delete the video file from storage

    # Delete the post
    post.delete()
    messages.success(request, "Post deleted successfully.")
    return redirect('profile1', user_id=current_user.id)  # Redirect to the
def index(request):
    return render(request, 'profile.html') 

@login_required(login_url='/loginform/')
def change_profile_photo(request):
    user = request.user
    
    if request.method == 'POST' and request.FILES.get('profile_photo'):
        profile_photo = request.FILES['profile_photo']
        user.image = profile_photo
        user.save()

        # Fix followers query
        follower_ids = user.followers.values_list('follower', flat=True)  # Extract follower IDs
        followers = Login.objects.filter(id__in=follower_ids)  # Get login instances

        # Notify followers
        for follower in followers:
            create_notification(
                user=follower,  # ✅ Now it's a login instance
                triggered_by=user,
                message=f"{user.username} updated their profile picture",
                notification_type='profile'
            )

        messages.success(request, "Profile photo updated successfully.")
        return redirect('profile1', user.id)

    return render(request, 'change_profile_photo.html', {'user': user})




def create_notification(user, triggered_by, message, notification_type):
    """Helper function to create notifications"""
    Notification.objects.create(
        user=user,
        triggered_by=triggered_by,
        message=message,
        notification_type=notification_type
    )
@csrf_exempt
def toggle_like(request, post_id):
    if request.method == 'POST':
        user = request.user
        if not user.is_authenticated:
            return JsonResponse({'success': False, 'message': 'User not authenticated'}, status=403)

        post = get_object_or_404(Post, id=post_id)
        like = Like.objects.filter(user=user, post=post).first()

        if like:
            like.delete()
            liked = False
        else:
            Like.objects.create(user=user, post=post)
            liked = True
            # Create notification for post owner
            if user != post.user:  # Don't notify yourself
                create_notification(
                    user=post.user,
                    triggered_by=user,
                    message=f"{user.username} liked your post",
                    notification_type='like'
                )

        return JsonResponse({
            'success': True,
            'liked': liked,
            'likes_count': post.likes.count()
        })
    return JsonResponse({'success': False, 'message': 'Invalid request method'}, status=400)


def get_likes(request):
    user_id = request.session.get('user_id')
    user = get_object_or_404(Login, id=user_id) if user_id else None

    posts_data = []
    for post in Post.objects.all():
        posts_data.append({
            'id': post.id,
            'likes_count': post.likes.count(),  # Fix: Dynamic count
            'liked': user in post.likes.all() if user else False,  # Fix: Check if the user liked the post
        })

    return JsonResponse({'posts': posts_data})

def get_comments_count(request):
    posts_data = []
    for post in Post.objects.all():
        posts_data.append({
            'id': post.id,
            'comments_count': Comment.objects.filter(post=post).count(),  # Dynamic comments count
        })
    
    return JsonResponse({'posts': posts_data})

@csrf_protect
def add_comment(request):
    if request.method == 'POST':
        data = json.loads(request.body)
        post_id = data.get('post_id')
        content = data.get('content')

        if not post_id or not content:
            return JsonResponse({'success': False, 'error': 'Invalid data'})

        if not request.user.is_authenticated:
            return JsonResponse({'success': False, 'error': 'User not authenticated'}, status=403)

        user = request.user
        post = get_object_or_404(Post, id=post_id)

        comment = Comment.objects.create(user=user, post=post, content=content)

        # Create notification for post owner
        if user != post.user:  # Don't notify yourself
            create_notification(
                user=post.user,
                triggered_by=user,
                message=f"{user.username} commented on your post: {content[:30]}...",
                notification_type='comment'
            )

        return JsonResponse({
            'success': True,
            'comment_id': comment.id,
            'content': comment.content,
            'username': user.username,
            'comments_count': Comment.objects.filter(post=post).count(),
        })
    return JsonResponse({'success': False, 'error': 'Invalid request method'}, status=400)
def get_comments(request, post_id):
    """Fetch comments for a specific post"""
    comments = Comment.objects.filter(post_id=post_id).order_by('-id')
    
    comments_data = [
        {
            'comment_id': comment.id,
            'username': comment.user.username,
            'content': comment.content,
        }
        for comment in comments
    ]

    return JsonResponse({'comments': comments_data})


@csrf_protect
def delete_comment(request, comment_id):
    if not request.user.is_authenticated:
        return JsonResponse({'success': False, 'error': 'User not authenticated'}, status=403)

    try:
        comment = get_object_or_404(Comment, id=comment_id)
        post = comment.post

        # Allow deletion if user is either the comment owner or the post owner
        if request.user == comment.user or request.user == post.user:
            comment.delete()
            return JsonResponse({
                'success': True,
                'comments_count': Comment.objects.filter(post=post).count(),
            })
        else:
            return JsonResponse({'success': False, 'error': 'Permission denied!'}, status=403)

    except Comment.DoesNotExist:
        return JsonResponse({'success': False, 'error': 'Comment not found!'}, status=404)

def settings1(request):
    return render(request, 'settings1.html')

def connected_apps(request):
    # Add logic to fetch and display connected apps
    return render(request, 'connected_apps.html')
from django.core.files.base import File
@login_required
def share_post(request, post_id):
    post = get_object_or_404(Post, id=post_id)

    if request.method == "POST":
        recipient_id = request.POST.get("recipient_id")
        recipient = get_object_or_404(User, id=recipient_id)

        # Create shared post record
        SharedPost.objects.create(
            sender=request.user,
            recipient=recipient,
            post=post
        )

        # Decide what to send (image or video)
        file_to_send = None
        if hasattr(post, 'image') and isinstance(post.image, File) and post.image.name:
          file_to_send = post.image
        elif hasattr(post, 'video') and isinstance(post.video, File) and post.video.name:
          file_to_send = post.video

        # Create a message notification
        Message.objects.create(
            sender=request.user,
            recipient=recipient,
            content=f"{request.user.username} shared a post with you!",
            file=file_to_send
        )

        # Update share count
        post.shares_count += 1
        post.save()

        messages.success(request, f"Post shared with {recipient.username}!")
        return redirect('chat', recipient_id=recipient.id)

    # GET request - show sharing interface
    following_ids = Follow.objects.filter(follower=request.user).values_list('followed_id', flat=True)
    contacts = User.objects.filter(id__in=following_ids).exclude(id=request.user.id)
    return render(request, "share_message.html", {"post": post, "contacts": contacts})

def blocked_users(request):
    # Add logic to fetch and display blocked users
    return render(request, 'blocked_users.html')

def delete_notification(request):
    """Deletes a notification"""
    if request.method == 'POST':
        notification_id = request.POST.get('id')
        try:
            notification = Notification.objects.get(id=notification_id)
            notification.delete()
            return JsonResponse({'status': 'success'}, status=200)
        except Notification.DoesNotExist:
            return JsonResponse({'status': 'error', 'message': 'Notification not found'}, status=404)



def permanent_delete_notification(request):
    if request.method == 'POST':
        notification_id = request.POST.get('id')
        try:
            notification = Notification.objects.get(id=notification_id)
            notification.delete()  # Permanent delete from DB
            return JsonResponse({'status': 'success'}, status=200)
        except Notification.DoesNotExist:
            return JsonResponse({'status': 'error', 'message': 'Notification not found'}, status=404)
@csrf_exempt
def restore_notification(request):
    """Restore a soft-deleted notification."""
    if request.method == 'POST':
        notification_id = request.POST.get('id')
        try:
            notification = Notification.objects.get(id=notification_id, is_deleted=True)
            notification.is_deleted = False  # Restore notification
            notification.save()
            return JsonResponse({'status': 'success', 'message': 'Notification restored.'})
        except Notification.DoesNotExist:
            return JsonResponse({'status': 'error', 'message': 'Notification not found or not deleted.'})
    return JsonResponse({'status': 'error', 'message': 'Invalid request method.'})

# views.py
from django.shortcuts import render
from .models import LoginHistory

def login_history_view(request):
    if request.user.is_authenticated:
        history = LoginHistory.objects.filter(user=request.user).order_by('-login_time')
        return render(request, 'login_history.html', {'history': history})
    else:
        return redirect('loginform')  # Or appropriate route for your project


