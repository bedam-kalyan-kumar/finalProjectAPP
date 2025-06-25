from django.contrib import admin
from django.urls import path
from django.contrib.auth import views as auth_views
from django.views.static import serve
from django.urls import re_path
from .views import (
    loginform, forget, toggle_like, otp, newpass, register, success, create_post, delete_post, chat,profile1,get_followers,blocked_users,debug_host,
    add_comment, share_post, loginsuccess, search, notifications, profile, delete_notification, follow_user,get_following,connected_apps,send_message,
    restore_notification, changepass, message, change_profile_photo, get_likes, delete_comment, upload_story, delete_story,settings1,view_story,
    delete_account,get_comments,get_comments_count,delete_message,get_story,story_list,latest_story,get_stories_by_user,get_all_stories,edit_profile,
    get_story_viewers,unfollow_user,check_new_notifications,mark_notifications_seen,mark_notification_seen,check_new_messages,delete_chat_user,update_last_seen
)
from . import views
from django.conf import settings
from django.conf.urls.static import static
from . import consumers
from .utils import generate_random_string

urlpatterns = [
    path('login/', auth_views.LoginView.as_view(template_name='loginform.html'), name='login'),
    path('loginform/', loginform, name="loginform"),
    path('logout/', auth_views.LogoutView.as_view(next_page='loginform'), name='logout'),  # Root login URL
    path('forget/', forget, name="forget"),
    path('otp/', otp, name="otp"),
    path('newpass/', newpass, name='newpass'),
    path('register/', register, name='register'),
    path('success/', success, name='success'),
    path('', loginsuccess, name='loginsuccess'),
    path('search/', search, name='search'),
    path('notifications/', notifications, name='notifications'),
    path('profile/', profile, name='profile'),
    path('changepass/', changepass, name='changepass'),
    path('messages/', message, name='messages'),
    path('change_profile_photo/', change_profile_photo, name='change_profile_photo'),
    path('create_post/', create_post, name='create_post'),
    path('delete_post/<int:post_id>/', delete_post, name='delete_post'),
    path('toggle_like/<int:post_id>/', toggle_like, name='toggle_like'),
    path('add_comment/', add_comment, name='add_comment'),
    path('delete_comment/<int:comment_id>/', delete_comment, name='delete_comment'),
    path("share_post/<int:post_id>/", share_post, name="share_post"),
    path('get_likes/', get_likes, name='get_likes'),
    path('get_comments/<int:post_id>/', get_comments, name='get_comments'),
    path('chat/<int:recipient_id>/',chat, name='chat'),
    path('delete-notification/', delete_notification, name='delete-notification'),
    path('restore-notification/', restore_notification, name='restore-notification'),
    path('delete_story/<int:story_id>/', delete_story, name='delete_story'),
    path('follow_user/<int:user_id>/', follow_user, name='follow_user'),
    path('profile1/<int:user_id>/', profile1, name='profile1'),
    path('get_followers/<int:user_id>/', get_followers, name='get_followers'),
    path('get_following/<int:user_id>/',get_following, name='get_following'),
    path('settings1/',settings1, name='settings1'),
    path('blocked_users/', blocked_users, name='blocked_users'),
    path('connected_apps/', connected_apps, name='connected_apps'),
    path("stories/", story_list, name="story_list"),
    path('upload_story/', upload_story, name='upload_story'),
    path("send_message/<int:story_id>/",send_message,name="send_message"),
    path('debug/', debug_host, name='debug'),
    path('delete_account/', delete_account, name='delete_account'),
    path('get_comments_count/', get_comments_count, name='get_comments_count'),
    path('delete_message/<int:message_id>/', delete_message, name='delete_message'),
    path('latest_story/', latest_story, name='latest_story'),
    path('get_stories_by_user/', get_stories_by_user, name='get_stories_by_user'),
    path('get_all_stories/', get_all_stories, name='get_all_stories'),   
    path('stories/<str:username>/', view_story, name='view_story'),
    path('api/get_story/<int:story_id>/',get_story, name='get_story'), 
    path('edit-profile/', edit_profile, name='edit_profile'),
     path('delete_story/<int:story_id>/', delete_story, name='delete_story'),
    path('story_viewers/<int:story_id>/', get_story_viewers, name='story_viewers'),
     path('unfollow/<int:user_id>/', unfollow_user, name='unfollow_user'),
     path('check_new_notifications/', check_new_notifications, name='check_new_notifications'),
     path('mark_notifications_seen/', mark_notifications_seen, name='mark_notifications_seen'),
    path('mark_notification_seen/<int:notification_id>/', mark_notification_seen, name='mark_notification_seen'),
    path('check_new_messages/',check_new_messages, name='check_new_messages'),
path('delete_user/<int:recipient_id>/', delete_chat_user, name='delete_chat_user'),
# path('update_last_seen/', update_last_seen, name='update_last_seen'),
path('clear_chat/<int:recipient_id>/', views.clear_chat, name='clear_chat'),
path('undo_clear_chat/<int:recipient_id>/', views.undo_clear_chat, name='undo_clear_chat'),
 path('edit_message/<int:message_id>/', views.edit_message, name='edit_message'),
#  path('story_viewers/<int:story_id>/', views.story_viewers, name='story_viewers'),
#  path('stories/<int:story_id>/react/', views.react_to_story, name='react_to_story'),
    # path('stories/<int:story_id>/message/', views.send_story_message, name='send_story_message'),
    path('refresh-captcha/', views.refresh_captcha, name='refresh_captcha'),
 path('verify_old_password/', views.verify_old_password, name='verify_old_password'),
 path('edit-profile/', views.edit_profile, name='edit_profile'),
 path('check_new_messages/', views.check_new_messages, name='check_new_messages'),
 path('get_search_history/', views.get_search_history, name='get_search_history'),
path('delete_search_history/<int:history_id>/', views.delete_search_history, name='delete_search_history'),
path('save_search_history/', views.save_search_history, name='save_search_history'),
# urls.py
path('delete_story/<int:story_id>/', views.delete_story, name='delete_story'),
path('story_viewers/<int:story_id>/', views.story_viewers, name='story_viewers'),
path('stories/<int:story_id>/react/', views.react_to_story, name='react_to_story'),
path('stories/<int:story_id>/message/', views.send_story_message, name='send_story_message'),
# urls.py
path('mark_story_viewed/<int:story_id>/', views.mark_story_viewed, name='mark_story_viewed'),
path('update_privacy_settings/', views.update_privacy_settings, name='update_privacy_settings'),
 path('update_last_seen/', views.update_last_seen, name='update_last_seen'),
 path('login-history/',views. login_history_view, name='login_history'),
 ]

if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
    re_path(r'^media/(?P<path>.*)$', serve, {'document_root': settings.MEDIA_ROOT}),