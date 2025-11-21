import os
from PIL import Image
from django.conf import settings
from django.http import JsonResponse
from .models import Category, Brand, Product
from django.db.models import Q
from django.core.paginator import Paginator
from django.shortcuts import render, get_object_or_404
from django.contrib.auth.decorators import login_required
# Create your views here.


@login_required
def my_product(request):
    products = Product.objects.filter(user=request.user)
    return render(request, "product/my-product.html", {"products": products})


@login_required
def add_product(request):
    category = Category.objects.all()
    brand = Brand.objects.all()
    if request.method == "POST":
        name = request.POST.get("name")
        price = request.POST.get("price")
        category_id = request.POST.get("category")
        brand_id = request.POST.get("brand")
        status = request.POST.get("status") == "1"  # True neu chon sale
        sale = request.POST.get("sale") if status else 0
        company = request.POST.get("company")
        detail = request.POST.get("detail")
        files = request.FILES.getlist("images")

        # validate
        errors = {}

        if not name:
            errors["name"] = "Vui long nhap ten san pham"
        if not price:
            errors["price"] = "Vui long nhap gia san pham"
        else:
            try:
                price = float(price)
                if price < 0:
                    errors["price"] = "Gia phai la so duong"
            except ValueError:
                errors["price"] = "Gia khong hop le"

        if not files:
            errors["images"] = "Phai chon it nhat 1 anh"
        elif len(files) > 3:
            errors["images"] = "Toi da 3 file"
        else:
            for file in files:
                if file.content_type not in ["image/jpeg", "image/png"]:
                    errors["images"] = f"{file.name} file khong hop le (jpg,png)"
                    break
                if file.size > 1 * 1024 * 1024:
                    errors["images"] = f"{file.name} file qua 1MB"
                    break
        if errors:
            return JsonResponse({"status": "error", "errors": errors}, status=400)

        # save file
        saved_filenames = []

        for file in files:
            filename = file.name.replace(" ", "_")
            base, ext = os.path.splitext(filename)
            ext = ext.lower()

            save_folder = os.path.join(settings.MEDIA_ROOT, "products")
            os.makedirs(save_folder, exist_ok=True)
            original_path = os.path.join(save_folder, f"{base}{ext}")
            with open(original_path, "wb+") as dest:
                for chunk in file.chunks():
                    dest.write(chunk)
            saved_filenames.append(f"products/{base}{ext}")
            img = Image.open(original_path)
            for size in [100, 200]:
                img_copy = img.copy()
                img_copy.thumbnail((size, size))
                resized_name = f"{size}_{base}{ext}"
                resized_path = os.path.join(save_folder, resized_name)
                img_copy.save(resized_path)

        Product.objects.create(
            user=request.user,
            name=name,
            price=price,
            category_id=category_id,
            brand_id=brand_id,
            status=status,
            sale=sale or 0,
            company=company,
            detail=detail,
            images=saved_filenames,
        )
        return JsonResponse(
            {"status": "success", "redirect_url": "/product/my-product/"}
        )
    return render(
        request, "product/add-product.html", {"category": category, "brand": brand}
    )


