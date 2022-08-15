import json
from django.core.paginator import Paginator
from django.contrib.auth import authenticate, login, logout
from django.db import IntegrityError
from django.http import HttpResponse, HttpResponseRedirect,JsonResponse
from django.shortcuts import render,redirect
from django.urls import reverse
from django.views.decorators.csrf import csrf_exempt
from django.contrib.auth.decorators import login_required
from django.conf import settings

from operator import itemgetter, attrgetter
from .models import Like, User,Post,Following,Comment


def index(request):
    total_post = Post.objects.all()
    total_post = total_post.order_by("-pub_date").all()
    return render(request, "network/index.html",{
        'all_post': total_post
    })

def all_post(request, page):
    total_post = Post.objects.all()
    init_post = total_post.order_by("-pub_date").all()
    paginate = Paginator(init_post, 10)

    total_post = paginate.get_page(page)

    page_num = total_post.number
    next = total_post.has_next()
    prev = total_post.has_previous()

    num_of_pages = paginate.num_pages

    total = []
    for posts in total_post:
        pos = posts.serialize()
        if posts.user == request.user:
            pos['original_users'] = True
        else:
            pos['original_users'] = False
        
        likes = Like.objects.filter(post=posts ,user = request.user)
        if likes:
            pos['liked'] = True
        else:
            pos['liked'] = False
        total.append(pos)
    return JsonResponse({'total':total, 'total_page':num_of_pages,
    'prev':prev,'next':next,'page_num':page_num}, safe=False)


@csrf_exempt
@login_required(login_url='network:login')
def following_post(request, page):

    post_follow =[]
    follow =  Following.objects.filter(user=request.user)

    for u in follow:
       init_post = Post.objects.filter(user=u.followings.first())
       post_follow.extend(init_post) 

    post_follow.sort(key=attrgetter('pub_date'), reverse=True)
    postes = Paginator(post_follow, 10)

    post_follow = postes.get_page(page)

    page_num = post_follow.number
    prev = post_follow.has_previous()
    nexts = post_follow.has_next()


    total = []
    for posts in post_follow:
        pos = posts.serialize()
        if posts.user == request.user:
            pos['original_users'] = True
        else:
            pos['original_users'] = False
        likes = Like.objects.filter(post=posts, user=request.user)
        if likes:
            pos['liked'] = True
        else:
            pos['liked'] = False
        total.append(pos)
        
    return JsonResponse({'total':total,
                         'prev': prev, 'next': nexts, 'page_num': page_num}, safe=False)


@csrf_exempt
@login_required(login_url='network:login')
def edit_post(request, post_id):
    if request.method =='GET':
        try:
            posts = Post.objects.get(pk=post_id)
        except Post.DoesNotExist:
            return JsonResponse({'error':'no permission to edit post'}, status=404)
        
        if not posts.user == request.user:
            return JsonResponse({'error':'NOT ALLOWED'}, status=401)
        else:
            return JsonResponse(posts.serialize(),safe=False)
    elif request.method == 'PUT':
        try:
            posts = Post.objects.get(pk=post_id)
        except Post.DoesNotExist:
            return JsonResponse({'error':'no permission to edit post'}, status=404)
        
        if not posts.user == request.user:
            return JsonResponse({'error':'NOT ALLOWED'}, status=401)
        else:
            data = json.loads(request.body)
            body = data.get("body", "")
            # Convert email addresses to users
            posts.post_content = body
            posts.save()
            return JsonResponse({"message": 'Posted Successfully'}, status=201)
           

@csrf_exempt
@login_required(login_url='network:login')
def liking(request,post_id):

    if request.method =='PUT':
        try:
            liking_post = Post.objects.get(pk=post_id)
        except Post.DoesNotExist:
            return JsonResponse({'error':'post does not exit or has been deleted'}, status=404)
        
        liked = json.loads(request.body)
        try:
            already_liked = Like.objects.get(
                user=request.user, post=liking_post
            )
        except Like.DoesNotExist:
            already_liked = Like.objects.create(
                user=request.user, post=liking_post
            )

        if liked.get('liked') == False:
            already_liked.delete()
            no_like = Like.objects.filter(post=liking_post).count()
            return JsonResponse({'message': 'Unliked','no_likes':no_like}, safe= False)

        elif liked.get('liked') == True:
            already_liked.likes = True
            already_liked.save()
            no_like = Like.objects.filter(post=liking_post).count()
            return JsonResponse({'message': 'Liked', 'no_likes': no_like}, safe=False)
    else:
        return JsonResponse({"error": "PUT request required."}, status=400)

def view_comment(request, post_id):
    try:
        posts = Post.objects.get(pk=post_id)
        comments =Comment.objects.filter(post=posts)
    except Post.DoesNotExist:
        return JsonResponse({'error':'no such post'})
    return JsonResponse([comment.serialize() for comment in comments], safe=False)

