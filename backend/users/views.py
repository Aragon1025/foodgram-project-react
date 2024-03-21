from django.contrib.auth import get_user_model
from django.shortcuts import get_object_or_404
from rest_framework import status, viewsets
from rest_framework.decorators import action
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response

from api.pagination import CustomPagination
from api.serializers import UserSerializer, FavoriteSerializer
from users.models import Follow

User = get_user_model()


class CustomUserViewSet(viewsets.ModelViewSet):
    """
    Пользовательское представление для работы с пользователями.
    """
    queryset = User.objects.all()
    serializer_class = UserSerializer
    pagination_class = CustomPagination

    @action(
        detail=True,
        methods=('POST', 'DELETE',),
        permission_classes=[IsAuthenticated]
    )
    def subscribe(self, request, pk=None):
        """
        Действие для подписки на пользователя.

        Позволяет текущему пользователю подписаться на другого пользователя.
        """
        user = request.user
        author = get_object_or_404(User, pk=pk)

        if request.method == 'POST':
            serializer = FavoriteSerializer(
                data={'user': user.pk, 'author': author.pk},
                context={'request': request, 'author': author}
            )
            serializer.is_valid(raise_exception=True)
            serializer.save()
            return Response(serializer.data, status=status.HTTP_201_CREATED)

        elif request.method == 'DELETE':
            follow_instance = Follow.objects.filter(user=user, author=author)
            if follow_instance.exists():
                follow_instance.delete()
                return Response(status=status.HTTP_204_NO_CONTENT)
            else:
                return Response(status=status.HTTP_404_NOT_FOUND)

    @action(
        detail=False,
        permission_classes=[IsAuthenticated]
    )
    def subscriptions(self, request):
        user = request.user
        queryset = user.subscribing.all()
        page = self.paginate_queryset(queryset)
        serializer = UserSerializer(page, many=True, context={'request': request})
        return self.get_paginated_response(serializer.data)
