from django.contrib.auth import authenticate, login
from rest_framework import status
from rest_framework.response import Response
from rest_framework.views import APIView
from .serializers import UserSerializer, FriendRequestSerializer
from rest_framework.authtoken.views import ObtainAuthToken
from rest_framework.authtoken.models import Token
from rest_framework.permissions import IsAuthenticated
from django.http import Http404
from .models import User, FriendRequest, StatusType
from rest_framework.pagination import PageNumberPagination


class UserRegistrationView(APIView):
    """User registration view."""

    @classmethod
    def post(cls, request) -> Response:
        """Return user registration response."""
        serializer = UserSerializer(data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class UserLoginView(ObtainAuthToken):
    """User login view."""
    @classmethod
    def post(cls, request, *args, **kwargs) -> Response:
        """Return user login response."""
        email = request.data.get('email')
        password = request.data.get('password')
        user = authenticate(request, username=email, password=password)
        if user is not None:
            login(request, user)
            token, created = Token.objects.get_or_create(user=user)
            if created:
                token.delete()
                token = Token.objects.create(user=user)
            return Response({'token': token.key, 'email': user.email})
        else:
            return Response({'message': 'Invalid username or password'}, status=status.HTTP_401_UNAUTHORIZED)


class UserLogoutView(APIView):
    permission_classes = [IsAuthenticated]

    def post(self, request):
        token_key = request.auth.key
        token = Token.objects.get(key=token_key)
        token.delete()
        return Response({'detail': 'Successfully logged out.'})


class FriendListView(APIView):
    """Friend list view"""
    permission_classes = [IsAuthenticated]

    @classmethod
    def get(cls, request) -> Response:
        """Return list of users friends."""
        user = User.objects.get(id=request.user.id)
        friends_list = user.friends.all()
        serializer = UserSerializer(friends_list, many=True)
        return Response(serializer.data)


class FriendRequestListView(APIView):
    """FriendRequest List or create View"""
    throttle_scope = 'send'
    permission_classes = [IsAuthenticated]

    @classmethod
    def post(cls, request) -> Response:
        """Create and return FriendRequest response"""
        target_user = User.objects.get(email=request.data.get('target_user_email'))
        data = dict()
        data['from_user'] = request.user.pk
        data['to_user'] = target_user.pk
        data['status'] = StatusType.PENDING
        serializer = FriendRequestSerializer(data=data)
        if FriendRequest.objects.filter(**data).exists():
            return Response('Friend request was already sent', status=status.HTTP_400_BAD_REQUEST)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    @classmethod
    def get(cls, request) -> Response:
        """Return pending friend request"""
        friend_requests = FriendRequest.objects.filter(to_user=request.user.pk, status=StatusType.PENDING)
        serializer = FriendRequestSerializer(friend_requests, many=True)
        return Response(serializer.data)


class FriendRequestDetailView(APIView):
    """FriendRequest Detail View"""
    permission_classes = [IsAuthenticated]

    @classmethod
    def get_object(cls, request_id, status: StatusType) -> FriendRequest:
        try:
            return FriendRequest.objects.get(pk=request_id, status=status)
        except FriendRequest.DoesNotExist:
            raise Http404(f"Friend request does not exist with requestid {request_id}")

    @classmethod
    def put(cls, request):
        """FriendRequest accept or reject View"""
        friend_request = cls.get_object(request_id=request.data.get('request_id'), status=StatusType.PENDING)
        data = dict()
        data["from_user"] = friend_request.from_user.pk
        data["to_user"] = request.user.pk
        if request.data.get("accept", False):
            data['status'] = StatusType.ACCEPTED
        else:
            data['status'] = StatusType.REJECTED
        serializer = FriendRequestSerializer(friend_request, data=data)
        if serializer.is_valid():
            serializer.save()
            request.user.friends.add(friend_request.from_user)
            friend_request.from_user.friends.add(request.user)
            return Response(serializer.data)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class SearchUserView(APIView):
    """Search User view"""
    permission_classes = [IsAuthenticated]
    pagination_class = PageNumberPagination

    @classmethod
    def get(cls, request) -> Response:
        """Return users based on query string"""
        if request.data.get('email'):
            users = User.objects.filter(email__exact=request.data.get('email'))
            if users:
                serializer = UserSerializer(users.first())
            else:
                users = User.objects.filter(email__contains=request.data.get('email'))
                serializer = UserSerializer(users, many=True)
        else:
            users = User.objects.filter(first_name__contains=request.data.get('name'))
            serializer = UserSerializer(users, many=True)
        return Response(serializer.data)

