from django.urls import path

from . import views

app_name = 'chat'

urlpatterns = [
    path(r'', views.index, name='index'),
    path('<str:room_name>/', views.room, name='room'),
    path('<str:group>/<str:slug>/', views.comments, name='commets'),
]