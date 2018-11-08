from django_countries.serializers import CountryFieldMixin
from django_countries.serializer_fields import CountryField
from rest_framework import serializers
from users.models import CustomUser


class UserSerializer(CountryFieldMixin, serializers.ModelSerializer):
    country = CountryField(country_dict=True)
    class Meta:
        model = CustomUser
        fields = (
            'url',
            'id',
            'email',
            'first_name',
            'last_name',
            'country',
        )
