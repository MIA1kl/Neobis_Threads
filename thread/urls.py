from django.urls import path
from .views import ThreadListView, ThreadCreateView, ThreadLikeView, ThreadCommentView, CommentLikeView



urlpatterns = [
    path('threads/', ThreadListView.as_view(), name='thread_list'),
    path('create/', ThreadCreateView.as_view(), name='thread_create'),
    path('threads/<int:thread_id>/like/', ThreadLikeView.as_view(), name='thread-like'),
    path('threads/<int:thread_id>/comments/', ThreadCommentView.as_view(), name='thread-comments'),
    path('comments/<int:comment_id>/like/', CommentLikeView.as_view(), name='comment-like'),
]
