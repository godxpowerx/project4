
from django.urls import path

from . import views

app_name = 'network'

urlpatterns = [
    path("", views.index, name="index"),
    path('all_post/<int:page>', views.all_post, name='all_post'),
    path("create_post", views.create_post, name='create_post'),
    path('edit_post/<int:post_id>', views.edit_post, name='edit_post'),
    path('follow_switch/<int:user_id>', views.follow_switch, name='follow_switch'),
    path("profile_page/<int:user_id>", views.profile_page, name="profile_page"),
    path('user_posts', views.user_posts,name='user_posts'),
    path('liking/<int:post_id>',views.liking,name='liking'),
    path('post_comment/<int:post_id>', views.post_comment, name='post_comment'),
    path('view_comment/<int:post_id>', views.view_comment, name='view_comment'),
    path("following_post/<int:page>", views.following_post, name="following_post"),
    path("login", views.login_view, name="login"),
    path("logout", views.logout_view, name="logout"),
    path("register", views.register, name="register")
]
