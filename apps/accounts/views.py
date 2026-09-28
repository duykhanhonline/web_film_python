from django.views.generic import TemplateView


class LoginView(TemplateView):
    """UI placeholder. Phone + OTP login comes in a later task."""

    template_name = "accounts/login.html"
