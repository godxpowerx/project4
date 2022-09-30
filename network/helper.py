from django.core.paginator import Paginator
from .models import Like

def addPaginator(init_post,page):
    # create a django Paginator object which sends only 10 post per page
    paginate = Paginator(init_post, 10)

    # paginate.get_page(p) returns post from a particular pages num i.e (p) and
    # and stores it as a list object.
    total_post = paginate.get_page(page)

    # returns the current page number
    page_num = total_post.number

    # returns the True if there is a next page else False
    next = total_post.has_next()

    # returns the True if there is a previous page else False
    prev = total_post.has_previous()

    # paginate.num_pages returns the number of page generated depending on number of post and
    # how many per page.
    num_of_pages = paginate.num_pages

    return {'total': total_post, 'total_page': num_of_pages,
            'prev': prev, 'next': next, 'page_num': page_num}

def is_liked(posts,request,pos):
    
    # check if the current user liked this post if liked return True else False
    likes = Like.objects.filter(post=posts , user = request.user)
    if likes:
        pos['liked'] = True
    else:
        pos['liked'] = False

def is_original_user(posts,request,pos):

     # if the post was created by the current user then original user is True else False
    if posts.user == request.user:
        pos['original_users'] = True
    else:
        pos['original_users'] = False
