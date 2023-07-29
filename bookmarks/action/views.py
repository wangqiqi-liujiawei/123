# from django.shortcuts import render
# from django.contrib.auth.decorators import login_required
# from django.http import HttpResponse
# from django.core.paginator import PageNotAnInteger, EmptyPage, Paginator
# from action.models import Action


# # Create your views here.
# @login_required
# def action_list(request):
#     action = Action.objects.exclude(user=request.user)
#     follow_ids = request.user.following.values_list('id', flat=True)
#     if follow_ids:
#         action = action.filter(user_id__in=follow_ids)
#     actions = action.select_related('user', 'user__profile').prefetch_related('target')[:10]
#     paginator = Paginator(actions, 4)
#     page = request.GET.get('page')
#     try:
#         actions = paginator.page(page)
#     except PageNotAnInteger:
#         actions = paginator.page(1)
#     except EmptyPage:
#         if request.headers.get('x-request-with') == 'XMLHttpRequest':
#             return HttpResponse('')
#         actions = paginator.page(paginator.num_pages)
#     ajax_actions_list = 'action/detail.html'
#     ajax_actions_datas = {'section': 'dashboard', 'actions': actions}
#     actions_list = 'action/list.html'
#     actions_datas = {'section': 'dashboard', 'actions': actions}
#     if request.headers.get('x-request-with') == 'XMLHttpRequest':
#         return render(request, ajax_actions_list, ajax_actions_datas)
#     return render(request, actions_list, actions_datas)
