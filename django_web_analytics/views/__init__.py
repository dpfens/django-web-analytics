from django.views.generic.base import View, TemplateView
from django.contrib.auth.mixins import PermissionRequiredMixin, LoginRequiredMixin
from django.shortcuts import render


# Create your views here.
class DashboardView(TemplateView, PermissionRequiredMixin):
    permission_required = 'is_staff'

    template_name = "dashboard.html"

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        return context


class DataCollectionView(LoginRequiredMixin, View):

    def get(self, request):
        context = dict()
        return render(request, 'data-collection.html', context)

    def post(self, request):
        """
        DELETE requested user information
        """
        context = dict()
        return render(request, 'data-collection.html', context)