@login_required
def edit_product(request, pk):
    category = Category.objects.all()
    brand = Brand.objects.all()
    product = get_object_or_404(Product, pk=pk, user=request.user)
    if request.method == "POST":
        name = request.POST.get("name")
        price = request.POST.get("price")
        category_id = request.POST.get("category")
        brand_id = request.POST.get("brand")
        status = request.POST.get("status") == "1"
        sale = request.POST.get("sale") if status else 0
        company = request.POST.get("company")
        detail = request.POST.get("detail")
        files = request.FILES.getlist("images")
        hinhcu = product.images or []
        hinhxoa = request.POST.getlist("hinhxoa[]")
        hinhconlai = [img for img in hinhcu if img not in hinhxoa]

        # validate
        errors = {}
        if not name:
            errors["name"] = "Vui long nhap ten san pham"
        if not price:
            errors["price"] = "Vui long nhap gia san pham"
        else:
            try:
                price = float(price)
                if price < 0:
                    errors["price"] = "Gia phai la so duong"
            except ValueError:
                errors["price"] = "Gia khong hop le"

        if len(hinhconlai) + len(files) > 3:
            errors["images"] = "Tong hinh moi + cu toi da la 3"
        else:
            for file in files:
                if file.content_type not in ["image/jpeg", "image/png"]:
                    errors["images"] = f"{file.name} file khong hop le (jpg,png)"
                    break
                if file.size > 1 * 1024 * 1024:
                    errors["images"] = f"{file.name} file qua 1MB"
                    break
        if errors:
            return JsonResponse({"status": "error", "errors": errors}, status=400)

        # Xoa hinh bi checked
        for img in hinhxoa:
            img_path = os.path.join(settings.MEDIA_ROOT, img)
            if os.path.exists(img_path):
                os.remove(img_path)
            # Xóa luôn các thumbnail 100_, 200_
            base_name = os.path.basename(img)  # vd: abc.jpg
            name, ext = os.path.splitext(base_name)
            folder = os.path.dirname(img_path)
            for size in [100, 200]:
                thumb_path = os.path.join(folder, f"{size}_{name}{ext}")
                if os.path.exists(thumb_path):
                    os.remove(thumb_path)
        # Save file
        save_folder = os.path.join(settings.MEDIA_ROOT, "products")
        os.makedirs(save_folder, exist_ok=True)
        new_images = []
        for file in files:
            filename = file.name.replace(" ", "_")
            base, ext = os.path.splitext(filename)
            ext = ext.lower()
            file_path = os.path.join(save_folder, f"{base}{ext}")
            with open(file_path, "wb+") as dest:
                for chunk in file.chunks():
                    dest.write(chunk)
            new_images.append(f"products/{base}{ext}")

        product.name = name
        product.price = price
        product.category_id = category_id
        product.brand_id = brand_id
        product.status = status
        product.sale = sale or 0
        product.company = company
        product.detail = detail
        product.images = hinhconlai + new_images
        product.save()

        return JsonResponse(
            {"status": "success", "redirect_url": "/product/my-product/"}
        )
    return render(
        request,
        "product/edit-product.html",
        {"product": product, "category": category, "brand": brand},
    )


@login_required
def delete_product(request, pk):
    if request.method == "POST":
        product = get_object_or_404(Product, pk=pk, user=request.user)
        product.delete()
        return JsonResponse({"success": True})
    return JsonResponse({"success": False, "error": "Invalid request"}, status=400)


@login_required
def product_detail(request, pk):
    product = get_object_or_404(Product, pk=pk)
    return render(request, "product/product-details.html", {"product": product})


@login_required
def cart(request):
    cart = request.session.get("cart", {})
    total_all = sum(item["qty"] * float(item["price"]) for item in cart.values())
    return render(request, "product/cart.html", {"cart": cart, "totalAll": total_all})


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


@login_required
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


@login_required
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


def search_name(request):
    # Lay tham so tu url
    query = request.GET.get("q", "")
    results = ""
    if query:
        # name__icontains = WHERE name_product LIKE "%name%"
        results = Product.objects.filter(name__icontains=query)
    return render(request, "product/search.html", {"query": query, "results": results})


def search_advanced(request):
    categories = Category.objects.all()
    brands = Brand.objects.all()
    products = Product.objects.all().order_by("-id")

    name_query = request.GET.get("name", "")
    price_query = request.GET.get("price", "")
    category_query = request.GET.get("category", "")
    brand_query = request.GET.get("brand", "")
    status_query = request.GET.get("status", "")

    if name_query:
        products = products.filter(name__icontains=name_query)
    if category_query:
        products = products.filter(category_id=category_query)
    if brand_query:
        products = products.filter(brand_id=brand_query)
    if status_query:
        if status_query == "1":  # SALE
            products = products.filter(status=True)
        elif status_query == "0":  # NEW
            products = products.filter(status=False)
    if price_query:
        try:
            min_price, max_price = price_query.split("-")
            products = products.filter(price__range=(min_price, max_price))
        except ValueError:
            pass
    # Phan trang
    paginator = Paginator(products, 6)
    page_number = request.GET.get("page")
    page_obj = paginator.get_page(page_number)
    context = {
        "paginator": paginator,
        "products": page_obj,
        "categories": categories,
        "brands": brands,
        "search_name": name_query,
        "search_price": price_query,
        "search_category": int(category_query) if category_query else "",
        "search_brand": int(brand_query) if brand_query else "",
        "search_status": status_query,
    }
    return render(request, "product/shop.html", context)
