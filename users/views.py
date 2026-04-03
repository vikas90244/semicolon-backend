from allauth.socialaccount.providers.google.views import GoogleOAuth2Adapter
from dj_rest_auth.registration.views import SocialLoginView

import traceback

class GoogleLoginView(SocialLoginView):
    authentication_classes = []
    adapter_class = GoogleOAuth2Adapter

    def post(self, request, *args, **kwargs):
        try:
            print("Incoming data:", request.data)
            return super().post(request, *args, **kwargs)
        except Exception as e:
            print("FULL ERROR:")
            traceback.print_exc()
            raise e