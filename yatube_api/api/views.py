from django.shortcuts import get_object_or_404
from rest_framework import viewsets

from .serializers import CommentSerializer, FollowSerializer
from .serializers import GroupSerializer, PostSerializer
from posts.models import Group, Post, Follow
from .permissions import AuthorOrReadOnly, ReadOnly
from rest_framework import permissions
from rest_framework.pagination import LimitOffsetPagination
from rest_framework import filters
from rest_framework import mixins


class ListCreateViewSet(mixins.CreateModelMixin, mixins.ListModelMixin,
                        viewsets.GenericViewSet):
    pass


class PostViewSet(viewsets.ModelViewSet):
    queryset = Post.objects.all()
    serializer_class = PostSerializer
    permission_classes = (AuthorOrReadOnly,)
    pagination_class = LimitOffsetPagination

    def perform_create(self, serializer):
        serializer.save(author=self.request.user)

    def get_permissions(self):
        if self.action == 'retrieve':
            return (ReadOnly(),)
        return super().get_permissions()


class GroupViewSet(viewsets.ReadOnlyModelViewSet):
    queryset = Group.objects.all()
    serializer_class = GroupSerializer
    permission_classes = (permissions.IsAuthenticatedOrReadOnly,)


class CommentViewSet(viewsets.ModelViewSet):
    serializer_class = CommentSerializer
    permission_classes = (AuthorOrReadOnly,)

    def perform_create(self, serializer):
        post_id = self.kwargs.get('post_id')
        post = get_object_or_404(Post, pk=post_id)
        serializer.save(author=self.request.user,
                        post=post)

    def get_queryset(self):
        post_id = self.kwargs.get('post_id')
        post = get_object_or_404(Post, pk=post_id)
        new_queryset = post.comments.all()
        return new_queryset

    def get_permissions(self):
        if self.action == 'retrieve':
            return (ReadOnly(),)
        return super().get_permissions()


class FollowViewSet(ListCreateViewSet):
    filter_backends = (filters.SearchFilter,)
    search_fields = ('following__username',)
    serializer_class = FollowSerializer

    def perform_create(self, serializer):
        serializer.save(user=self.request.user)

    def get_queryset(self):
        follows = Follow.objects.filter(user=self.request.user)
        return follows
