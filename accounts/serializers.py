from rest_framework import serializers
from accounts.models import Users, UserDetail, ConnectionRequest


class UserDetailSerializer(serializers.ModelSerializer):
    class Meta:
        model = UserDetail
        fields = ['contact_number', 'company_name', 'address', 'industry', 'profile_pic']


class UserSerializer(serializers.ModelSerializer):
    profile = UserDetailSerializer(read_only=True)

    class Meta:
        model = Users
        fields = ['id', 'email', 'username', 'name', 'profile']

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
        fields = ['id', 'from_user', 'to_user', 'status', 'created_at']
        read_only_fields = ['id', 'from_user', 'created_at', 'status']


class SendConnectionRequestSerializer(serializers.ModelSerializer):
    class Meta:
        model = ConnectionRequest
        fields = ['to_user']

    def validate_to_user(self, to_user):
        if to_user == self.context['request'].user:
            raise serializers.ValidationError("Cannot send request to yourself.")
        return to_user

    def create(self, validated_data):
        from_user = self.context['request'].user
        return ConnectionRequest.objects.create(from_user=from_user, **validated_data)
