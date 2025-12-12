from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework import status

from .serializers import (
    RegisterSerializer,
    GlossarySerializer,
    ProductSerializer
)

from .models import (
    Product,
    Glossary
)

from rest_framework_simplejwt.tokens import RefreshToken
from rest_framework_simplejwt.authentication import JWTAuthentication

# CORE LOGIC ENDPOINTS
class ShoppingPriceCalculator(APIView):
    def post(self, request, format = None):
        return Response('shopping list')
    
class GlossaryView(APIView):
    authentication_classes = [JWTAuthentication]
    permission_classes = [IsAuthenticated]

    def get(self, request, format=None):
        try:
            glossary = Glossary.objects.get(user=request.user)
            serializer = GlossarySerializer(glossary)
            return Response(serializer.data)
        except Glossary.DoesNotExist:
            return Response(
                {'translations': {}},
                status=status.HTTP_200_OK
            )

    def put(self, request, format=None):
        try:
            glossary = Glossary.objects.get(user=request.user)
            serializer = GlossarySerializer(glossary, data=request.data, partial=True)
        except Glossary.DoesNotExist:
            serializer = GlossarySerializer(data=request.data)

        if serializer.is_valid():
            serializer.save(user=request.user)
            return Response(serializer.data)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
    
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