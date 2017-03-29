from registration.forms import RegistrationForm

from heartext.models import User


class CustomUserForm(RegistrationForm):
    class Meta:
        model = User
        fields = ("username", "email", "password1", "password2")
