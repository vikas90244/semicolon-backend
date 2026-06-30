from rest_framework_simplejwt.authentication import JWTAuthentication
from rest_framework_simplejwt.exceptions import InvalidToken, AuthenticationFailed


class JWTCookieAuthentication(JWTAuthentication):
    """
    Custom JWT authentication that reads token from cookies.
    Falls back to Authorization header if cookie not present.
    """
    
    def authenticate(self, request):
        # Try to get token from cookie first
        access_token = request.COOKIES.get('access_token')
        
        if access_token:
            # Validate the token
            try:
                validated_token = self.get_validated_token(access_token)
                return self.get_user(validated_token), validated_token
            except (InvalidToken, AuthenticationFailed) as e:
                # Token invalid, try header auth
                pass
        
        # Fall back to Authorization header
        return super().authenticate(request)
