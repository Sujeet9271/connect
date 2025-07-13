# package imports
from rest_framework.viewsets import ModelViewSet
from rest_framework.views import APIView
from rest_framework.permissions import IsAuthenticated, AllowAny
from rest_framework.response import Response
from rest_framework import status
from rest_framework import serializers


from django.db.models import Q

from rest_framework_simplejwt.views import TokenObtainPairView, TokenRefreshView, TokenVerifyView, TokenRefreshSlidingView

from accounts.models import Users, ConnectionRequest
from accounts.serializers import SendConnectionRequestSerializer, UserDetailSerializer, UserSerializer, ConnectionRequestSerializer, RegisterSerializer


from core.logger import logger
# Create your views here.

class RegisterView(APIView):
    permission_classes = [AllowAny]

    def post(self, request):
        serializer = RegisterSerializer(data=request.data)
        if serializer.is_valid():
            user = serializer.save()
            return Response({'user_id': user.id, 'email': user.email}, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

register_view = RegisterView.as_view()

token_obtain_pair_view = TokenObtainPairView.as_view()

token_refresh = TokenRefreshView.as_view()

token_verify = TokenVerifyView.as_view()

class UserViewSet(ModelViewSet):
    queryset = Users.objects.none()
    serializer_class = UserSerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        return Users.objects.all().exclude(id=self.request.user.id)
    
    
class UserProfile(APIView):
    serializer_class = UserSerializer
    permission_classes = [IsAuthenticated]

    def get(self, request):
        profile = self.serializer_class(request.user).data
        return Response(profile, status=status.HTTP_200_OK)
    
    def patch(self, request):
        data = request.data.copy()
        profile_fields = ['contact_number', 'company_name', 'address', 'industry']

        user_data = {k: v for k, v in data.items() if k not in profile_fields}
        profile_data = {k: v for k, v in data.items() if k in profile_fields}

        if user_data:
            user_serializer = self.serializer_class(instance=request.user, data=user_data, partial=True)
            user_serializer.is_valid(raise_exception=True)
            user_serializer.save()

        if profile_data:
            detail_serializer = UserDetailSerializer(instance=request.user.profile, data=profile_data, partial=True)
            detail_serializer.is_valid(raise_exception=True)
            detail_serializer.save()

        return Response(self.serializer_class(request.user).data, status=status.HTTP_200_OK)

    
    def put(self, request):
        data = request.data.copy()
        profile_fields = ['contact_number', 'company_name', 'address', 'industry']

        user_data = {k: v for k, v in data.items() if k not in profile_fields}
        profile_data = {k: v for k, v in data.items() if k in profile_fields}

        # Full update Users
        user_serializer = self.serializer_class(instance=request.user, data=user_data)
        user_serializer.is_valid(raise_exception=True)
        user_serializer.save()

        # Full update UserDetail
        detail_serializer = UserDetailSerializer(instance=request.user.profile, data=profile_data)
        detail_serializer.is_valid(raise_exception=True)
        detail_serializer.save()

        return Response(self.serializer_class(request.user).data, status=status.HTTP_200_OK)
    
user_profile = UserProfile.as_view()


class ConnectionRequestViewSet(ModelViewSet):
    permission_classes = [IsAuthenticated]
    lookup_field = 'id'
    
    def get_queryset(self):
        view_type = self.request.query_params.get('type')
        user = self.request.user

        if view_type == 'sent':
            return ConnectionRequest.objects.filter(from_user=user, status='pending')
        elif view_type == 'received':
            return ConnectionRequest.objects.filter(to_user=user, status='pending')
        return ConnectionRequest.objects.filter(Q(from_user=user) | Q(to_user=user),)


    def get_serializer_class(self):
        if self.action == 'create':
            return SendConnectionRequestSerializer
        return ConnectionRequestSerializer


    def create(self, request, *args, **kwargs):
        # create new connection request
        serializer = SendConnectionRequestSerializer(data=request.data, context={'request': request})
        serializer.is_valid(raise_exception=True)
        connection = serializer.save()
        response_serializer = ConnectionRequestSerializer(connection, context={'request': request})
        return Response(response_serializer.data, status=status.HTTP_201_CREATED)




    def update(self, request, *args, **kwargs):
        # accept pending connection request
        update_data = {
            'status':'accepted',
        }
        instance:ConnectionRequest = ConnectionRequest.objects.filter(id=kwargs.get(self.lookup_field), to_user=request.user, status='pending').first()
        if not instance:
            return Response({"detail":"Connection Request not found"}, status=status.HTTP_404_NOT_FOUND)
        serializer = ConnectionRequestSerializer(data=update_data, instance=instance, partial=True)
        serializer.is_valid(raise_exception=True)
        self.perform_update(serializer)
        return Response(serializer.data,status=status.HTTP_200_OK)
    


    def partial_update(self, request, *args, **kwargs):
        # accept pending connection request
        update_data = {
            'status':'accept'
        }
        serializer = self.serializer_class
        instance:ConnectionRequest = ConnectionRequest.objects.filter(id=kwargs.get(self.lookup_field), to_user=request.user, status='pending').first()
        if not instance:
            return Response({"detail":"Connection Request not found"}, status=status.HTTP_404_NOT_FOUND)
        serializer = ConnectionRequestSerializer(data=update_data, instance=instance, partial=True)
        serializer.is_valid(raise_exception=True)
        self.perform_update(serializer)
        return Response(serializer.data,status=status.HTTP_200_OK)
    


    def destroy(self, request, *args, **kwargs):
        # delete connection 
        instance:ConnectionRequest = self.get_object()
        if instance.from_user != request.user and instance.to_user != request.user:
            return Response({"detail": "You've no permission for this action"}, status=status.HTTP_403_FORBIDDEN)
        instance.delete()
        return Response(status=status.HTTP_204_NO_CONTENT)
    

    


class ConnectionActions(APIView):
    permission_classes = [IsAuthenticated]

    def delete(self, request, id):
        # to delete user's pending connection
        filters = Q(id=id)
        filters.add(Q(Q(from_user=request.user)|Q(to_user=request.user)),Q.AND)
        connection = ConnectionRequest.objects.filter(filters).exclude(status='accepted').first()
        if connection:
            connection.delete()
            return Response(status=status.HTTP_204_NO_CONTENT)
        return Response(status=status.HTTP_404_NOT_FOUND)
    

    def post(self, request, id):
        # to accept/reject user's pending connection request
        connection = ConnectionRequest.objects.filter(to_user=request.user,status='pending', id=id).first()
        if connection:
            connection.delete()
            return Response(status=status.HTTP_204_NO_CONTENT)
        return Response(status=status.HTTP_404_NOT_FOUND)

connection_actions = ConnectionActions.as_view()
