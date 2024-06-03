from django.urls import path
from .views import (
    UserRegistrationView, UserLoginView, UserLogoutView,
    FriendRequestListView, FriendRequestDetailView, SearchUserView,
    FriendListView
    )


urlpatterns = [
    path('register/', UserRegistrationView.as_view(), name='user-registration'),
    path('login/', UserLoginView.as_view(), name='user-login'),
    path('logout/', UserLogoutView.as_view(), name='user-logout'),
    path('search/', SearchUserView.as_view(), name='request-search'),
    path('friend/list', FriendListView.as_view(), name='friend-list'),
    path('request/send/', FriendRequestListView.as_view(), name='request-sent'),
    path('request/reject/', FriendRequestDetailView.as_view(), name='request-reject'),
    path('request/accept/', FriendRequestDetailView.as_view(), name='request-accepted'),
    path('request/pending/', FriendRequestListView.as_view(), name='request-pending'),
]
