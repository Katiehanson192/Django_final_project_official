from django.dispatch import receiver
from django.shortcuts import render, redirect
from .forms import PostForm,ProfileForm, RelationshipForm
from .models import Post, Comment, Like, Profile, Relationship
from datetime import datetime, date

from django.contrib.auth.decorators import login_required
from django.http import Http404


# Create your views here.

# When a URL request matches the pattern we just defined, 
# Django looks for a function called index() in the views.py file. 

def index(request):
    """The home page for Learning Log."""
    return render(request, 'FeedApp/index.html')



@login_required #decorator = varifies something, once varified, allows use to following function. Restricts access unless user is logged in
def profile(request): #access DB and posting things to website
    #only want ppl logged in to have access to it. (hence decorator)
    profile = Profile.objects.filter(user=request.user) #user refers to currently logged in user. user = fields in profile model. user filter b/c get doesn't work w/ exists
    if not profile.exists(): #checks to see if user has profile, if not, creates one
        Profile.objects.create(user=request.user)
    profile = Profile.objects.get(user=request.user) #can use ".get()" here b/c not working w/ ".exists()"

    if request.method != 'POST':
        form = ProfileForm(instance=profile) #instance = profile in case user already has a profile and wants to update it
    else: #request method = "POST", trying to save to DB
        form = ProfileForm(instance=profile, data=request.POST) #grab all info from Profile class form for that specific user instance
                                                                #if user has filled out all information described in Profile class in forms.py, the form is valid
        if form.is_valid():
            form.save()
            return redirect('FeedApp:profile') #keeps them on the profile page

    context = {'form': form}
    return render(request, 'FeedApp/profile.html', context)

@login_required
def myfeed(request): #want to see all of our posts + all likes and comments
    comment_count_list = []
    like_count_list = [] #create empty lists b/c there are multiple comments 
    posts = Post.objects.filter(username=request.user).order_by('-date_posted')#use filter if >1, use get() if only 1
                                                                               #order_by = descending order
    for p in posts:
        c_count = Comment.objects.filter(post=p).count()#provides number of comments on each post
        l_count = Like.objects.filter(post=p).count() #provides number of likes on each post
        comment_count_list.append(c_count)
        like_count_list.append(l_count)

    #iterate through the comments and likes of each post together
    zipped_list = zip(posts,comment_count_list,like_count_list)

    context = {'posts':posts, 'zipped_list': zipped_list} #context is how we pass all of the things in this function to myfeed in urls?
    return render(request, 'FeedApp/myfeed.html', context)

@login_required
def new_post(request):
    #check if GET or POST request
    #pulls info from forms.py --> PostForm
        #form only needs 2 pieces of info: description and image
    if request.method != 'POST':
        form = PostForm()
    else: 
        form=PostForm(request.POST, request.FILES) #Pull all the data from the PostForm and the images
        if form.is_valid():
           new_post = form.save(commit=False) #don't write to DB yet (don't have username info yet), just save instance.
           new_post.username=request.user
           new_post.save()
           return redirect('FeedApp:myfeed') #once user posts, keep them on MyFeed page so they can see their post
    
    context= {'form':form}
    return render(request, 'FeedApp/new_post.html', context)

@login_required
def friendsfeed(request):
    comment_count_list = []
    like_count_list = [] #create empty lists b/c there are multiple comments 
    friends=Profile.objects.filter(user=request.user).values('friends')
    posts = Post.objects.filter(username__in=friends).order_by('-date_posted')#use filter if >1, use get() if only 1
                                                                               #order_by = descending order
    for p in posts:
        c_count = Comment.objects.filter(post=p).count()#provides number of comments on each post
        l_count = Like.objects.filter(post=p).count() #provides number of likes on each post
        comment_count_list.append(c_count)
        like_count_list.append(l_count)

    #iterate through the comments and likes of each post together
    zipped_list = zip(posts,comment_count_list,like_count_list)

    #check to see if "Like" button was clicked
    if request.method == 'POST' and request.POST.get("like"):
        post_to_like = request.POST.get("like") #getting the value of the "like" button, which is the post_id (from line 36 in friendsfeed template)
        print(post_to_like)
        #keep same person from liking post multiple times
        like_already_exists = Like.objects.filter(post_id=post_to_like,username=request.user) #if the same user has already liked the same post_id
        if not like_already_exists.exists():
            Like.objects.create(post_id=post_to_like,username=request.user)
            return redirect("FeedApp:friendsfeed") #redirects user back to the friendsfeed (essentially refreshes the page)

    context = {'posts':posts, 'zipped_list': zipped_list} #context is how we pass all of the things in this function to myfeed in urls?
    return render(request, 'FeedApp/friendsfeed.html', context)


