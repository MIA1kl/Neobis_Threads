from django.urls import path
from .views import (ThreadListView,
                    ThreadCreateView,
                    ThreadLikeView,
                    ThreadCommentView,
                    CommentLikeView,
                    ThreadDeleteView,
                    ThreadWithCommentListView,
                    ThreadQuotationView,
                    ThreadLikedUsersListView,
                    CommentLikedUsersListView,
                    ThreadRepostView
                    )


urlpatterns = [
    path('threads/', ThreadListView.as_view(), name='thread_list'),
    path('threads/<int:pk>/', ThreadDetailView.as_view(), name='thread-detail'), 
    path('create/', ThreadCreateView.as_view(), name='thread_create'),
    path('threads/<int:pk>/delete/', ThreadDeleteView.as_view(), name='thread-delete'),
    path('threads_with_comments/', ThreadWithCommentListView.as_view(), name='thread-with-comments-list'),
    path('threads/<int:thread_id>/like/', ThreadLikeView.as_view(), name='thread-like'),
    path('threads/<int:thread_id>/comments/', ThreadCommentView.as_view(), name='thread-comments'),
    path('comments/<int:comment_id>/like/', CommentLikeView.as_view(), name='comment-like'),
    path('threads/<int:thread_id>/liked_users/', ThreadLikedUsersListView.as_view(), name='thread-liked-users'),
    path('comments/<int:comment_id>/liked_users/', CommentLikedUsersListView.as_view(), name='comment-liked-users'),
    path('threads/<int:thread_id>/quote/', ThreadQuotationView.as_view(), name='thread-quote'),
]
