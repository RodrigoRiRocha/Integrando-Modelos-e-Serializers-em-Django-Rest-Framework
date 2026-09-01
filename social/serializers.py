from django.contrib.auth.models import User
from rest_framework import serializers

from .models import Comment, Post, Profile


class RegisterSerializer(serializers.ModelSerializer):
    password = serializers.CharField(write_only=True, min_length=8)

    class Meta:
        model = User
        fields = ('username', 'password', 'first_name', 'last_name')

    def create(self, validated_data):
        password = validated_data.pop('password')
        return User.objects.create_user(password=password, **validated_data)


class ProfileSerializer(serializers.ModelSerializer):
    username = serializers.CharField(source='user.username', read_only=True)
    first_name = serializers.CharField(source='user.first_name', required=False)
    last_name = serializers.CharField(source='user.last_name', required=False)
    password = serializers.CharField(source='user.password', write_only=True, required=False)
    following_count = serializers.IntegerField(source='following.count', read_only=True)
    followers_count = serializers.IntegerField(source='followers.count', read_only=True)

    class Meta:
        model = Profile
        fields = (
            'id',
            'username',
            'first_name',
            'last_name',
            'password',
            'avatar_url',
            'following_count',
            'followers_count',
        )
        read_only_fields = ('id', 'username', 'following_count', 'followers_count')

    def update(self, instance, validated_data):
        user_data = validated_data.pop('user', {})
        password = user_data.pop('password', None)
        for field, value in user_data.items():
            setattr(instance.user, field, value)
        if password:
            instance.user.set_password(password)
        instance.user.save()
        return super().update(instance, validated_data)


class CommentSerializer(serializers.ModelSerializer):
    author = serializers.CharField(source='author.username', read_only=True)

    class Meta:
        model = Comment
        fields = ('id', 'author', 'content', 'created_at')
        read_only_fields = ('id', 'author', 'created_at')


class PostSerializer(serializers.ModelSerializer):
    author = serializers.CharField(source='author.username', read_only=True)
    likes_count = serializers.IntegerField(source='likes.count', read_only=True)
    comments = CommentSerializer(many=True, read_only=True)

    class Meta:
        model = Post
        fields = (
            'id',
            'author',
            'content',
            'likes_count',
            'comments',
            'created_at',
            'updated_at',
        )
        read_only_fields = (
            'id',
            'author',
            'likes_count',
            'comments',
            'created_at',
            'updated_at',
        )