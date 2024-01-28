from django.contrib.auth.models import User
from django.core import validators
from rest_framework import serializers
from rest_framework.validators import UniqueValidator

from api.models import Profile
from api.chat_service import create_chat_thread


class ProfileCreateSerializer(serializers.ModelSerializer):
    class Meta:
        model = Profile
        fields = ["phone_number", "iin", "charges", "region", "smoker",
                  "body_mass_index", "gender", "children", "age"]


class ProfileUpdateSerializer(serializers.ModelSerializer):
    class Meta:
        model = Profile
        fields = ["phone_number", "charges", "region", "smoker",
                  "body_mass_index", "gender", "children", "age"]


class ProfileSerializer(serializers.ModelSerializer):
    class Meta:
        model = Profile
        exclude = ['user', 'confirmation_token', 'chat_thread_id']


class UserCreateSerializer(serializers.ModelSerializer):
    email = serializers.EmailField(
        required=True,
        validators=[UniqueValidator(queryset=User.objects.all())]
    )
    first_name = serializers.CharField(required=True, validators=[
        validators.MinLengthValidator(limit_value=3, message="First name should be at least 3 characters long."),
    ])
    last_name = serializers.CharField(required=True, validators=[
        validators.MinLengthValidator(limit_value=3, message="Last name should be at least 3 characters long."),
    ])
    password = serializers.CharField(write_only=True, required=True)

    class Meta:
        model = User
        fields = ["username", "email", "first_name", "last_name", "password"]

    def create(self, validated_data):
        user = User.objects.create(
            username=validated_data['username'],
            email=validated_data['email'],
            first_name=validated_data['first_name'],
            last_name=validated_data['last_name'],
        )

        chat_thread_id = create_chat_thread()
        Profile.objects.create(user=user, chat_thread_id=chat_thread_id)

        user.set_password(validated_data['password'])
        user.save()

        return user


class UserUpdateSerializer(serializers.ModelSerializer):
    profile = ProfileUpdateSerializer(partial=True)
    first_name = serializers.CharField(required=True, validators=[
        validators.MinLengthValidator(limit_value=3, message="First name should be at least 3 characters long."),
    ])
    last_name = serializers.CharField(required=True, validators=[
        validators.MinLengthValidator(limit_value=3, message="Last name should be at least 3 characters long."),
    ])

    class Meta:
        model = User
        fields = ['username', 'email', 'first_name', 'last_name', 'profile']

    def validate_email(self, value):
        user_with_email = User.objects.filter(email=value).exclude(
            pk=self.instance.id if self.instance else None).first()

        if user_with_email:
            raise serializers.ValidationError('Email must be unique.')

        return value

    def update(self, instance, validated_data):
        instance.username = validated_data['username']
        instance.first_name = validated_data['first_name']
        instance.last_name = validated_data['last_name']

        profile_data = validated_data.get('profile', {})
        profile = instance.profile

        self._check_email_field_for_update(instance.email, validated_data['email'], profile)
        instance.email = validated_data['email']

        if profile_data:
            for key, value in profile_data.items():
                setattr(profile, key, value)
            profile.save()

        instance.save()
        return instance

    def to_representation(self, instance):
        representation = super().to_representation(instance)
        profile = representation.pop("profile")
        representation.update(profile)
        return representation

    def to_internal_value(self, data):
        mutable_data = data.copy()
        print("Step in 'to_internal_value'")

        profile = {
            'phone_number': mutable_data.pop('phone_number', None),
            'charges': mutable_data.pop('charges', None),
            'region': mutable_data.pop('region', None),
            'smoker': mutable_data.pop('smoker', None),
            'body_mass_index': mutable_data.pop('body_mass_index', None),
            'gender': mutable_data.pop('gender', None),
            'children': mutable_data.pop('children', None),
            'age': mutable_data.pop('age', None),
        }

        mutable_data['profile'] = profile
        return super().to_internal_value(mutable_data)

    def _check_email_field_for_update(self, email, updated_email, profile):
        if email != updated_email:
            profile.is_email_confirmed = False
            profile.save()


class UserSerializer(serializers.ModelSerializer):
    profile = ProfileSerializer()

    class Meta:
        model = User
        fields = ['username', 'email', 'first_name', 'last_name', 'profile']


class UserPasswordEditSerializer(serializers.ModelSerializer):
    old_password = serializers.CharField(write_only=True, required=True)
    new_password = serializers.CharField(write_only=True, required=True)

    class Meta:
        model = User
        fields = ["old_password", "new_password"]

    def validate_old_password(self, value):
        user: User = self.context["request"].user
        if not user.check_password(value):
            raise serializers.ValidationError(
                {"old_password": "Old password is not correct"}
            )
        return value

    def update(self, instance, validated_data):
        instance.set_password(validated_data["new_password"])
        instance.save()
        return instance

