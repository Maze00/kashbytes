from django.contrib.auth.backends import ModelBackend
from django.contrib.auth import get_user_model

User = get_user_model()


class CustomAuthenticate(ModelBackend):

    def authenticate(self, request, user=None, password=None, *args, **kwargs):
        try:
            try:
                user = User.objects.get(username=user)
            except:
                user = User.objects.get(email=user)
        except User.DoesNotExist:
            return None
        else:
            if user.check_password(password):
                return user
        return None
