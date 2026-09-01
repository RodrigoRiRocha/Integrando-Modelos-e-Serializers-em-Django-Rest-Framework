from django.contrib.auth import authenticate
from django.shortcuts import render
from rest_framework import status
from rest_framework.authtoken.models import Token
from rest_framework.decorators import action
from rest_framework.permissions import AllowAny, IsAuthenticated
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework.viewsets import ModelViewSet, ReadOnlyModelViewSet

from .models import Post, Profile
from .permissions import IsAuthorOrReadOnly
from .serializers import CommentSerializer, PostSerializer, ProfileSerializer, RegisterSerializer


def social_home(request):
	return render(request, 'social/home.html')


class RegisterView(APIView):
	permission_classes = (AllowAny,)

	def post(self, request):
		serializer = RegisterSerializer(data=request.data)
		serializer.is_valid(raise_exception=True)
		user = serializer.save()
		token, _ = Token.objects.get_or_create(user=user)
		return Response({'token': token.key}, status=status.HTTP_201_CREATED)


class LoginView(APIView):
	permission_classes = (AllowAny,)

	def post(self, request):
		user = authenticate(
			username=request.data.get('username'),
			password=request.data.get('password'),
		)
		if user is None:
			return Response(
				{'detail': 'Invalid username or password.'},
				status=status.HTTP_400_BAD_REQUEST,
			)
		token, _ = Token.objects.get_or_create(user=user)
		return Response({'token': token.key})


class ProfileViewSet(ReadOnlyModelViewSet):
	queryset = Profile.objects.select_related('user')
	serializer_class = ProfileSerializer

	@action(detail=False, methods=('get', 'patch'), permission_classes=(IsAuthenticated,))
	def me(self, request):
		profile = request.user.profile
		if request.method == 'PATCH':
			serializer = self.get_serializer(profile, data=request.data, partial=True)
			serializer.is_valid(raise_exception=True)
			serializer.save()
			return Response(serializer.data)
		return Response(self.get_serializer(profile).data)

	@action(detail=True, methods=('post',), permission_classes=(IsAuthenticated,))
	def follow(self, request, pk=None):
		profile = self.get_object()
		if profile == request.user.profile:
			return Response(
				{'detail': 'You cannot follow yourself.'},
				status=status.HTTP_400_BAD_REQUEST,
			)
		request.user.profile.following.add(profile)
		return Response({'status': 'following'})

	@action(detail=True, methods=('post',), permission_classes=(IsAuthenticated,))
	def unfollow(self, request, pk=None):
		request.user.profile.following.remove(self.get_object())
		return Response({'status': 'unfollowed'})


class PostViewSet(ModelViewSet):
	queryset = Post.objects.select_related('author').prefetch_related('likes', 'comments__author')
	serializer_class = PostSerializer
	permission_classes = (IsAuthenticated, IsAuthorOrReadOnly)

	def perform_create(self, serializer):
		serializer.save(author=self.request.user)

	@action(detail=False, methods=('get',))
	def feed(self, request):
		following = request.user.profile.following.all()
		queryset = self.get_queryset().filter(author__profile__in=following)
		page = self.paginate_queryset(queryset)
		if page is not None:
			return self.get_paginated_response(self.get_serializer(page, many=True).data)
		return Response(self.get_serializer(queryset, many=True).data)

	@action(detail=True, methods=('post',), permission_classes=(IsAuthenticated,))
	def like(self, request, pk=None):
		post = self.get_object()
		post.likes.add(request.user)
		return Response({'likes_count': post.likes.count()})

	@action(detail=True, methods=('delete',), permission_classes=(IsAuthenticated,))
	def unlike(self, request, pk=None):
		post = self.get_object()
		post.likes.remove(request.user)
		return Response(status=status.HTTP_204_NO_CONTENT)

	@action(detail=True, methods=('post',), permission_classes=(IsAuthenticated,))
	def comments(self, request, pk=None):
		serializer = CommentSerializer(data=request.data)
		serializer.is_valid(raise_exception=True)
		comment = serializer.save(post=self.get_object(), author=request.user)
		return Response(CommentSerializer(comment).data, status=status.HTTP_201_CREATED)

# Create your views here.
