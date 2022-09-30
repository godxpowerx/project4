from django.contrib.auth.models import AbstractUser
from django.db import models
import datetime

# this file contains all the model used within the application 
# each class represent a table and its attribute

# this this the User model for storing personal information relating to a particular User,
# using django AbstractUser class we imported the field and dont need to create a new one.
class User(AbstractUser):

    #  created a serialize function for easy use or convertion to JSON 
    def serialize(self):
        return {
            'id': self.id,
            'username': self.username,
            'email': self.email,
            'date_joined': self.date_joined.strftime("%b %d %Y"),
            'last_login' : self.last_login.strftime("%b %d %Y"),
        }

# this class model represent  and stores a Post created by each User. 
# each post is connected to a user who created the post 
class Post(models.Model):
    user = models.ForeignKey(
        User, on_delete=models.CASCADE, related_name="posts")
    post_content = models.TextField()
    pub_date = models.DateTimeField(auto_now_add=True)
    

    # this is function returns a string representation of the information about the Post data
    def __str__(self):
        return f'{self.post_content} by {self.user} at {self.pub_date}'

     #  created a serialize function for easy use or convertion to JSON
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

# Like class store data related to the each user and a post if the user choose to like it or not,
# .
class Like(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE,related_name="user_likes")
    post = models.ForeignKey(
        Post, on_delete=models.CASCADE, related_name="liked_post")
    likes = models.BooleanField(default=False)
    pub_date = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f'{self.post.post_content} -> {self.likes} likes'

    #  created a serialize function for easy use or convertion to JSON
    def serialize(self):
        return {
        'user_id': self.user.id,
        'post_id': self.post.id,
        'likes': self.likes,
        'pub_date':self.pub_date,
    }

# using the django ManyToMany db connector Following class store each user being followed by another
# user and each user following other user and makes retrieving and representing this information possible.
class Following(models.Model):
    user = models.ManyToManyField(User, related_name="follower")
    followings = models.ManyToManyField(User, related_name="followings")
    pub_date = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f'{self.user.all()}, {self.followings.all()}'

    #  created a serialize function for easy use or convertion to JSON
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


# Comment class store data related to the each user and a post 
# if the user choose to comment on it or not,
class Comment(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name = "user_comment")
    post = models.ForeignKey(
        Post, on_delete=models.CASCADE, related_name="post_comment")
    comment = models.TextField()
    pub_date = models.DateTimeField(auto_now_add=True)

    #  created a serialize function for easy use or convertion to JSON
    def serialize(self):
        return {
             'user':self.user.username,
            'user_id':self.user.id,
            'post_id': self.post.id,
            'comment':self.comment,
            'pub_date': self.pub_date,
        }
