from django.db.models import Q
from django.shortcuts import get_object_or_404
from rest_framework import serializers
from rest_framework.validators import UniqueValidator
from reviews.models import Category, Comments, Genre, GenreTitle, Review, Title
from users.models import User

from .utils import get_confirmation_code, send_confirmation_email


class UserSignUpSerializer(serializers.Serializer):
    """Сериализатор для регистрации."""

    username = serializers.CharField(max_length=150, required=True)
    email = serializers.EmailField(max_length=256, required=True)

    def validate_username(self, username):
        if username == 'me':
            raise serializers.ValidationError(
                'Зарезервированный username. Используйте другой.'
            )

        return username

    def validate(self, data):
        email = data['email']
        username = data['username']
        user = User.objects.filter(Q(username=username) | Q(email=email))

        if user and (user.get().email != email
                     or user.get().username != username):
            raise serializers.ValidationError(
                'Имя пользователя или email не соответствуют.'
            )

        return data

    def create(self, validated_data):
        user, _ = User.objects.get_or_create(**validated_data)
        email = validated_data.get('email')
        send_confirmation_email(email, get_confirmation_code(user))
        return user


class UserSerializer(serializers.ModelSerializer):
    """Сериализатор для модели User."""

    class Meta:
        model = User
        fields = ('username', 'email', 'first_name',
                  'last_name', 'bio', 'role')

    def validate_role(self, role):
        if not self.context['request'].user.is_admin:
            return self.instance.role

        return role


class CategorySerializer(serializers.ModelSerializer):
    """Сериализатор для модели Category."""

    class Meta:
        model = Category
        fields = '__all__'


class GenreSerializer(serializers.ModelSerializer):
    """Сериализатор для модели Genre."""

    class Meta:
        model = Genre
        fields = '__all__'


class TitleSerializer(serializers.ModelSerializer):
    """Сериализатор для модели Title."""

    genre = GenreSerializer(many=True, required=False)
    category = CategorySerializer(required=False)
    rating = serializers.IntegerField(read_only=True, required=False)

    class Meta:
        model = Title
        fields = (
            'id',
            'name',
            'year',
            'rating',
            'description',
            'genre',
            'category'
        )


class TitlePostSerializer(serializers.ModelSerializer):
    """Сериализатор для POST-запроса модели Title."""

    genre = serializers.SlugRelatedField(
        queryset=Genre.objects.all(),
        many=True,
        slug_field='slug',
    )

    category = serializers.SlugRelatedField(
        queryset=Category.objects.all(),
        slug_field='slug'
    )

    class Meta:
        model = Title
        fields = (
            'id',
            'name',
            'year',
            'description',
            'genre',
            'category'
        )

    def create(self, validated_data):
        genres = validated_data.pop('genre')
        title = Title.objects.create(**validated_data)

        for genre in genres:
            current_genre = get_object_or_404(
                Genre.objects,
                slug=genre
            )

            GenreTitle.objects.create(
                genre=current_genre, title=title)

        return title


class ReviewSerializer(serializers.ModelSerializer):
    """Сериализатор для модели Review."""

    author = serializers.SlugRelatedField(
        slug_field='username', read_only=True
    )
    title = serializers.SlugRelatedField(
        read_only=True, slug_field='id')

    class Meta:
        model = Review
        fields = ('id', 'title', 'text', 'author', 'score', 'pub_date')

    def validate(self, data):
        if self.context['request'].method == 'PATCH':
            return data
        title = self.context['view'].kwargs['title_id']
        author = self.context['request'].user
        if Review.objects.filter(author=author, title__id=title).exists():
            raise serializers.ValidationError(
                'Возможен один отзыв!')
        return data


class CommentSerializer(serializers.ModelSerializer):
    """Сериализатор для модели Comment."""

    author = serializers.SlugRelatedField(
        slug_field='username',
        read_only=True,
        validators=[UniqueValidator(queryset=Comments.objects.all())]
    )

    class Meta:
        model = Comments
        fields = ('id', 'text', 'author', 'pub_date')
