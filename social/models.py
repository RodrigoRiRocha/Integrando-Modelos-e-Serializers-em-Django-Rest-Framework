from django.db import models
from django.contrib.auth.models import User


class Profile(models.Model):
	user = models.OneToOneField(User, on_delete=models.CASCADE, related_name='profile')
	avatar_url = models.URLField(blank=True)
	following = models.ManyToManyField(
		'self',
		blank=True,
		symmetrical=False,
		related_name='followers',
	)

	def __str__(self):
		return self.user.username


class Post(models.Model):
	author = models.ForeignKey(User, on_delete=models.CASCADE, related_name='posts')
	content = models.CharField(max_length=280)
	likes = models.ManyToManyField(User, blank=True, related_name='liked_posts')
	created_at = models.DateTimeField(auto_now_add=True)
	updated_at = models.DateTimeField(auto_now=True)

	class Meta:
		ordering = ('-created_at',)

	def __str__(self):
		return f'{self.author.username}: {self.content[:30]}'


class Comment(models.Model):
	post = models.ForeignKey(Post, on_delete=models.CASCADE, related_name='comments')
	author = models.ForeignKey(User, on_delete=models.CASCADE, related_name='comments')
	content = models.CharField(max_length=280)
	created_at = models.DateTimeField(auto_now_add=True)

	class Meta:
		ordering = ('created_at',)

	def __str__(self):
		return f'{self.author.username}: {self.content[:30]}'
