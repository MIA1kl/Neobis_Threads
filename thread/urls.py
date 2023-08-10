from django.urls import path
from .views import ThreadListView, ThreadCreateView, ThreadLikeView, ThreadDeleteView

urlpatterns = [
    path('threads/', ThreadListView.as_view(), name='thread_list'),
    path('create/', ThreadCreateView.as_view(), name='thread_create'),
    path('threads/<int:pk>/like/', ThreadLikeView.as_view(), name='thread-like'),
    path('threads/<int:pk>/delete/', ThreadDeleteView.as_view(), name='thread-delete'),  
]
