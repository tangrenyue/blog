from django.db.models import Q
from django.shortcuts import render, get_object_or_404
from django_comments.models import Comment

from blog.pagination import make_paginator, pagination_data
from . import models
import markdown, pygments


def index(request):
    entries = models.Entry.objects.all()
    page = request.GET.get('page', 1)
    entry_list, paginator = make_paginator(entries, page)
    page_data = pagination_data(paginator, page)
    return render(request, 'blog/index.html', locals())


def detail(request, blog_id):
    # entry = models.Entry.objects.get(id=blog_id)
    entry = get_object_or_404(models.Entry, id=blog_id)
    md = markdown.Markdown(extensions=[
        'markdown.extensions.extra',
        'markdown.extensions.codehilite',
        'markdown.extensions.toc',
    ])
    entry.body = md.convert(entry.body)
    entry.toc = md.toc
    entry.increase_visiting()

    comment_list = list()

    def get_comment_list(comments):
        for comment in comments:
            comment_list.append(comment)

    top_comments = Comment.objects.filter(object_pk=blog_id,
                                          content_type__app_label='blog').order_by('-submit_date')

    get_comment_list(top_comments)

    return render(request, 'blog/detail.html', locals())


def catagory(request, category_id):
    c = models.Category.objects.get(id=category_id)
    entries = models.Entry.objects.filter(category=c)
    page = request.GET.get('page', 1)
    entry_list, paginator = make_paginator(entries, page)
    page_data = pagination_data(paginator, page)

    return render(request, 'blog/index.html', locals())


def tag(request, tag_id):
    t = models.Tag.objects.get(id=tag_id)
    if t.name == "全部":
        entries = models.Entry.objects.all()
    else:
        entries = models.Entry.objects.filter(tags=t)
    page = request.GET.get('page', 1)
    entry_list, paginator = make_paginator(entries, page)
    page_data = pagination_data(paginator, page)
    return render(request, 'blog/index.html', locals())


def search(request):
    keyword = request.GET.get('keyword', None)
    if not keyword:
        error_msg = "请输入关键字"
        return render(request, 'blog/index.html', locals())
    entries = models.Entry.objects.filter(Q(title__icontains=keyword)
                                          | Q(body__icontains=keyword)
                                          | Q(abstract__icontains=keyword))
    page = request.GET.get('page', 1)
    entry_list, paginator = make_paginator(entries, page)
    page_data = pagination_data(paginator, page)
    return render(request, 'blog/index.html', locals())


def archives(request, year, month):
    entries = models.Entry.objects.filter(created_time__year=year, created_time__month=month)
    page = request.GET.get('page', 1)
    entry_list, paginator = make_paginator(entries, page)
    page_data = pagination_data(paginator, page)
    return render(request, 'blog/index.html', locals())


def permission_denied(request):
    '''403'''
    return render(request, 'blog/403.html', locals())


def page_not_found(request):
    '''404'''
    return render(request, 'blog/404.html', locals())


def page_error(request):
    '''500'''
    return render(request, 'blog/500.html', locals())
