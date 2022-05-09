from django.urls import path
from . import views

app_name = 'FeedApp'

urlpatterns = [
            path('', views.index, name='index'),
    path('profile/', views.profile, name='profile'),
    path('myfeed', views.myfeed, name= 'myfeed'), #links to the 'My Feed button'
    path('new_post/', views.new_post, name='new_post'),
    path('friendsfeed',views.friendsfeed, name='friendsfeed'),
    path('comments/<int:post_id>/', views.comments,name='comments'), #<int:post_id> = needed b/c need to link comment to a particular post
                                                                    #b/c post = FK in Comment class in the models.py file
    path('friends/',views.friends, name='friends'),
    
    ]

    