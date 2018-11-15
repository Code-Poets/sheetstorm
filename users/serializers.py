from django_countries.serializers import CountryFieldMixin
from django_countries.serializer_fields import CountryField
from rest_framework import serializers
from users.models import CustomUser



class UserSerializer(CountryFieldMixin, serializers.ModelSerializer):
    class Meta:
        model = CustomUser
        fields = '__all__'


class UserListSerializer(UserSerializer):
    url = serializers.HyperlinkedIdentityField(
            view_name="users-detail",
    )
    class Meta:
        model = CustomUser
        fields = (
            'url',
            'email',
            'first_name',
            'last_name',
        )


class UserDetailSerializer(UserSerializer):
    class Meta:
        model = CustomUser
        fields = (
            'email',
            'first_name',
            'last_name',
            'date_of_birth',
            'phone_number',
            'country',
            'user_type',
        )


class UserUpdateSerializer(UserSerializer):
    class Meta:
        model = CustomUser
        fields = (
            'first_name',
            'last_name',
            'date_of_birth',
            'phone_number',
            'country',
        )


class UserCreateSerializer(UserSerializer):
    class Meta:
        model = CustomUser
        fields = (
            'email',
            'first_name',
            'last_name',
            'date_of_birth',
            'phone_number',
            'country',
            'user_type',
            'is_staff',
            'is_superuser',
            'is_active',
        )
