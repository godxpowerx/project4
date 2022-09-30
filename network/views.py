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
from .helper import addPaginator, is_liked, is_original_user
'''
most function returns the a json object after verifying and validating input.
thus this application works mostly as an Api 
using Javascript to display and format how information is handled within the front-end

'''
'''
@login_required annotation is used to make sure the user accessing the information is verified and signed in 
if not the user is directed to the login page
'''



# retrieve all the post from all the user
def index(request):

    total_post = Post.objects.all()

    # retrieve the post and order it by the newest one
    total_post = total_post.order_by("-pub_date").all()
    return render(request, "network/index.html",{
        'all_post': total_post
    })



def all_post(request, page):
    # retrieve all the post 
    total_post = Post.objects.all()

    # and order it by the newest ones first
    init_post = total_post.order_by("-pub_date").all()

    # create a new paginator using the addpaginator helper function
    paginated = addPaginator(init_post, page)

    # create a empty list objects to append each post after changes has been made through iteration
    total = []

    # loops through the new list of post object return by addpaginator 
    # and add extra information.
    for posts in paginated['total']:

        # for each post convert it to a object which can easily be converted to Json 
        # i.e ( dict object in python)
        pos = posts.serialize()

        # if the post was created by the current user then original user is True else False
        is_original_user(posts, request, pos)
        
        # check if the current user liked this post if liked return True else False
        is_liked(posts, request, pos)

        # append the current post to the created list called total after converting to json-type 
        # object and added extra information
        total.append(pos)
    
    # change the content of  paginated['total'] with the new improved content
    paginated['total'] = total
       
    # return the information as a JSON objects and safe=false because total contain a pythin dict
    return JsonResponse(paginated, safe=False)


# csrf_exempt used to by-pass CSRF checks but should not b used during production.
@csrf_exempt
@login_required(login_url='network:login')
def following_post(request, page):
    '''
    this function retrieves only post made user which the current user is following and return as a Json formats
    '''

    # create an empty list object
    post_follow =[]

    # return a list of following objects 
    follow =  Following.objects.filter(user=request.user)

    # loops through the list of following objects (follow) and for each objects get the user 
    # the current user is following 
    for u in follow:
       init_post = Post.objects.filter(user=u.followings.first())
       post_follow.extend(init_post) 

    # sort through and place the current at the top
    post_follow.sort(key=attrgetter('pub_date'), reverse=True)

    # create a new paginator using the addpaginator helper function
    paginated = addPaginator(post_follow, page)

    # create an empty list to add the list of post object including
    # extra information for each post object
    total = []

    # loop through the list of post object return from addpaginator
    for posts in paginated['total']:
        # for each post convert it to a object which can easily be converted to Json
        # i.e ( dict object in python)
        pos = posts.serialize()

        # if the post was created by the current user then original user is True else False
        is_original_user(posts, request, pos)

        # check if the current user liked this post if liked return True else False
        is_liked(posts, request, pos)

        # append the current post to the created list called total after converting to json-type
        # object and added extra information
        total.append(pos)

    # change the content of  paginated['total'] with the new improved content
    paginated['total'] = total

    # return the information as a JSON objects and safe=false because total contain a pythin dict
    return JsonResponse(paginated, safe=False)

# csrf_exempt used to by-pass CSRF checks but should not b used during production.
@csrf_exempt
@login_required(login_url='network:login')
def edit_post(request, post_id):

    '''
    This function allows the user to edit a post which was already created by first checking if the 
    request was a GET or PUT, if the request was GET it return post to be edited to the user.
    if the request user do not match the original user the request is denied to save an edited 
    post the request method has to a PUT and validation are made to determine if the edit should
    be save
    '''

    # checks if the request method is a GET
    if request.method =='GET':

        # if its a GET, try to  access that post if an error is created
        # return an error back to the user.
        try:
            posts = Post.objects.get(pk=post_id)
        except Post.DoesNotExist:
            return JsonResponse({'error':'no permission to edit post'}, status=404)
        
        # if the current user do not match the user who created the post return an error
        # else return the post back to the user.
        if not posts.user == request.user:
            return JsonResponse({'error':'NOT ALLOWED'}, status=401)
        else:
            return JsonResponse(posts.serialize(),safe=False)

    # checks if the request method is a PUT
    elif request.method == 'PUT':

        # try to  access that post if an error is created
        # return an error back to the user.
        try:
            posts = Post.objects.get(pk=post_id)
        except Post.DoesNotExist:
            return JsonResponse({'error':'no permission to edit post'}, status=404)
        
        # if the current user do not match the user who created the post return an error
        # else apply the changes made.
        if not posts.user == request.user:
            return JsonResponse({'error':'NOT ALLOWED'}, status=401)
        else:

            # retrieve the data from the returned json 
            data = json.loads(request.body)

            # get the post content called body
            body = data.get("body", "")

            # change the content of the post with the edited content and save it.
            posts.post_content = body
            posts.save()

            # if successful let the user know
            return JsonResponse({"message": 'Posted Successfully'}, status=201)
           

