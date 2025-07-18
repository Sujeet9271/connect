from rest_framework import serializers

from django.db.models import Q

from accounts.models import Users, UserDetail, ConnectionRequest

from core.logger import logger


class UserProfileSerializer(serializers.ModelSerializer):
    class Meta:
        model = UserDetail
        fields = ['contact_number', 'company_name', 'address', 'industry',]


class UserDetailSerializer(serializers.ModelSerializer):
    profile = UserProfileSerializer(read_only=True)
    is_connected = serializers.SerializerMethodField()

    class Meta:
        model = Users
        fields = ['id', 'user_id', 'email', 'username', 'name', 'profile_pic', 'is_connected', 'profile']


    def get_is_connected(self, obj):
        return getattr(obj, 'is_connected', False)


class UserSerializer(serializers.ModelSerializer):
    class Meta:
        model = Users
        fields = [
            'id', 'user_id', 'username', 'email', 'name', 'profile_pic'
        ]

class UserListSerializer(serializers.ModelSerializer):
    is_connected = serializers.BooleanField()

    class Meta:
        model = Users
        fields = [
            'id', 'user_id', 'username', 'email', 'name', 'is_connected', 'profile_pic'
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


    def validate_status(self, status):
        if status=='pending':
            raise serializers.ValidationError("The status value should be either 'accepted' or 'rejected' ")
        return status
    
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
        # if ConnectionRequest.objects.filter(
        #     Q(from_user=from_user, to_user=to_user) |
        #     Q(from_user=to_user, to_user=from_user)
        # ).exclude(status='rejected').exists():
        #     raise serializers.ValidationError("A connection request already exists or you are already connected.")

        existing_request = ConnectionRequest.objects.filter(
                                    Q(from_user=from_user, to_user=to_user) | Q(from_user=to_user, to_user=from_user),
                                    status__in=['pending', 'accepted']
                                ).exists()

        if existing_request:
            raise serializers.ValidationError("A connection already exists or is pending between these users.")
        return to_user

    def create(self, validated_data):
        from_user = self.context['request'].user
        return ConnectionRequest.objects.create(from_user=from_user, **validated_data)

