from django.shortcuts import render, get_object_or_404
from django_shop.decorators import non_superuser_required
from django.views.decorators.csrf import csrf_exempt
from django.core.paginator import Paginator
from django.http import JsonResponse
from django.utils import timezone
from django.db.models import Avg
from .models import Blog, Rate, Comment


@non_superuser_required
def blog_list(request):
    blog_list = Blog.objects.all().order_by("created_at")
    # 3 bai trong 1 page
    paginator = Paginator(blog_list, 3)
    # Lay so page tu url
    page_number = request.GET.get("page")
    page_obj = paginator.get_page(page_number)
    return render(
        request, "blog/blog.html", {"page_obj": page_obj, "paginator": paginator}
    )


@non_superuser_required
def blog_detail(request, pk):
    blog = get_object_or_404(Blog, pk=pk)
    next_blog = Blog.objects.filter(id__gt=blog.id).order_by("id").first()
    prev_blog = Blog.objects.filter(id__lt=blog.id).order_by("-id").first()
    # tinh diem trung binh
    avg_rate = (
        Rate.objects.filter(id_blog=blog).aggregate(Avg("rate"))["rate__avg"] or 0
    )
    # lay rate cua user hien tai de hien thi (neu co)
    user_rate = 0
    if request.user.is_authenticated:
        rate_obj = Rate.objects.filter(id_blog=blog, id_user=request.user).first()
        if rate_obj:
            user_rate = rate_obj.rate
    # Lay comment trong data de hien thi
    comments = Comment.objects.filter(id_blog=blog).order_by("created_at")

    context = {
        "blog": blog,
        "next_blog": next_blog,
        "prev_blog": prev_blog,
        "avg_rate": round(avg_rate, 1),
        "user_rate": user_rate,
        "comments": comments,
    }
    return render(request, "blog/blog-detail.html", context)


@csrf_exempt
def blog_rate(request):
    # neu chua login thi yeu cau login
    if not request.user.is_authenticated:
        return JsonResponse({"login_required": True})
    if request.method == "POST":
        rate = request.POST.get("rate")
        id_blog = request.POST.get("id_blog")
        try:
            blog = Blog.objects.get(id=id_blog)
            Rate.objects.filter(id_blog=blog, id_user=request.user).delete()
            Rate.objects.create(id_blog=blog, id_user=request.user, rate=rate)
            # tinh trung binh
            avg_rate = (
                Rate.objects.filter(id_blog=blog).aggregate(Avg("rate"))["rate__avg"]
                or 0
            )
            return JsonResponse(
                {"success": True, "avg_rate": round(avg_rate, 1), "user_rate": rate}
            )
        except Blog.DoesNotExist:
            return JsonResponse({"success": False, "error": "Blog not found"})
    return JsonResponse({"success": False, "error": "Invalid request"})


# @csrf_exempt
@non_superuser_required
def blog_cmt(request):
    # if request.method == 'POST':
    #     cmt = request.POST.get('cmt')
    #     id_blog = request.POST.get('id_blog')
    #     if request.user.is_authenticated:
    #         blog = Blog.objects.get(pk=id_blog)
    #         user = request.user
    #         name_user = user.username
    #         avatar_user = user.avatar if user.avatar else None
    #         data = {
    #             'cmt': cmt,
    #             'id_blog': blog,
    #             'id_user': user,
    #             'name_user': name_user,
    #             'avatar_user': avatar_user,
    #         }
    #         try:
    #             new_comment = Comment.objects.create(**data)
    #             # Lay nguyen 1 obj tra ve
    #             comment_data = Comment.objects.filter(id=new_comment.id).values().first()
    #             return JsonResponse({'success': True, 'data': comment_data})
    #         except Comment.DoesNotExist:
    #             return JsonResponse({'success': False, 'error': 'cmt not found'})
    #     return JsonResponse({'success': False, 'error': '? user'})
    # return JsonResponse({'success': False, 'error': 'Invalid request'})
    if request.method == "POST":
        cmt = request.POST.get("cmt")
        id_blog = request.POST.get("id_blog")
        id_parent = request.POST.get("id_parent")

        try:
            blog = Blog.objects.get(pk=id_blog)
            user = request.user
            new_comment = Comment.objects.create(
                cmt=cmt,
                id_user=user,
                id_blog=blog,
                name_user=user.username,
                created_at=timezone.now(),
                level=id_parent if id_parent else 0,
                avatar_user=user.avatar if user.avatar else None,
            )
            data = {
                "id": new_comment.id,
                "cmt": new_comment.cmt,
                "level": new_comment.level,
                "name_user": new_comment.name_user,
                "created_at": new_comment.created_at.strftime("%Y-%m-%d %H:%M"),
                "avatar_user": new_comment.avatar_user.url
                if new_comment.avatar_user
                else "",
            }
            # tra json sang lai js
            return JsonResponse({"success": True, "data": data})
        except Blog.DoesNotExist:
            return JsonResponse({"success": False, "error": "Blog not found"})
    return JsonResponse({"success": False, "error": "Invalid request"})
