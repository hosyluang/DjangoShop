from django.http import JsonResponse
from django.shortcuts import render
from django_shop.decorators import non_superuser_required
from django.template.loader import render_to_string
from django.core.mail import send_mail
from django.conf import settings


# Create your views here.


@non_superuser_required
def checkout(request):
    carts = request.session.get("cart", {})
    total_all = sum(item["qty"] * float(item["price"]) for item in carts.values())
    total_qty = sum(item["qty"] for item in carts.values())
    return render(
        request,
        "orders/checkout.html",
        {"carts": carts, "total_all": total_all, "total_qty": total_qty},
    )


@non_superuser_required
def send_order_email(request):
    if request.method == "POST":
        cart = request.session.get("cart", {})
        if not cart:
            return JsonResponse({"status": "error", "msg": "LOI"})
        # tinh tong
        total_amount = sum(item["qty"] * float(item["price"]) for item in cart.values())
        total_qty = sum(item["qty"] for item in cart.values())

        # tao noi dung email voi render_to_string
        email_context = {
            "user": request.user,
            "cart": cart,
            "total_amount": total_amount,
            "total_qty": total_qty,
            "order_id": request.user.id,
        }
        html_render = render_to_string("emails/checkout-email.html", email_context)
        try:
            # Gui email
            send_mail(
                subject=f"Don hang moi tu {request.user.username}",
                message="",  # "" vi dung html rieng
                from_email=settings.DEFAULT_FROM_EMAIL,
                recipient_list=[settings.EMAIL_HOST_USER],
                html_message=html_render,
                fail_silently=False,
            )
            request.session["cart"] = {}
            request.session.modified = True
            return JsonResponse(
                {
                    "status": "success",
                    "msg": "oder sent",
                    "redirect_url": "/order/checkout/",
                }
            )
        except Exception as e:
            return JsonResponse({"status": "error", "error": str(e)})
    return JsonResponse({"status": "error", "message": "Invalid request"})


@non_superuser_required
def update_cart(request):
    if request.method == "POST":
        product_id = str(request.POST.get("product_id"))
        action = request.POST.get("action")
        cart = request.session.get("cart", {})

        if product_id not in cart:
            return JsonResponse({"status": "error", "msg": "not found"})

        qty = int(cart[product_id]["qty"])
        if action == "up":
            qty += 1
        elif action == "down":
            qty -= 1
            if qty < 1:
                qty = 1

        price = float(cart[product_id]["price"])
        total = qty * price

        cart[product_id]["qty"] = qty
        cart[product_id]["total"] = total
        # Ghi lại session
        request.session["cart"] = cart
        total_all = sum(item["qty"] * float(item["price"]) for item in cart.values())
        cart_count = sum(item["qty"] for item in cart.values())
        return JsonResponse(
            {
                "status": "success",
                "qty": qty,
                "total": f"{total:.1f}",
                "total_all": f"{total_all:.1f}",
                "cart_count": cart_count,
            }
        )
    return JsonResponse({"status": "error"})


@non_superuser_required
def delete_cart(request):
    if request.method == "POST":
        product_id = str(request.POST.get("product_id"))
        cart = request.session.get("cart", {})
        if product_id in cart:
            del cart[product_id]
        request.session["cart"] = cart
        cart_count = sum(item["qty"] for item in cart.values())
        return JsonResponse(
            {
                "status": "success",
                "cart": cart,
                "cart_count": cart_count,
            }
        )
    return JsonResponse({"status": "error"})
