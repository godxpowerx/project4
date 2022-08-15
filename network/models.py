from django.contrib.auth.models import AbstractUser
from django.db import models
import datetime


class User(AbstractUser):

    def serialize(self):
        return {
            'id': self.id,
            'username': self.username,
            'email': self.email,
            'date_joined': self.date_joined.strftime("%b %d %Y"),
            'last_login' : self.last_login.strftime("%b %d %Y"),
        }


class Post(models.Model):
    user = models.ForeignKey(
        User, on_delete=models.CASCADE, related_name="posts")
    post_content = models.TextField()
    pub_date = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f'{self.post_content} by {self.user} at {self.pub_date}'

    def serialize(self):
        return {
            'id' : self.id,
            'user_id':self.user.id,
            'user': self.user.username,
            'post_content': self.post_content,
            'pub_date' : self.pub_date,
            'no_likes': self.liked_post.count(),
            'no_comment' : self.post_comment.count(),
        }


class Like(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE,related_name="user_likes")
    post = models.ForeignKey(
        Post, on_delete=models.CASCADE, related_name="liked_post")
    likes = models.BooleanField(default=False)
    pub_date = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f'{self.post.post_content} -> {self.likes} likes'

    def serialize(self):
        return {
        'user_id': self.user.id,
        'post_id': self.post.id,
        'likes': self.likes,
        'pub_date':self.pub_date,
    }


class Following(models.Model):
    user = models.ManyToManyField(User, related_name="follower")
    followings = models.ManyToManyField(User, related_name="followings")
    pub_date = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f'{self.user.all()}, {self.followings.all()}'

    def serialize(self):
        return {
            'user': [user.username for user in self.user.all()],
            'user_id': [user.id for user in self.user.all()],
            'following':[following.username for following in self.followings.all()],
            'following_id': [following.id for following in self.followings.all()],
        }


class UserFollowing(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    following = models.ForeignKey(Following, on_delete=models.CASCADE)



class Comment(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name = "user_comment")
    post = models.ForeignKey(
        Post, on_delete=models.CASCADE, related_name="post_comment")
    comment = models.TextField()
    pub_date = models.DateTimeField(auto_now_add=True)

    def serialize(self):
        return {
             'user':self.user.username,
            'user_id':self.user.id,
            'post_id': self.post.id,
            'comment':self.comment,
            'pub_date': self.pub_date,
        }
