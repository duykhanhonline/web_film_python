from django.views.generic import ListView

from .models import Plan


class PlanListView(ListView):
    template_name = "billing/vip.html"
    context_object_name = "plans"
    queryset = Plan.objects.filter(is_active=True)
