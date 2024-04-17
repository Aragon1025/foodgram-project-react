from django.contrib.auth import get_user_model
from django.shortcuts import get_object_or_404
from rest_framework import status, viewsets
from rest_framework.decorators import action
from rest_framework.permissions import AllowAny, IsAuthenticated
from rest_framework.response import Response

from api.pagination import CustomPagination
from api.serializers import CustomUserSerializer, SubscriptionSerializer
from users.models import Follow

User = get_user_model()


class CustomUserViewSet(viewsets.ModelViewSet):
    queryset = User.objects.all()
    serializer_class = CustomUserSerializer
    pagination_class = CustomPagination
    permission_classes = (AllowAny,)

    @action(detail=False, methods=['GET'], permission_classes=[IsAuthenticated])
    def me(self, request):
        serializer = self.get_serializer(request.user)
        return Response(serializer.data)

    @action(
        detail=True,
        methods=['post', 'delete'],
        permission_classes=[IsAuthenticated]
    )
    def subscribe(self, request, pk=None):
        subscriber = request.user
        target_user = get_object_or_404(User, pk=pk)
        subscribe_existence = Follow.objects.filter(
            user=subscriber,
            author=target_user
        ).exists()

        if request.method == 'POST':
            if subscribe_existence:
                return Response(
                    {'errors': 'Данная подписка уже существует'},
                    status=status.HTTP_400_BAD_REQUEST
                )
            if subscriber == target_user:
                return Response(
                    {'errors': 'Нельзя подписаться на самого себя'},
                    status=status.HTTP_400_BAD_REQUEST
                )
            subscription = Follow.objects.create(user=subscriber, author=target_user)
            serializer = CustomUserSerializer(
                subscription.author,
                context={'request': request}
            )
            return Response(serializer.data, status=status.HTTP_201_CREATED)

        if not subscribe_existence:
            return Response(
                {'errors': 'Данной подписки не существует'},
                status=status.HTTP_400_BAD_REQUEST
            )
        Follow.objects.filter(user=subscriber, author=target_user).delete()
        return Response(status=status.HTTP_204_NO_CONTENT)

    @action(
        detail=False,
        methods=('get',),
        permission_classes=(IsAuthenticated,),
    )
    def subscriptions(self, request):
        subscriber = request.user
        queryset = User.objects.filter(following__user=subscriber)
        page = self.paginate_queryset(queryset)
        serializer = SubscriptionSerializer(
            page,
            many=True,
            context={'request': request}
        )
        return self.get_paginated_response(serializer.data)
