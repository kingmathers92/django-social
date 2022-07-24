
from django.urls import path
from django.conf import settings
from django.conf.urls.static import static

from . import views
from .views import (
    posts_of_following_profiles,
    like_unlike_post,
    invites_received_view,
    invite_profiles_list_view,
    send_invitation,
    remove_friends,
    accept_invitation,
    reject_invitation,
    search_view,
    post_comment_create_view,
    login_view,
    logout_view,
    register,


    ProfileDetailView,
    PostDeleteView,
    PostUpdateView,
    ProfileListView,
    #EditProfileView,
)


urlpatterns = [
    path("", ProfileListView.as_view(), name="all-profiles-view"),
    path("posts/", views.post_comment_create_view, name="posts"),
    path("posts-follow/", posts_of_following_profiles, name="posts-follow"),
    path("login", views.login_view, name="login"),
    path("logout", views.logout_view, name="logout"),
    path("register", views.register, name="register"),
    path("liked/", like_unlike_post, name="like-post-view"),
    path("<pk>/delete", PostDeleteView.as_view(), name="post-delete"),
    path("<pk>/update", PostUpdateView.as_view(), name="post-update"),
    path("invites/", invites_received_view, name="invites-view"),
    path("send-invite/", send_invitation, name="send-invite"),
    path("remove-friend/", remove_friends, name="remove-friend"),
    path("invites/accept/", accept_invitation, name="accept-invite"),
    path("invites/reject/", reject_invitation, name="reject-invite"),
    path("to-invite/", invite_profiles_list_view, name='invite-profiles-view'),
    path("search/", views.search_view, name='search-view'),
    path("<slug>", ProfileDetailView.as_view(), name="profile-view"),
]


urlpatterns += static(settings.STATIC_URL, document_root=settings.STATIC_ROOT)
urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)