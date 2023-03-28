from django.db.models import Avg
from django.shortcuts import get_object_or_404
from django_filters.rest_framework import DjangoFilterBackend
from rest_framework import status
from rest_framework.decorators import action
from rest_framework.filters import SearchFilter
from rest_framework.mixins import CreateModelMixin
from rest_framework.pagination import LimitOffsetPagination
from rest_framework.permissions import AllowAny, IsAuthenticated
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework.viewsets import GenericViewSet, ModelViewSet
from rest_framework_simplejwt.tokens import RefreshToken
from reviews.models import Category, Genre, Title
from users.models import User

from .filters import TitleFilter
from .mixins import CreateDestroyListViewSet
from .permissions import (IsAdmin, IsAdminOrReadOnly,
                          IsAuthorOrStaffOrAuthenticatedCreateOrReadOnly)
from .serializers import (CategorySerializer, CommentSerializer,
                          GenreSerializer, ReviewSerializer,
                          TitlePostSerializer, TitleSerializer, UserSerializer,
                          UserSignUpSerializer)
from .utils import check_confirmation_code


class SignUpViewSet(CreateModelMixin, GenericViewSet):
    """Вью регистрации пользователя."""

    queryset = User.objects.all()
    serializer_class = UserSignUpSerializer
    permission_classes = (AllowAny,)

    def create(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        self.perform_create(serializer)
        headers = self.get_success_headers(serializer.data)
        return Response(
            serializer.data,
            status=status.HTTP_200_OK,
            headers=headers
        )


class TokenObtainView(APIView):
    """Вью для получения токена."""

    permission_classes = (AllowAny,)

    def post(self, request):
        username = request.data.get('username')
        confirmation_code = request.data.get('confirmation_code')

        if not confirmation_code:
            return Response(
                {'confirmation_code': ['Обязательное поле.']},
                status=status.HTTP_400_BAD_REQUEST,
            )

        if not username:
            return Response(
                {'username': ['Обязательное поле.']},
                status=status.HTTP_400_BAD_REQUEST,
            )

        user = get_object_or_404(User, username=username)

        if not check_confirmation_code(user, confirmation_code):
            return Response(
                {'confirmation_code': ['Неверный код подтверждения.']},
                status=status.HTTP_400_BAD_REQUEST,
            )

        return Response(
            {'token': str(RefreshToken.for_user(user).access_token)},
            status=status.HTTP_200_OK,
        )


class UserViewSet(ModelViewSet):
    """Вью для работы с пользователями."""

    queryset = User.objects.all()
    serializer_class = UserSerializer
    permission_classes = (IsAdmin,)
    lookup_field = 'username'
    filter_backends = (SearchFilter,)
    search_fields = ('username',)

    @action(
        detail=False,
        methods=('get', 'patch', 'put'),
        permission_classes=(IsAuthenticated,),
    )
    def me(self, request):
        """Метод для url: 'me/'."""
        if request.method == 'GET':
            serializer = self.get_serializer(
                instance=request.user,
                partial=True,
            )

            return Response(serializer.data, status=status.HTTP_200_OK)

        serializer = self.get_serializer(
            instance=request.user,
            data=request.data,
            partial=True,
        )
        serializer.is_valid()
        serializer.save()

        return Response(serializer.validated_data, status=status.HTTP_200_OK)


class CategoryViewSet(CreateDestroyListViewSet):
    """Вью для работы с категориями."""

    queryset = Category.objects.all()
    serializer_class = CategorySerializer
    permission_classes = (IsAdminOrReadOnly,)
    pagination_class = LimitOffsetPagination
    filter_backends = (SearchFilter,)

    search_fields = ('name', )


class GenreViewSet(CreateDestroyListViewSet):
    """Вью для работы с жанрами."""

    queryset = Genre.objects.all()
    serializer_class = GenreSerializer
    permission_classes = (IsAdminOrReadOnly,)
    pagination_class = LimitOffsetPagination
    filter_backends = (SearchFilter,)

    search_fields = ('name', )


class TitleViewSet(ModelViewSet):
    """Вью для работы с произведениями."""

    queryset = Title.objects.all().annotate(
        rating=Avg('reviews__score'),
    ).order_by('name')
    filter_backends = (DjangoFilterBackend,)
    filterset_class = TitleFilter
    permission_classes = (IsAdminOrReadOnly,)
    pagination_class = LimitOffsetPagination

    def get_serializer_class(self):
        if self.action in ('create', 'partial_update'):
            return TitlePostSerializer
        return TitleSerializer


class ReviewViewSet(ModelViewSet):
    "Вью для работы с отзывами."

    serializer_class = ReviewSerializer
    permission_classes = [IsAuthorOrStaffOrAuthenticatedCreateOrReadOnly, ]

    def get_queryset(self):
        title = get_object_or_404(Title, id=self.kwargs.get('title_id'))
        return title.reviews.all()

    def perform_create(self, serializer):
        title = get_object_or_404(Title, id=self.kwargs.get('title_id'))
        serializer.save(author=self.request.user, title=title)


class CommentViewSet(ModelViewSet):
    "Вью для работы с комментариями."

    serializer_class = CommentSerializer
    permission_classes = [IsAuthorOrStaffOrAuthenticatedCreateOrReadOnly, ]

    def get_queryset(self):
        title = get_object_or_404(Title, id=self.kwargs.get('title_id'))
        review = get_object_or_404(
            title.reviews, id=self.kwargs.get('review_id'))
        return review.comments.all()

    def perform_create(self, serializer):
        title = get_object_or_404(Title, id=self.kwargs.get('title_id'))
        review = get_object_or_404(
            title.reviews, id=self.kwargs.get('review_id'))
        serializer.save(author=self.request.user, review=review)