@csrf_exempt
@login_required(login_url='network:login')
def post_comment(request, post_id):

    if request.method == 'PUT':
        try:
            posts = Post.objects.get(pk=post_id)
        except Post.DoesNotExist:
            return JsonResponse({'error':'Post dont exist'}, status=404)
        
        comments = json.loads(request.body)
        the_comment = comments.get('post_com').strip()

        if not the_comment:
            return JsonResponse({'error':'comment is empty'}, status=404)
        else:
            new_comment = Comment.objects.create(user=request.user, post=posts, comment=the_comment)
            new_comment.save()
            no_comment = Comment.objects.filter(post=posts).count()
            return JsonResponse({'message':'comment added','no_comment':no_comment}, status=200)

    else:
        return JsonResponse({'error':'request not a post'})

@csrf_exempt
@login_required(login_url='network:login')
def follow_switch(request, user_id):

    if request.method == "PUT":
        try:
            user = User.objects.get(pk=user_id)
        except User.DoesNotExist:
            return JsonResponse({"error": "User dont eaxit"}, status=404)

        data = json.loads(request.body)
        try:
            followers = Following.objects.filter(
                user=request.user, followings=user)
        except Following.DoesNotExist:
            return JsonResponse({"error": "you do not follow this user."}, status=404)
            
        if data.get('follow').strip() == 'UNFOLLOW':

            followers.delete()
            return JsonResponse({'message': 'Unfollowed'}, status=404)

        elif data.get('follow') == 'FOLLOW':
            if followers:
                return JsonResponse({'error': 'already following this user'}, safe=False)
            else:
                followers = request.user.follower.create()
                followers.followings.add(user)
                followers.save()
                return JsonResponse({'message':'Following now'}, safe=False)
    else:
        return JsonResponse({"error": "GET or PUT request required."}, status=400)


@csrf_exempt
@login_required(login_url='network:login')
def profile_page(request,user_id):
    user = User.objects.get(pk=user_id)
    followings = Following.objects.filter(user=user)
    followers = Following.objects.filter(followings=user)
    posts = Post.objects.filter(user=user).order_by("-pub_date").all()

    following_user = False
    original_user = False

    if user == request.user:
        original_user = True

    for users in followers:
        for use in users.user.all():
            if request.user == use:
                following_user = True

    user = user.serialize()
    followings =[following.serialize() for following in followings]
    followers =[follower.serialize() for follower in followers]
    posts = [post.serialize() for post in posts]
  
    return JsonResponse({'user':user,'following':followings,'follower':followers,'posts':posts,
    'following_user':following_user,'original_user':original_user,
    }, safe=False)


@csrf_exempt
@login_required(login_url='network:login')
def user_posts(request):
    posts = Post.objects.filter(user=request.user).order_by("-pub_date").all()
    return JsonResponse([post.serialize() for post in posts],safe=False)


@csrf_exempt
@login_required(login_url='network:login')
def create_post(request):

    # Composing a new email must be via POST
    if request.method != "POST":
        return JsonResponse({"error": "POST request required."}, status=400)

    data = json.loads(request.body)
    body = data.get("body", "")
    # Convert email addresses to users
    try:
        user_post = Post(user=request.user, post_content=body)
        user_post.save()
    except User.DoesNotExist:
        return JsonResponse({
            "error": f"Login first to add post."
        }, status=400)

    # Create one email for each recipient, plus sender

    return JsonResponse({"message": 'Posted Successfully'}, status=201)


def login_view(request):
    if request.method == "POST":

        # Attempt to sign user in
        username = request.POST["username"]
        password = request.POST["password"]
        user = authenticate(request, username=username, password=password)

        # Check if authentication successful
        if user is not None:
            login(request, user)
            return HttpResponseRedirect(reverse("network:index"))
        else:
            return render(request, "network/login.html", {
                "message": "Invalid username and/or password."
            })
    else:
        return render(request, "network/login.html")


def logout_view(request):
    logout(request)
    return HttpResponseRedirect(reverse("network:index"))


def register(request):
    if request.method == "POST":
        username = request.POST["username"]
        email = request.POST["email"]

        # Ensure password matches confirmation
        password = request.POST["password"]
        confirmation = request.POST["confirmation"]
        if password != confirmation:
            return render(request, "network/register.html", {
                "message": "Passwords must match."
            })

        # Attempt to create new user
        try:
            user = User.objects.create_user(username, email, password)
            user.save()
        except IntegrityError:
            return render(request, "network/register.html", {
                "message": "Username already taken."
            })
        login(request, user)
        return HttpResponseRedirect(reverse("network:index"))
    else:
        return render(request, "network/register.html")
