from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.views.decorators.http import require_POST
from django.core.paginator import PageNotAnInteger, EmptyPage, Paginator
from django.http import JsonResponse, HttpResponse
from .forms import ImageCreateFrom
from django.contrib import messages
from .models import Image
from common.decorators import ajax_request
from action.utils import create_action
import redis


r = redis.Redis(host='192.168.233.4', port=6379, db=0, password='redis')


# Create your views here.
@login_required
def image_create(request):
    if request.method == 'POST':
        imagecreateform = ImageCreateFrom(data=request.POST)
        if imagecreateform.is_valid():
            # cd = imagecreateform.cleaned_data
            new_item = imagecreateform.save(commit=False)
            new_item.user = request.user
            new_item.save()
            messages.success(request, 'Images add success')
            create_action(request.user, 'bookmarked image', new_item)
            return redirect(new_item.get_absolute_url())
    else:
        imagecreateform = ImageCreateFrom(data=request.GET)
    url_path = 'images/image/create.html'
    dates = {'imagecreateform': imagecreateform, 'section': 'image'}
    return render(request, url_path, dates)


def image_detail(request, id, slug):
    image = get_object_or_404(Image, id=id, slug=slug)
    total_views = r.incr(f'image:{image.id}:views')
    r.zincrby('image_ranking', 1, image.id)
    html_path = 'images/image/detail.html'
    data = {'section': 'image', 'image': image, 'total_views': total_views}
    return render(request, html_path, data)


@login_required
def image_ranking(request):
    image_ranking = r.zrange('image_ranking', 0, -1, desc=True)[:10]
    print(type(image_ranking), image_ranking)
    image_ranking_ids = [int(id) for id in image_ranking]
    print(type(image_ranking_ids), image_ranking_ids)
    most_viewed = list(Image.objects.filter(id__in=image_ranking_ids))
    most_viewed.sort(key=lambda x: image_ranking_ids.index(x.id))
    html_path = 'images/image/ranking.html'
    data = {'section': 'image', 'most_viewed': most_viewed}
    return render(request, html_path, data)


@ajax_request
@login_required
@require_POST
def image_like(request):
    image_id = request.POST.get('id')
    action = request.POST.get('action')
    print(image_id, action)
    if image_id and action:
        try:
            image = Image.objects.get(id=image_id)
            print(image.users_like.count())
            # print(image)
            if action == 'like':
                image.users_like.add(request.user)
                create_action(request.user, 'like', image)
            else:
                image.users_like.remove(request.user)
            return JsonResponse({'status': 'ok'})
        except Exception:
            print('出错了')
            pass
    return JsonResponse({'status': 'error'})


@login_required
def image_list(request):
    images = Image.objects.all()
    paginator = Paginator(images, 8)
    page = request.GET.get('page')
    # print(request.GET)
    try:
        images = paginator.page(page)
    except PageNotAnInteger:
        images = paginator.page(1)
    except EmptyPage:
        if request.headers.get('x-requested-with') == 'XMLHttpRequest':
            return HttpResponse('')
        images = paginator.page(paginator.num_pages)
    ajax_images_list = 'images/image/list_ajax.html'
    ajax_datas = {'section': 'image', 'images': images}
    images_lists = 'images/image/list.html'
    datas = {'section': 'image', 'images': images}
    # 判断是否是ajax请求
    if request.headers.get('x-requested-with') == 'XMLHttpRequest':
        return render(request, ajax_images_list, ajax_datas)
    return render(request, images_lists, datas)
