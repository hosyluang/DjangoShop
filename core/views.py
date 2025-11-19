from django.http import JsonResponse
from django.shortcuts import render
from product.models import Product
from django.core.paginator import Paginator
from django.contrib.auth.decorators import login_required
# Create your views here.


def home(request):
    products = Product.objects.all().order_by("-id")
    paginator = Paginator(products, 6)
    page_number = request.GET.get("page")
    page_obj = paginator.get_page(page_number)
    return render(
        request, "core/home.html", {"page_obj": page_obj, "paginator": paginator}
    )


def four_zero_four(request):
    return render(request, "core/404.html")


def contact(request):
    return render(request, "core/contact.html")


@login_required
def add_to_cart(request):
    if request.method == "POST":
        product_id = str(request.POST.get("product_id"))
        product = Product.objects.get(id=product_id)
        cart = request.session.get("cart", {})

        if product_id in cart:
            cart[product_id]["qty"] += 1
            cart[product_id]["total"] = cart[product_id]["qty"] * float(
                cart[product_id]["price"]
            )
        else:
            cart[product_id] = {
                "id": product.id,
                "name": product.name,
                "image": product.images[0],
                "price": float(product.price),
                "qty": 1,
                "total": float(product.price),
            }
        request.session["cart"] = cart
        cart_count = sum(item["qty"] for item in cart.values())
        return JsonResponse(
            {
                "status": "success",
                "cart": cart,
                "cart_count": cart_count,
            }
        )
    return JsonResponse({"status": "invalid"}, status=400)
