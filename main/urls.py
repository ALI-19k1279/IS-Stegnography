from django.urls import path
from . import views

urlpatterns = [
    path('', views.home, name='home'),
    path('home', views.home, name='home'),
    path('sign-up', views.sign_up, name='sign_up'),
    path('text-steg', views.encode, name='textSteg'),
     path('decode', views.decode, name='decode'),
    path('image-steg', views.steg, name='imageSteg'),
    path('audio-steg', views.steg, name='audioSteg'),
    #path('post/<str:type>', views.encode, name='textSteg'),
    path('delete/<str:filename>/<int:_id>', views.deleteRec, name='delete'),
    # path('create-post', views.create_post, name='create_post'),
]