# csrf_exempt used to by-pass CSRF checks but should not b used during production.
@csrf_exempt
@login_required(login_url='network:login')
def liking(request,post_id):

    '''
    liking checks and updates post if the user choose to like it and unlike it 
    if the user is trying to unlike a post the returned json should be false else true for liking a post
    '''

    # checks if the request methods is a PUT
    if request.method =='PUT':
        # try to access the post using the post_id provided in the parameter
        try:
            liking_post = Post.objects.get(pk=post_id)
        
        # return an error if posts does not exist
        except Post.DoesNotExist:
            return JsonResponse({'error':'post does not exit or has been deleted'}, status=404)
        
        # access the json file provided and get the body containing the information 
        # needed to determine if the post was like or unliked
        liked = json.loads(request.body)

        # try to access and check if the post was already liked before 
        try:
            already_liked = Like.objects.get(
                user=request.user, post=liking_post
            )

        # if like dont exist meaning the post was never liked by this user
        except Like.DoesNotExist:
            # create a new like if none existed
            already_liked = Like.objects.create(
                user=request.user, post=liking_post
            )

        # if the user is trying to unlike a post 
        if liked.get('liked') == False:
            # delete the already like or created like for the post
            already_liked.delete()

            # and return the new number of likes for that post
            no_like = Like.objects.filter(post=liking_post).count()
            return JsonResponse({'message': 'Unliked','no_likes':no_like}, safe= False)

        # else is the user was trying to like a post
        elif liked.get('liked') == True:

            # change the Like.likes attritube from False to True and save it
            already_liked.likes = True
            already_liked.save()

            # return the current number likes for that post
            no_like = Like.objects.filter(post=liking_post).count()
            return JsonResponse({'message': 'Liked', 'no_likes': no_like}, safe=False)
    else:
        # request must be a PUT method before changes can be made
        return JsonResponse({"error": "PUT request required."}, status=400)

def view_comment(request, post_id):

    '''
    view_comment provides access to the comments for a particular post,
    make the post exist and returns the comments using a json format
    '''
    # trys to make connection withn the db and get access to the post and its comments
    try:
        posts = Post.objects.get(pk=post_id)
        comments =Comment.objects.filter(post=posts)
    except Post.DoesNotExist:
        # if post do not exist returns an error 
        return JsonResponse({'error':'no such post'})
    # return a serialize json formatted list of comment 
    return JsonResponse([comment.serialize() for comment in comments], safe=False)


# csrf_exempt used to by-pass CSRF checks but should not b used during production.
@csrf_exempt
@login_required(login_url='network:login')
def post_comment(request, post_id):
    '''
    creates a new comment for a particular post and a particular user
    '''
    
    # checks if the request method is PUT
    if request.method == 'PUT':
        try:
            # try to access the post to add the comment using the post_id provided in the parameter
            posts = Post.objects.get(pk=post_id)
        except Post.DoesNotExist:
            # if the post do not exist return an error
            return JsonResponse({'error':'Post dont exist'}, status=404)
        
        # access the request.body provided in the return json object
        comments = json.loads(request.body)
        # from the request.body get the post content called 'post_com'
        the_comment = comments.get('post_com').strip()

        #if the post is empty or do not exist return an error
        if not the_comment:
            return JsonResponse({'error':'comment is empty'}, status=404)
        else:
            # else create a new comment object using the provided 
            # comment, post , the user making the comment, and save it to the DB
            new_comment = Comment.objects.create(user=request.user, post=posts, comment=the_comment)
            new_comment.save()

            # return back the current number of availabe comment
            no_comment = Comment.objects.filter(post=posts).count()
            return JsonResponse({'message':'comment added','no_comment':no_comment}, status=200)

    else:
        # request must be a PUT method before changes can be made
        return JsonResponse({'error':'request not a post'})

