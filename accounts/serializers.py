from rest_framework import serializers

from django.db.models import Q

from accounts.models import Users, UserDetail, ConnectionRequest

from core.logger import logger


class UserProfileSerializer(serializers.ModelSerializer):
    class Meta:
        model = UserDetail
        fields = ['contact_number', 'company_name', 'address', 'industry', 'profile_pic']


class UserDetailSerializer(serializers.ModelSerializer):
    profile = UserProfileSerializer(read_only=True)

    class Meta:
        model = Users
        fields = ['id', 'email', 'username', 'name', 'profile']

    def to_representation(self, instance):
        data = super().to_representation(instance)
        logger.debug(f'{data=}')
        profile_detail = data.pop('profile',{})
        logger.debug(f'{profile_detail=}')
        if profile_detail:
            data.update(profile_detail)
        return data

class UserSerializer(serializers.ModelSerializer):
    class Meta:
        model = Users
        fields = [
            'id', 'username', 'email', 'name',
        ]

class UserListSerializer(serializers.ModelSerializer):
    is_connected = serializers.BooleanField()

    class Meta:
        model = Users
        fields = [
            'id', 'username', 'email', 'name', 'is_connected',
        ]



class RegisterSerializer(serializers.ModelSerializer):
    contact_number = serializers.CharField(write_only=True)
    company_name = serializers.CharField(write_only=True)
    address = serializers.CharField(write_only=True)
    industry = serializers.CharField(write_only=True)
    password = serializers.CharField(write_only=True)

    class Meta:
        model = Users
        fields = ['email', 'username', 'name', 'password', 'contact_number', 'company_name', 'address', 'industry']

    def create(self, validated_data):
        profile_fields = {key: validated_data.pop(key) for key in ['contact_number', 'company_name', 'address', 'industry']}
        user = Users.objects.create_user(**validated_data)
        UserDetail.objects.create(user=user, **profile_fields)
        return user


class ConnectionRequestSerializer(serializers.ModelSerializer):
    from_user = UserSerializer(read_only=True)
    to_user = UserSerializer(read_only=True)

    class Meta:
        model = ConnectionRequest
        fields = ['id', 'from_user', 'to_user', 'status', 'created_at', 'updated_at']
        read_only_fields = ['id', 'from_user', 'to_user', 'created_at', 'updated_at']


class ConnectionRequestReceived(serializers.ModelSerializer):
    from_user = UserSerializer(read_only=True)

    class Meta:
        model = ConnectionRequest
        fields = ['id', 'from_user', 'status', 'created_at', 'updated_at']
        read_only_fields = ['id', 'from_user', 'created_at', 'updated_at']


class ConnectionRequestSent(serializers.ModelSerializer):
    to_user = UserSerializer(read_only=True)

    class Meta:
        model = ConnectionRequest
        fields = ['id', 'to_user', 'status', 'created_at', 'updated_at']
        read_only_fields = ['id', 'to_user', 'status', 'created_at', 'updated_at']



class SendConnectionRequestSerializer(serializers.ModelSerializer):
    class Meta:
        model = ConnectionRequest
        fields = ['to_user']

    def validate_to_user(self, to_user):
        from_user = self.context['request'].user

        if from_user == to_user:
            raise serializers.ValidationError("Cannot send request to yourself.")

        # check for existing request or connection between the sender and receiver
        if ConnectionRequest.objects.filter(
            Q(from_user=from_user, to_user=to_user) |
            Q(from_user=to_user, to_user=from_user)
        ).exists():
            raise serializers.ValidationError("A connection request already exists or you are already connected.")
        return to_user

    def create(self, validated_data):
        from_user = self.context['request'].user
        return ConnectionRequest.objects.create(from_user=from_user, **validated_data)

