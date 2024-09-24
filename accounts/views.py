from django.contrib.auth.decorators import login_required
from django.http import HttpResponse
from django.shortcuts import render, get_object_or_404, redirect
from django.contrib.auth import authenticate, login
from django.views import View
from django.views.generic import TemplateView
from django.views.generic.edit import FormView
from django.contrib import messages
from .forms import LoginForm, UserRegistrationForm, UserEditForm, ProfileEditForm
from .models import Profile
from django.contrib.auth.views import LogoutView
from django.urls import reverse_lazy
from subscriptions.models import BookPurchase
from rest_framework import viewsets
from .serializers import ProfileSerializer
from subscriptions.models import Subscription, BookPurchase
from django.utils import timezone


@login_required
def profile_view(request):
    user = request.user
    purchased_books = BookPurchase.objects.filter(user=user)

    # Обработка получения активной подписки
    active_subscription = getattr(user, 'subscription', None)
    if active_subscription and not active_subscription.is_active:
        active_subscription = None  # Если подписка не активна, установите значение в None

    context = {
        'user': user,
        'purchased_books': purchased_books,
        'active_subscription': active_subscription,
    }
    return render(request, 'accounts/profile.html', context)

class UserLoginView(View):
    def get(self, request):
        form = LoginForm()
        return render(request, 'accounts/login.html', {'form': form})

    def post(self, request):
        form = LoginForm(request.POST)
        if form.is_valid():
            cd = form.cleaned_data
            user = authenticate(request, username=cd['username'], password=cd['password'])
            if user is not None:
                if user.is_active:
                    login(request, user)
                    return HttpResponse('Authenticated successfully')
                else:
                    return HttpResponse('Disabled account')
            else:
                return HttpResponse('Invalid login')
        return render(request, 'accounts/login.html', {'form': form})


class UserRegistrationView(FormView):
    template_name = 'accounts/register.html'
    form_class = UserRegistrationForm
    success_url = reverse_lazy('register_done')

    def form_valid(self, form):
        new_user = form.save(commit=False)
        new_user.set_password(form.cleaned_data['password'])
        new_user.save()
        Profile.objects.create(user=new_user)
        return super().form_valid(form)


class UserRegistrationDoneView(View):
    def get(self, request):
        return render(request, 'accounts/register_done.html', {'new_user': request.user})


@login_required
def edit(request, id):
    profile = get_object_or_404(Profile, user_id=id)

    if request.user.id != profile.user_id:
        return redirect('profile')

    if request.method == 'POST':
        user_form = UserEditForm(instance=profile.user, data=request.POST)
        profile_form = ProfileEditForm(instance=profile, data=request.POST, files=request.FILES)
        if user_form.is_valid() and profile_form.is_valid():
            user_form.save()
            profile_form.save()
            messages.success(request, 'Profile updated successfully')
            return redirect('profile')
        else:
            messages.error(request, 'Error updating your profile')
    else:
        user_form = UserEditForm(instance=profile.user)
        profile_form = ProfileEditForm(instance=profile)

    return render(request, 'accounts/edit.html', {
        'user_form': user_form,
        'profile_form': profile_form,
        'profile': profile
    })


# Это использует стандартный LogoutView, но вы можете указать свой шаблон для страницы выхода
class UserLogoutView(LogoutView):
    template_name = 'logged_out.html'
    next_page = reverse_lazy('books:home')  # Куда перенаправлять после выхода


class ProfileViewSet(viewsets.ModelViewSet):
    queryset = Profile.objects.all()
    serializer_class = ProfileSerializer