'''
comments class is different from others b/c we don't have a form for it. 
Need to mannually create the fields.
'''

@login_required
def comments(request, post_id): #post_id is needed b/c we have to link each comment to a particular post
                                #Comments class in models.py file has post as a FK 
    if request.method == 'POST' and request.POST.get("btn1"): #check if sending info to DB AND if "submit" button has been clicked (submit button variable = "btn1")
        comment = request.POST.get("comment") #request.get() = getting text in comment box
        Comment.objects.create(post_id=post_id, username=request.user,text=comment, date_added=date.today()) #capital C b/c refering to the Comments model (in model.py file)
                                    #post = a field in Comments model, Django assigns it an ID automatically
                                    #to call that ID, you use the DB column name_id
                                    #we need the ID number, NOT the actual post text itself, to connect to a particular post

                                    #need post_id, username, text, & date_added b/c those are the fields assigned in the Comments model
                                        #creates a new row in comment model w/ those fields in the DB
        

    '''
    once comment = created, refresh screen so shows up on the page
    but need to get ALL comments on the post once comment = submitted
    '''
    comments = Comment.objects.filter(post=post_id)
    post = Post.objects.get(id=post_id)

    context = {'post':post,'comments':comments}
    return render(request, 'FeedApp/comments.html', context)

@login_required
def friends(request):
    #get the admin_profile and user profile to create the first relationship
    admin_profile = Profile.objects.get(user=1)
    user_profile = Profile.objects.get(user=request.user)

    #to get User's Friends
    user_friends = user_profile.friends.all()
    user_friends_profiles = Profile.objects.filter(user__in=user_friends)

    #get list of Friend Requests sent
    user_relationships = Relationship.objects.filter(sender=user_profile)
    request_sent_profiles = user_relationships.values('receiver') #sender and receiver are FK in the Relationship object in models.py file

    #list of who we can send friend requests to
        #show everyone in the system who the user is not already friends with + exclude user + exclude friend requests alrady sent
    all_profiles = Profile.objects.exclude(user=request.user).exclude(id__in=user_friends_profiles).exclude(id__in=request_sent_profiles)

    #get friend requests received by the user
    request_received_profiles = Relationship.objects.filter(receiver=user_profile,status='sent')

    #create user's 1st relationship w/ admin (if this is the first time to access friend request page)
        #need to do this b/c relationship table needs to have at least 1 row in it for the program to run smoothly
    if not user_relationships.exists(): #'filter' works with exists, 'get' doesn't
        Relationship.objects.create(sender=user_profile,receiver=admin_profile,status='sent') #need user/admin profiles bc their profile objects in models.py file
        #relationship = Relationship.objects.filter(sender=user_profile,status='sent')

    #check to see WHICH submit button was pressed (sending a friend request or accepting a friend request)

    #this is to process all send requests
    if request.method == 'POST' and request.POST.get("send_requests"): #if button pressed = "send requests"
        receivers = request.POST.getlist("send_requests") #getlist b/c this will be checkboxes in HTML and multiple can be checked
                                                        #value of checkbox = ID of user
        print(receivers)
        for receiver in receivers:
            receiver_profile = Profile.objects.get(id=receiver)
            Relationship.objects.create(sender=user_profile, receiver=receiver_profile, status='sent')
        return redirect('FeedApp:friends') #keeps them on the same page

    #this is to process all receive requests
    if request.method == 'POST' and request.POST.get("receive_requests"): #if button pressed = "receive_requests"
        senders = request.POST.getlist("receive_requests") #getlist b/c this will be checkboxes in HTML and multiple can be checked
        
        for sender in senders:
            #update relationship model for the sender to status = 'accepted'
            Relationship.objects.filter(id=sender).update(status='accepted')

            #create a relationship object to access the sender's user id
            #to add to the friends list of the user
            relationship_obj = Relationship.objects.get(id=sender)
            user_profile.friends.add(relationship_obj.sender.user) #.sender.user = get the ID of the user who sent the request and add that user_id to the list of friends for the current usesr

            #add the user (user B) to the friends list of the sender's (user A) profile
            relationship_obj.sender.friends.add(request.user) #relationship_obj.sender = represents a profile, .friends = that profile's friends, .add = adds current user (user B) to sender's (user A) friend list
        
    context = {'user_friends_profiles': user_friends_profiles, 'user_relationships':user_relationships, 
                'all_profiles':all_profiles, 'request_received_profiles': request_received_profiles}
    return render(request, 'FeedApp/friends.html', context)





