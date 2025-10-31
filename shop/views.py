from django.shortcuts import get_object_or_404, redirect, render
from django.views.generic import ListView, DetailView
from .models import Product, Category
from decimal import Decimal

# ---------------------------
# Product Views
# ---------------------------
class ProductListView(ListView):
    model = Product
    template_name = 'shop/product_list.html'
    context_object_name = 'products'

class ProductDetailView(DetailView):
    model = Product
    template_name = 'shop/product_detail.html'
    context_object_name = 'product'

# ---------------------------
# Category View
# ---------------------------
def category_products(request, slug):
    category = get_object_or_404(Category, slug=slug)
    products = category.products.filter(available=True)
    return render(request, 'shop/category.html', {'category': category, 'products': products})

# ---------------------------
# Search View
# ---------------------------
def search(request):
    query = request.GET.get('q')
    products = Product.objects.filter(name__icontains=query, available=True) if query else []
    return render(request, 'shop/search_results.html', {'products': products, 'query': query})

# ---------------------------
# Cart Views
# ---------------------------
def add_to_cart(request, pk):
    """Add product to cart or increase quantity"""
    product = get_object_or_404(Product, pk=pk)
    cart = request.session.get('cart', {})
    if str(pk) in cart:
        cart[str(pk)]['quantity'] += 1
    else:
        cart[str(pk)] = {
            'name': product.name,
            'price': str(product.price),
            'quantity': 1,
            'image': product.image.url if product.image else ''
        }
    request.session['cart'] = cart
    return redirect('shop:view_cart')  # Redirect to cart page

def remove_from_cart(request, pk):
    """Remove a product completely from the cart"""
    cart = request.session.get('cart', {})
    if str(pk) in cart:
        del cart[str(pk)]
        request.session['cart'] = cart
    return redirect('shop:view_cart')

def update_cart(request, pk):
    """Update quantity from a form"""
    cart = request.session.get('cart', {})
    if str(pk) in cart and request.method == 'POST':
        quantity = int(request.POST.get('quantity', 1))
        if quantity > 0:
            cart[str(pk)]['quantity'] = quantity
        else:
            del cart[str(pk)]
        request.session['cart'] = cart
    return redirect('shop:view_cart')

def view_cart(request):
    """Display the shopping cart"""
    cart = request.session.get('cart', {})
    total = sum(Decimal(item['price']) * item['quantity'] for item in cart.values())
    return render(request, 'shop/cart.html', {'cart': cart, 'total': total})
