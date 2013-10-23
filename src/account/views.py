from django.contrib.auth.decorators import login_required
from django.shortcuts import render, redirect
from django.utils.decorators import method_decorator
from django.views.generic.base import TemplateView, View
from account import forms

class ProfileView(TemplateView):
    template_name = 'account/profile.html'

    @method_decorator(login_required)
    def dispatch(self, *args, **kwargs):
        return super(ProfileView, self).dispatch(*args, **kwargs)

    def get_context_data(self, **kwargs):
        context = super(ProfileView, self).get_context_data(**kwargs)
        return context

class UpdateView(View):
    template_name = 'account/update.html'

    @method_decorator(login_required)
    def dispatch(self, *args, **kwargs):
        return super(UpdateView, self).dispatch(*args, **kwargs)

    def get(self, request):
        initial = {
            'email': request.user.email
        }
        form = forms.UpdateUserForm(initial=initial)
        form.user = request.user

        context = {'form': form}
        return render(request, self.template_name, context)

    def post(self, request):
        form = forms.UpdateUserForm(request.POST)
        form.user = request.user
        context = {}

        if not form.is_valid():
            context['form'] = form
            return render(request, self.template_name, context)

        form.save()
        return redirect('/account/profile')
