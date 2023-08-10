from django.urls import path
from .views import ThreadListView, ThreadCreateView



urlpatterns = [
    path('threads/', ThreadListView.as_view(), name='thread_list'),
    path('create/', ThreadCreateView.as_view(), name='thread_create'),
]