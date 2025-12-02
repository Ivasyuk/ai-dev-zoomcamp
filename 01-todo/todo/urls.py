from django.urls import path
from . import views

urlpatterns = [
    path('', views.todo_list, name='todo_list'),
    path('todo/<int:pk>/', views.todo_detail, name='todo_detail'),
    path('create/', views.todo_create, name='todo_create'),
    path('todo/<int:pk>/update/', views.todo_update, name='todo_update'),
    path('todo/<int:pk>/delete/', views.todo_delete, name='todo_delete'),
    path('todo/<int:pk>/complete/', views.todo_complete, name='todo_complete'),
    path('stats/', views.todo_stats, name='todo_stats'),
]
