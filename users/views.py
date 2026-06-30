from rest_framework import status
from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import AllowAny, IsAuthenticated
from rest_framework.response import Response
from rest_framework_simplejwt.tokens import RefreshToken
from django.contrib.auth import authenticate
from django.conf import settings
from .serializers import SemicolonUserModelSerializer, UserRegistrationSerializer
from .models import SemicolonUserModel
import uuid


def set_auth_cookies(response, access_token, refresh_token):
    """Helper to set JWT tokens as HTTP-only cookies"""
    is_production = not settings.DEBUG
    
    # For cross-origin cookies (frontend on different domain), we need SameSite=None
    # But SameSite=None requires Secure=True (HTTPS only)
    samesite = 'None' if is_production else 'Lax'
    
    response.set_cookie(
        key='access_token',
        value=access_token,
        httponly=True,
        secure=is_production,  # Only sent over HTTPS in production
        samesite=samesite,
        max_age=3600,  # 1 hour
        path='/',
    )
    
    response.set_cookie(
        key='refresh_token',
        value=refresh_token,
        httponly=True,
        secure=is_production,  # Only sent over HTTPS in production
        samesite=samesite,
        max_age=604800,  # 7 days
        path='/',
    )


@api_view(['POST'])
@permission_classes([AllowAny])
def register(request):
    """
    Register a new user.
    POST /api/auth/register/
    Body: { "email": "user@example.com", "password": "password123", "username": "optional" }
    """
    serializer = UserRegistrationSerializer(data=request.data)
    
    if serializer.is_valid():
        user = serializer.save()
        
        # Generate JWT tokens
        refresh = RefreshToken.for_user(user)
        
        response = Response({
            "success": True,
            "message": "User created successfully",
            "data": {
                "user": SemicolonUserModelSerializer(user).data,
            }
        }, status=status.HTTP_201_CREATED)
        
        # Set tokens as HTTP-only cookies
        set_auth_cookies(response, str(refresh.access_token), str(refresh))
        
        return response
    
    return Response({
        "success": False,
        "error": {
            "message": "Validation failed",
            "code": "VALIDATION_ERROR",
            "status": 400,
            "details": serializer.errors
        }
    }, status=status.HTTP_400_BAD_REQUEST)


@api_view(['POST'])
@permission_classes([AllowAny])
def login(request):
    """
    Login user and return JWT tokens as cookies.
    POST /api/auth/login/
    Body: { "email": "user@example.com", "password": "password123" }
    """
    email = request.data.get('email')
    password = request.data.get('password')
    
    if not email or not password:
        return Response({
            "success": False,
            "error": {
                "message": "Email and password are required",
                "code": "VALIDATION_ERROR",
                "status": 400
            }
        }, status=status.HTTP_400_BAD_REQUEST)
    
    # Authenticate user
    user = authenticate(request, username=email, password=password)
    
    if user is not None:
        # Generate JWT tokens
        refresh = RefreshToken.for_user(user)
        
        response = Response({
            "success": True,
            "message": "Login successful",
            "data": {
                "user": SemicolonUserModelSerializer(user).data,
            }
        }, status=status.HTTP_200_OK)
        
        # Set tokens as HTTP-only cookies
        set_auth_cookies(response, str(refresh.access_token), str(refresh))
        
        return response
    
    return Response({
        "success": False,
        "error": {
            "message": "Invalid email or password",
            "code": "UNAUTHORIZED",
            "status": 401
        }
    }, status=status.HTTP_401_UNAUTHORIZED)


@api_view(['POST'])
@permission_classes([AllowAny])
def refresh_token(request):
    """
    Refresh access token using refresh token from cookie.
    POST /api/auth/refresh/
    """
    refresh_token = request.COOKIES.get('refresh_token')
    
    if not refresh_token:
        return Response({
            "success": False,
            "error": {
                "message": "Refresh token not found",
                "code": "UNAUTHORIZED",
                "status": 401
            }
        }, status=status.HTTP_401_UNAUTHORIZED)
    
    try:
        refresh = RefreshToken(refresh_token)
        
        response = Response({
            "success": True,
            "message": "Token refreshed successfully",
            "data": {}
        }, status=status.HTTP_200_OK)
        
        is_production = not settings.DEBUG
        samesite = 'None' if is_production else 'Lax'
        
        # Set new access token
        response.set_cookie(
            key='access_token',
            value=str(refresh.access_token),
            httponly=True,
            secure=is_production,
            samesite=samesite,
            max_age=3600,
            path='/',
        )
        
        return response
    except Exception as e:
        return Response({
            "success": False,
            "error": {
                "message": "Invalid or expired refresh token",
                "code": "UNAUTHORIZED",
                "status": 401
            }
        }, status=status.HTTP_401_UNAUTHORIZED)


@api_view(['GET'])
@permission_classes([IsAuthenticated])
def get_user(request):
    """
    Get current authenticated user.
    GET /api/auth/user/
    """
    serializer = SemicolonUserModelSerializer(request.user)
    return Response({
        "success": True,
        "data": serializer.data
    }, status=status.HTTP_200_OK)


@api_view(['POST'])
@permission_classes([AllowAny])
def logout(request):
    """
    Logout user by clearing cookies.
    POST /api/auth/logout/
    """
    response = Response({
        "success": True,
        "message": "Logged out successfully"
    }, status=status.HTTP_200_OK)
    
    is_production = not settings.DEBUG
    samesite = 'None' if is_production else 'Lax'
    
    # Clear cookies with same settings they were set with
    response.delete_cookie('access_token', path='/', samesite=samesite)
    response.delete_cookie('refresh_token', path='/', samesite=samesite)
    
    return response


@api_view(['POST'])
@permission_classes([AllowAny])
def guest_login(request):
    """
    Login as demo/guest user.
    POST /api/users/guest-login/
    
    Uses a shared demo account for quick testing without registration.
    Email: demo@semicolon.app
    Password: demo123456
    """
    demo_email = "demo@semicolon.app"
    demo_password = "demo123456"
    
    try:
        # Try to get existing demo user
        try:
            user = SemicolonUserModel.objects.get(email=demo_email)
        except SemicolonUserModel.DoesNotExist:
            # Create demo user if it doesn't exist
            user = SemicolonUserModel.objects.create_user(
                email=demo_email,
                username="demo_user",
                password=demo_password
            )
        
        # Generate JWT tokens
        refresh = RefreshToken.for_user(user)
        
        response = Response({
            "success": True,
            "message": "Logged in as demo user",
            "data": {
                "user": SemicolonUserModelSerializer(user).data,
                "is_guest": True,
                "note": "Demo account is shared. Data may be deleted periodically."
            }
        }, status=status.HTTP_200_OK)
        
        # Set tokens as HTTP-only cookies
        set_auth_cookies(response, str(refresh.access_token), str(refresh))
        
        return response
        
    except Exception as e:
        print(f"Guest login error: {e}")
        return Response({
            "success": False,
            "error": {
                "message": "Failed to login as demo user",
                "code": "INTERNAL_ERROR",
                "status": 500
            }
        }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
