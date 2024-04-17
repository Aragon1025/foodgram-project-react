from django.contrib.auth import get_user_model
from django.shortcuts import get_object_or_404
from rest_framework import status
from rest_framework.decorators import action
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response

from djoser.views import UserViewSet

from api.permissions import CreateOrAuthenticatedUser
from api.serializers import CustomUserSerializer, SubscriptionSerializer
from users.models import Follow

User = get_user_model()


class CustomUserViewSet(UserViewSet):
    queryset = User.objects.all()
    serializer_class = CustomUserSerializer
    permission_classes = (CreateOrAuthenticatedUser,)

    @action(
        detail=True,
        methods=['post', 'delete'],
        permission_classes=[IsAuthenticated]
    )
    def subscribe(self, request, id):
        subscriber = request.user
        target_user = get_object_or_404(User, pk=id)
        subscribe_existence = Follow.objects.filter(
            user=subscriber,
            author=target_user
        ).exists()

        if request.method == 'POST':
            if subscribe_existence:
                return Response(
                    {'errors': 'Подписка на пользователя уже существует!'},
                    status=status.HTTP_400_BAD_REQUEST
                )
            if subscriber == target_user:
                return Response(
                    {'errors': 'Подписка на самого себя невозможна!'},
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
                {'errors': 'Подписка не существует!'},
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
