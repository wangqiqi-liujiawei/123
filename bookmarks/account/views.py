from django.shortcuts import render, get_object_or_404
from django.http import HttpResponse
from .forms import LoginForm, UserRegistrationFrom, UserEditForm, ProfileEditForm
from django.contrib.auth import authenticate, login
from django.contrib.auth.models import User
from django.contrib.auth.decorators import login_required
from .models import Profile, Contact
from django.http import JsonResponse
from django.contrib import messages
from common.decorators import ajax_request
from django.views.decorators.http import require_POST
from action.utils import create_action
from action.models import Action
from django.core.paginator import PageNotAnInteger, EmptyPage, Paginator
# from django.http import HttpResponse


# Create your views here.
@login_required
def dashboard(request):
    action = Action.objects.exclude(user=request.user)
    follow_ids = request.user.following.values_list('id', flat=True)
    if follow_ids:
        action = action.filter(user_id__in=follow_ids)
    actions = action.select_related('user', 'user__profile').prefetch_related('target')[:10]
    # print(actions)
    return render(request, 'account/dashboard.html', {'section': 'dashboard', 'actions': actions})


@login_required
def action_list(request):
    action = Action.objects.exclude(user=request.user)
    follow_ids = request.user.following.values_list('id', flat=True)
    if follow_ids:
        action = action.filter(user_id__in=follow_ids)
    actions = action.select_related('user', 'user__profile').prefetch_related('target')[:10]
    paginator = Paginator(actions, 4)
    page = request.GET.get('page')
    try:
        actions = paginator.page(page)
    except PageNotAnInteger:
        actions = paginator.page(1)
    except EmptyPage:
        if request.headers.get('x-request-with') == 'XMLHttpRequest':
            return HttpResponse('')
        actions = paginator.page(paginator.num_pages)
    ajax_actions_list = 'action/detail.html'
    ajax_actions_datas = {'section': 'dashboard', 'actions': actions}
    actions_list = 'action/list.html'
    actions_datas = {'section': 'dashboard', 'actions': actions}
    if request.headers.get('x-request-with') == 'XMLHttpRequest':
        print(ajax_actions_datas)
        return render(request, ajax_actions_list, ajax_actions_datas)
    return render(request, actions_list, actions_datas)


def registers(request):
    if request.method == 'POST':
        user_form = UserRegistrationFrom(request.POST)
        if user_form.is_valid():
            new_user = user_form.save(commit=False)
            new_user.set_password(user_form.cleaned_data['password'])
            new_user.save()
            Profile.objects.create(user=new_user)
            create_action(new_user, 'has created an account')
            return render(request, 'account/register_done.html', {'new_user': new_user})
    else:
        user_form = UserRegistrationFrom()
    return render(request, 'account/registers.html', {'user_form': user_form})


@login_required
def edit(request):
    if request.method == 'POST':
        user_form = UserEditForm(instance=request.user, data=request.POST)
        profile_form = ProfileEditForm(instance=request.user, data=request.POST, files=request.FILES)
        if user_form.is_valid() and profile_form.is_valid():
            user_form.save()
            profile_form.save()
            # create_action(request.user, '修改用户信息')
            messages.success(request, 'Profiles updated successfully')
        else:
            messages.error(request, 'Error updateing your profile')

    else:
        user_form = UserEditForm(instance=request.user)
        profile_form = ProfileEditForm(instance=request.user, files=request.FILES)
    return render(request, 'account/edit.html', {'user_form': user_form, 'profile_form': profile_form})


def user_login(request):
    if request.method == 'POST':
        form = LoginForm(request.POST)
        if form.is_valid():
            cd = form.cleaned_data
            user = authenticate(request,
                                username=cd['user_name'],
                                password=cd['password'])
            print('**********************************************************************')
            print(request.user.is_authenticated)
            if user is not None:
                if user.is_active:
                    login(request, user)
                    return HttpResponse('Authenticated successfully')
                else:
                    return HttpResponse('Disable account')
            else:
                return HttpResponse('Invalid login')
    else:
        form = LoginForm()
    return render(request, 'account/login.html', {'form': form})


@login_required
def user_list(request):
    users = User.objects.filter(is_active=True)
    url_path = 'account/user/list.html'
    datas = {'section': 'people', 'users': users}
    # create_action(request.user, '进入用户列表')
    return render(request, url_path, datas)


@login_required
def user_detail(request, username):
    # print(username)
    users = get_object_or_404(User, username=username, is_active=True)
    url_path = 'account/user/detail.html'
    datas = {'section': 'people', 'user': users}
    # print(users.images_created.all())
    # print(users.get_full_name)
    # create_action(request.user, '进入', username, '用户信息页面')
    return render(request, url_path, datas)


@ajax_request
@require_POST
@login_required
def user_follow(request):
    user_id = request.POST.get('id')
    actions = request.POST.get('actions')
    print(user_id, actions)
    if user_id and actions:
        try:
            user = User.objects.get(id=user_id)
            if actions == 'follow':
                Contact.objects.get_or_create(user_from=request.user, user_to=user)
                create_action(request.user, 'is following', user)
            else:
                Contact.objects.filter(user_from=request.user, user_to=user).delete()
            return JsonResponse({'status': 'ok'})
        except User.DoesNotExist:
            return JsonResponse({'status': 'error'})
    return JsonResponse({'status': 'error'})
