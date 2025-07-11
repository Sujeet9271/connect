# package imports
from rest_framework.viewsets import ModelViewSet
from rest_framework.views import APIView
from rest_framework.permissions import IsAuthenticated, AllowAny
from rest_framework.response import Response
from rest_framework import status


from accounts.models import Users, ConnectionRequest
from accounts.serializers import UserSerializer, ConnectionRequestSerializer, RegisterSerializer

# Create your views here.

class RegisterView(APIView):
    permission_classes = [AllowAny]

    def post(self, request):
        serializer = RegisterSerializer(data=request.data)
        if serializer.is_valid():
            user = serializer.save()
            return Response({'user_id': user.id, 'email': user.email}, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)



class UserViewSet(ModelViewSet):
    queryset = Users.objects.none()
    serializer_class = UserSerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        return Users.objects.all().exclude(id=self.request.user.id)

class ConnectionRequestViewSet(ModelViewSet):
    serializer_class = ConnectionRequestSerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        view_type = self.request.query_params.get('type')
        if view_type == 'sent':
            return ConnectionRequest.objects.filter(from_user=self.request.user)
        elif view_type == 'received':
            return ConnectionRequest.objects.filter(to_user=self.request.user)
        return ConnectionRequest.objects.none()
