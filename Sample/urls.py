"""Sample URL Configuration

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/2.0/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  path('', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  path('', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.urls import include, path
    2. Add a URL to urlpatterns:  path('blog/', include('blog.urls'))
"""
from django.contrib import admin
from django.urls import path
from django.conf.urls import include, url
from django.views.generic import TemplateView

from bridge.views import payment_process, register_expert, student_registration, visitor, expert_index, edit_expert, \
    add_lecture, followers, update_followers, remove_followers, block_follower, expert_history, student_index, \
    send_follow_request, student_edit_profile, student_following_list, student_history, update_student, check_login, \
    notification_student, notification_expert, clear_notification_expert, clear_notification_student, \
    clear_notification_expert_all, clear_notification_student_all, send_email, expert_online_status, review_expert, \
    student_review, student_review_show, user_admin, accept_expert, reject_expert, reject_student, \
    reset_student_block_count, send_connect_request, remove_connection, accept_connection_req, show_expert_profile, \
    expert_enq, set_expert_review
from django.conf import settings
from django.conf.urls.static import static
from django.contrib.auth import views as auth_views


urlpatterns = [

    path('admin/', admin.site.urls),
    url('register_expert', register_expert),
    url('student_registration', student_registration),
    url(r'^paypal/', include('paypal.standard.ipn.urls')),
    url(r'^payment_process/$', payment_process, name='payment_process'),

    url(r'^payment_done/$', TemplateView.as_view(template_name="payment_done.html"),
                      name='payment_done'),
    url(r'^payment_canceled/$', TemplateView.as_view(template_name="payment_canceled.html"),
                      name='payment_canceled'),
    url(r'^login/$', auth_views.login, name='login'),
    url(r'^logout/$', auth_views.logout, {'template_name': 'registration/login.html'}, name='logout'),
    url(r'^visitor/$', visitor, name='visitor'),
    url(r'^expert_index/$', expert_index, name='expert_index'),
    url(r'^edit_expert/$', edit_expert, name='edit_expert'),
    url(r'^add_lecture/$', add_lecture, name='add_lecture'),
    url(r'^followers/$', followers, name='followers'),
    url(r'^coreHike/follower_update/(?P<id>\d+)/$', update_followers, name='update_followers'),
    url(r'^coreHike/remove_followers/(?P<id>\d+)/$', remove_followers, name='remove_followers'),
    url(r'^coreHike/block_follower/(?P<id>\d+)/$', block_follower, name='block_followers'),
    url(r'^expert_history/$', expert_history, name='expert_history'),
    url(r'^student_index/$', student_index, name='student_index'),
    url(r'^send_follow_request/(?P<expert_id>\d+)/$', send_follow_request, name='send_follow_request'),
    url(r'^student_edit_profile/$', student_edit_profile, name='student_edit_profile'),
    url(r'^student_following/$', student_following_list, name='student_following_list'),
    url(r'^student_history/$', student_history, name='student_following_list'),
    url(r'^update_student/$', update_student, name='update_student'),
    url(r'^check_login/$', check_login, name='check_login'),
    url(r'^notification_student/$', notification_student, name='notification'),
    url(r'^clear_notification_expert$', clear_notification_expert, name='clear_notification'),
    url(r'^clear_notification_student$', clear_notification_student, name='clear_notification'),
    url(r'^notification_expert/$', notification_expert, name='notification'),
    url(r'^clear_notification_student_all/$', clear_notification_student_all, name='clear_notification_student_all'),
    url(r'^clear_notification_expert_all/$', clear_notification_expert_all,
                      name='clear_notification_expert_all'),
    url(r'^email/$', send_email, name='send_email'),
    url(r'^expert_online_status/$', expert_online_status, name='expert_online_status'),
    url(r'^review_expert/$', review_expert, name='review_expert'),
    url(r'^student_review/$', student_review, name='student_review'),
    url(r'^student_review_show/$', student_review_show, name='student_review'),
    url(r'^user_admin/$', user_admin, name='user_admin'),
    url(r'^coreHike/accept_expert/(?P<expert_id>\d+)/$', accept_expert, name='accept_expert'),
    url(r'^coreHike/reject_expert/(?P<expert_id>\d+)/$', reject_expert, name='reject_expert'),
    url(r'^coreHike/reject_student/(?P<expert_id>\d+)/$', reject_student, name='reject_student'),
    url(r'^coreHike/reset_student_block/(?P<student_id>\d+)/$', reset_student_block_count, name='reset_student_block_count'),
    url(r'^send_connect_request/(?P<expert_req_id>\d+)/(?P<expert_login_id>\d+)$', send_connect_request, name='send_connect_request'),
    url(r'^coreHike/remove_connection/(?P<expert_req_id>\d+)/(?P<expert_login_id>\d+)$', remove_connection,
                      name='remove_connection'),
    url(r'^coreHike/accept_connection_req/(?P<expert_req_id>\d+)/(?P<expert_login_id>\d+)$', accept_connection_req,
                      name='accpet_connection_req'),

    url(r'^expert_index/coreHike/show_expert_profile/(?P<expert_id>\d+)/$', show_expert_profile, name='show_expert_profile'),
    url(r'^expert_enq/(?P<expert_id>\d+)/(?P<student_id>\d+)$', expert_enq,
                      name='expert_enq'),
    url(r'^set_expert_review/(?P<expert_id>\d+)/(?P<student_id>\d+)$', set_expert_review,
                      name='set_expert_review'),

              ]+ static(settings.STATIC_URL, document_root=settings.STATIC_ROOT)


urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
