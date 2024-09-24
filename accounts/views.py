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
import logging

# Настройка логирования
logger = logging.getLogger(__name__)

class ProfileView(TemplateView):
    template_name = 'accounts/profile.html'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        profile = get_object_or_404(Profile, user=self.request.user)
        context['profile'] = profile

        # Логируем информацию о профиле пользователя
        logger.info(f'Профиль пользователя {profile.user.username} загружен')

        # Получаем купленные книги из профиля
        context['purchased_books'] = profile.purchased_books.all()

        # Логируем информацию о купленных книгах
        logger.debug(f'Купленные книги для пользователя {profile.user.username}: {context["purchased_books"]}')

        # Получаем активную подписку через профиль
        context['active_subscription'] = profile.get_active_subscription()

        return context


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
                    logger.info(f'Пользователь {user.username} успешно авторизован')
                    return HttpResponse('Authenticated successfully')
                else:
                    logger.warning(f'Пользователь {user.username} попытался войти в отключенный аккаунт')
                    return HttpResponse('Disabled account')
            else:
                logger.error(f'Неверная попытка входа с именем пользователя: {cd["username"]}')
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
        logger.info(f'Новый пользователь {new_user.username} зарегистрирован')
        return super().form_valid(form)


class UserRegistrationDoneView(View):
    def get(self, request):
        return render(request, 'accounts/register_done.html', {'new_user': request.user})


@login_required
def edit(request, id):
    profile = get_object_or_404(Profile, user_id=id)

    if request.user.id != profile.user_id:
        logger.warning(f'Пользователь {request.user.username} попытался редактировать чужой профиль')
        return redirect('profile')

    if request.method == 'POST':
        user_form = UserEditForm(instance=profile.user, data=request.POST)
        profile_form = ProfileEditForm(instance=profile, data=request.POST, files=request.FILES)
        if user_form.is_valid() and profile_form.is_valid():
            user_form.save()
            profile_form.save()
            messages.success(request, 'Profile updated successfully')
            logger.info(f'Профиль пользователя {request.user.username} успешно обновлен')
            return redirect('profile')
        else:
            messages.error(request, 'Error updating your profile')
            logger.error(f'Ошибка при обновлении профиля пользователя {request.user.username}')
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
    logger.info('Пользователь успешно вышел')


class ProfileViewSet(viewsets.ModelViewSet):
    queryset = Profile.objects.all()
    serializer_class = ProfileSerializer
    logger.info('Загружен ViewSet для профиля')