# csrf_exempt used to by-pass CSRF checks but should not b used during production.
@csrf_exempt
@login_required(login_url='network:login')
def follow_switch(request, user_id):
    '''
        Makes following and unfollowing a user possible. recieves a json object with instruction
        FOLLOW or UNFOLLOW
    '''

    # checks to make sure the request method is PUT
    if request.method == "PUT":
        try:
            # checks if the user the current is try to follow exist
            user = User.objects.get(pk=user_id)
        except User.DoesNotExist:
            # if the user do not exist returen an error message
            return JsonResponse({"error": "not allowed"}, status=404)
        # loads the request.body from the json object
        data = json.loads(request.body)

        # access and checks if the current user is already following the user
        followers = Following.objects.filter(
                user=request.user, followings=user)
        
        # if the current user is trying to unfollow this user 
        # and if the current user was following the user    
        if data.get('follow').strip() == 'UNFOLLOW':
            if not followers:
                return JsonResponse({'error': 'do not follow this user'}, safe=False)
            else:
                # deleting the following makes sure the current user
                # no longer follows the user
                followers.delete()
                return JsonResponse({'message': 'Unfollowed'}, status=404)

        # if the current user is trying to Follow this user
        # and if the current user was following the user
        elif data.get('follow') == 'FOLLOW':
            if followers:
                return JsonResponse({'error': 'already following this user'}, safe=False)
            else:
                # first we create a follower object with the current user
                followers = request.user.follower.create()
                #and then add the user whom this current user want to follow and save it
                followers.followings.add(user)
                followers.save()
                return JsonResponse({'message':'Following now'}, safe=False)
    else:
        # request must be a PUT method before changes can be made
        return JsonResponse({"error": " PUT request required."}, status=400)


# csrf_exempt used to by-pass CSRF checks but should not b used during production.
@csrf_exempt
@login_required(login_url='network:login')
def profile_page(request,user_id):

    '''
    retrieve information about  a user  to be displayed to other user 
    including post, following, followers, and general user public information

    '''

    # retrieve the user list of followers and followings and posts
    user = User.objects.get(pk=user_id)
    followings = Following.objects.filter(user=user)
    followers = Following.objects.filter(followings=user)
    posts = Post.objects.filter(user=user).order_by("-pub_date").all()

    # declare variables to be used to determine if the current user
    # is following this user and is the or the owner of this user page and assign False to both
    following_user = False
    original_user = False

    # the user is the current user then True the user is the original_user
    if user == request.user:
        original_user = True

    # loop through the user following object and
    # check if the current user is following this user,
    # if the current user is following following_user = True.
    for users in followers:
        for use in users.user.all():
            if request.user == use:
                following_user = True

    # serialize every information retrieve from the database earlier
    user = user.serialize()
    followings =[following.serialize() for following in followings]
    followers =[follower.serialize() for follower in followers]
    posts = [post.serialize() for post in posts]
    
    # formatted to json and returned
    return JsonResponse({'user':user,'following':followings,'follower':followers,'posts':posts,
    'following_user':following_user,'original_user':original_user,
    }, safe=False)


# csrf_exempt used to by-pass CSRF checks but should not b used during production.
@csrf_exempt
@login_required(login_url='network:login')
def user_posts(request):
    '''
    retrieve all post created by the current user, sorted based on the newest at the top and return it 
    '''
    posts = Post.objects.filter(user=request.user).order_by("-pub_date").all()
    return JsonResponse([post.serialize() for post in posts],safe=False)


# csrf_exempt used to by-pass CSRF checks but should not b used during production.
@csrf_exempt
@login_required(login_url='network:login')
def create_post(request):
    '''
        create new post using the POST request methods for a post to be created a user need to be available
    '''
    # Create a new post via POST
    if request.method != "POST":
        return JsonResponse({"error": "POST request required."}, status=400)

    data = json.loads(request.body)
    body = data.get("body", "")
    
    # add the post and attach the current user object and save it
    try:
        user_post = Post(user=request.user, post_content=body)
        user_post.save()
    except User.DoesNotExist:
        return JsonResponse({
            "error": f"Login first to add post."
        }, status=400)

    # return a success message if successful
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
