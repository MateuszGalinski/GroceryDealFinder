from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework import status

from .serializers import (
    RegisterSerializer,
)

from rest_framework_simplejwt.tokens import RefreshToken
from rest_framework_simplejwt.authentication import JWTAuthentication

# CORE LOGIC ENDPOINTS
class ShoppingPriceCalculator(APIView):
    def post(self, request, format = None):
        return Response('shopping list')
    
class Glossary(APIView):
    authentication_classes = [JWTAuthentication]
    permission_classes = [IsAuthenticated]

    def get(self, request, format = None):
        return Response('your glossary')
    
    def put(self, request, format = None):
        return Response('glossary updated')
    
# LOGIN/REGISTER ENDPOINTS
def get_token_for_user(user):
    refresh = RefreshToken.for_user(user)
    return {
        "refresh": str(refresh),
        "access": str(refresh.access_token),
    }

class RegisterView(APIView):
    def post(self, request):
        serializer = RegisterSerializer(data=request.data)

        if serializer.is_valid():
            user = serializer.save()
            return Response({
                "message": "Registration successful.",
                "tokens": get_token_for_user(user)
            }, status=status.HTTP_201_CREATED)

        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)