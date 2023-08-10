from django.urls import path
from .views import ThreadListView, ThreadCreateView, ThreadLikeView



urlpatterns = [
    path('threads/', ThreadListView.as_view(), name='thread_list'),
    path('create/', ThreadCreateView.as_view(), name='thread_create'),
    path('threads/<int:thread_id>/like/', ThreadLikeView.as_view(), name='thread-like'),
]
