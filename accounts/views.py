# package imports
from rest_framework.viewsets import ModelViewSet, ReadOnlyModelViewSet
from rest_framework.views import APIView
from rest_framework.permissions import IsAuthenticated, AllowAny
from rest_framework.response import Response
from rest_framework import status

from django.utils.http import urlsafe_base64_decode

from django.db.models import Q, QuerySet, OuterRef, Exists

from rest_framework_simplejwt.views import TokenObtainPairView, TokenRefreshView, TokenVerifyView, TokenRefreshSlidingView

from accounts.models import Users, ConnectionRequest
from accounts.serializers import ConnectionRequestReceived, ConnectionRequestSent, SendConnectionRequestSerializer, UserDetailSerializer, UserListSerializer, UserProfileSerializer, UserSerializer, ConnectionRequestSerializer, RegisterSerializer


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
    

class ActivateUser(APIView):

    def get(self, request, *args, **kwargs):
        logger.debug(f'{args=},{kwargs=}')
        user = self.get_user(kwargs['uidb64'])
        if user:
            user.is_active = True
            user.save()
            return Response({"detail":"Your Account is active"}, status=status.HTTP_200_OK)
        return Response({"detail":"No User Found"}, status=status.HTTP_400_BAD_REQUEST)
    

    def get_user(self, uidb64):
        try:
            # urlsafe_base64_decode() decodes to bytestring
            uid = urlsafe_base64_decode(uidb64).decode()
            pk = Users._meta.pk.to_python(uid)
            user = Users._default_manager.get(pk=pk)
        except (
            TypeError,
            ValueError,
            OverflowError,
            Users.DoesNotExist,
        ):
            user = None
        return user



register_view = RegisterView.as_view()

activate_user = ActivateUser.as_view()

token_obtain_pair_view = TokenObtainPairView.as_view()

token_refresh = TokenRefreshView.as_view()

token_verify = TokenVerifyView.as_view()


class UserViewSet(ReadOnlyModelViewSet):
    queryset = Users.objects.none()
    serializer_class = UserListSerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        user = self.request.user

        accepted_connections = ConnectionRequest.objects.filter(
            status='accepted',
        ).filter(
            Q(from_user=user, to_user=OuterRef('pk')) |
            Q(from_user=OuterRef('pk'), to_user=user)
        )

        return Users.objects.exclude(id=user.id).annotate(
            is_connected=Exists(accepted_connections)
        )
    
    def retrieve(self, request, *args, **kwargs):
        self.serializer_class = UserDetailSerializer
        return super().retrieve(request, *args, **kwargs)
    
    
    
class UserProfile(APIView):
    serializer_class = UserDetailSerializer
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
            user_serializer = UserSerializer(instance=request.user, data=user_data, partial=True)
            user_serializer.is_valid(raise_exception=True)
            user_serializer.save()

        if profile_data:
            profile_serializer = UserProfileSerializer(instance=request.user.profile, data=profile_data, partial=True)
            profile_serializer.is_valid(raise_exception=True)
            profile_serializer.save()

        return Response(self.serializer_class(request.user).data, status=status.HTTP_200_OK)

    
    def put(self, request):
        data = request.data.copy()
        profile_fields = ['contact_number', 'company_name', 'address', 'industry']

        user_data = {k: v for k, v in data.items() if k not in profile_fields}
        profile_data = {k: v for k, v in data.items() if k in profile_fields}

        # Full update Users
        user_serializer = UserSerializer(instance=request.user, data=user_data)
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
    
    def get_queryset(self)->QuerySet[ConnectionRequest]:
        view_type = self.request.query_params.get('type')
        user = self.request.user
        if view_type == 'sent':
            return self.request.user.sent_requests.filter(status='pending')
        elif view_type == 'received':
            return self.request.user.received_requests.filter(status='pending')
        return ConnectionRequest.objects.select_related('from_user', 'to_user').filter(Q(from_user=user) | Q(to_user=user),)

    def list(self, request, *args, **kwargs):
        view_type = self.request.query_params.get('type')
        queryset = self.get_queryset()
        if view_type == 'sent':
            # queryset = self.request.user.sent_requests.filter(status='pending')
            serializer = ConnectionRequestSent(queryset, many=True)
        elif view_type == 'received':
            # queryset = self.request.user.received_requests.filter(status='pending')
            serializer = ConnectionRequestReceived(queryset, many=True)
        else:
            # queryset = ConnectionRequest.objects.select_related('from_user', 'to_user').filter(Q(from_user=user) | Q(to_user=user),)
            serializer = ConnectionRequestSerializer(queryset, many=True)
        return Response(serializer.data, status=status.HTTP_200_OK)
        

    def create(self, request, *args, **kwargs):
        # create new connection request
        serializer = SendConnectionRequestSerializer(data=request.data, context={'request': request})
        serializer.is_valid(raise_exception=True)
        connection = serializer.save()
        response_serializer = ConnectionRequestSent(connection, context={'request': request})
        return Response(response_serializer.data, status=status.HTTP_201_CREATED)




    def update(self, request, *args, **kwargs):
        # accept pending connection request
        update_data = {
            'status':'accepted',
        }
        instance:ConnectionRequest = ConnectionRequest.objects.filter(id=kwargs.get(self.lookup_field), to_user=request.user, status='pending').first()
        if not instance:
            return Response({"detail":"Connection Request not found"}, status=status.HTTP_404_NOT_FOUND)
        serializer = ConnectionRequestReceived(data=update_data, instance=instance, partial=True)
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
        serializer = ConnectionRequestReceived(data=update_data, instance=instance, partial=True)
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
