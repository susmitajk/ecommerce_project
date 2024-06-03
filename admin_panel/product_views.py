from django.shortcuts import render, redirect, get_object_or_404
from store.models import Brand, Type, Product, ProductVariant,ProductImage
from .forms import BrandForm,TypeForm,ProductForm, ProductVariantForm,ProductImageForm

#brand CRUD

# brand list view
def brand_list(request):
    brands = Brand.objects.all().order_by('-id')
    context = {'brands': brands}
    return render(request, 'admin_panel/product/brand/brand_list.html', context)

def brand_create(request):
    if request.method == 'POST':
        form = BrandForm(request.POST)
        if form.is_valid():
            form.save()
            return redirect('brand_list')
    else:
        form = BrandForm()
    return render(request, 'admin_panel/product/brand/create_brand.html', {'form': form})

def brand_update(request, brand_id):
    brand = get_object_or_404(Brand, id=brand_id)
    if request.method == 'POST':
        form = BrandForm(request.POST, instance=brand)
        if form.is_valid():
            form.save()
            return redirect('brand_list')
    else:
        form = BrandForm(instance=brand)
    return render(request, 'admin_panel/product/brand/edit_brand.html', {'form': form})

def brand_restore(request, brand_id):
    brand = get_object_or_404(Brand, id=brand_id)
    brand.restore()
    return redirect('brand_list')

def brand_delete(request, brand_id):
    brand = get_object_or_404(Brand, id=brand_id)
    brand.soft_delete()
    return redirect('brand_list')

# Type CRUD

def type_list(request):
    types = Type.objects.all().order_by('-id')
    context = {'types': types}
    return render(request, 'admin_panel/product/type/type_list.html', context)

def type_create(request):
    if request.method == 'POST':
        form = TypeForm(request.POST)
        if form.is_valid():
            form.save()
            return redirect('type_list')  # Redirect to 'type_list' instead of 'brand_list'
    else:
        form = TypeForm()
    return render(request, 'admin_panel/product/type/create_type.html', {'form': form})  # Corrected template path

def type_update(request, type_id):
    type_instance = get_object_or_404(Type, id=type_id)
    if request.method == 'POST':
        form = TypeForm(request.POST, instance=type_instance)
        if form.is_valid():
            form.save()
            return redirect('type_list')
    else:
        form = TypeForm(instance=type_instance)
    return render(request, 'admin_panel/product/type/edit_type.html', {'form': form})  # Corrected template path

def type_restore(request, type_id):
    type_instance = get_object_or_404(Type, id=type_id)
    type_instance.restore()
    return redirect('type_list')

def type_delete(request, type_id):
    type_instance = get_object_or_404(Type, id=type_id)
    type_instance.soft_delete()
    return redirect('type_list')   



# Product CRUD

def product_list(request):
    products = Product.objects.all().order_by('-id')
    return render(request, 'admin_panel/product/product/product_list.html', {'products': products})

def product_create(request):
    if request.method == 'POST':
        form = ProductForm(request.POST, request.FILES)
        if form.is_valid():
            form.save()
            return redirect('product1_list')
    else:
        form = ProductForm()
    return render(request, 'admin_panel/product/product/create_product.html', {'form': form})

def product_update(request, product_id):
    product = get_object_or_404(Product, id=product_id)
    if request.method == 'POST':
        form = ProductForm(request.POST, request.FILES, instance=product)
        if form.is_valid():
            form.save()
            return redirect('product1_list')
    else:
        form = ProductForm(instance=product)
    return render(request, 'admin_panel/product/product/edit_product.html', {'form': form})

def product_restore(request, product_id):
    product = get_object_or_404(Product, id=product_id)
    product.restore()
    return redirect('product1_list')

def product_delete(request, product_id):
    product = get_object_or_404(Product, id=product_id)
    product.soft_delete()
    return redirect('product1_list')


# Product Variant CRUD
def product_variant_list(request):
    variants = ProductVariant.objects.all().order_by('-id')
    return render(request, 'admin_panel/product/variant/variant_list.html', {"variants": variants})

def product_variant_create(request):
    if request.method == 'POST':
        form = ProductVariantForm(request.POST)
        if form.is_valid():
            form.save()
            return redirect('product_variant_list')
    else:
        form = ProductVariantForm()
    return render(request, 'admin_panel/product/variant/create_variant.html', {'form': form})

def product_variant_update(request, variant_id):
    variant = get_object_or_404(ProductVariant, id=variant_id)
    if request.method == 'POST':
        form = ProductVariantForm(request.POST, instance=variant)
        if form.is_valid():
            form.save()
            return redirect('product_variant_list')
    else:
        form = ProductVariantForm(instance=variant)
    return render(request, 'admin_panel/product/variant/edit_variant.html', {'form': form})


def product_variant_restore(request, variant_id):
    variant = get_object_or_404(ProductVariant, id=variant_id)
    variant.restore()  
    return redirect('product_variant_list')


def product_variant_delete(request, variant_id):
    variant = get_object_or_404(ProductVariant, id=variant_id)
    variant.soft_delete()  
    return redirect('product_variant_list')

# Product Image CRUD
def product_image_list(request):
    images = ProductImage.objects.all().order_by('-id')
    context = {
        'images': images,
    }
    return render(request, 'admin_panel/product/image/image_list.html', context)

def product_image_create(request):
    if request.method == 'POST':
        form = ProductImageForm(request.POST, request.FILES)
        if form.is_valid():
            form.save()
            return redirect('product_variant_list')
    else:
        form = ProductImageForm()
    return render(request, 'admin_panel/product/image/create_image.html', {'form': form})

def product_image_update(request, image_id):
    image = get_object_or_404(ProductImage, id=image_id)
    if request.method == 'POST':
        form = ProductImageForm(request.POST, request.FILES, instance=image)
        if form.is_valid():
            form.save()
            return redirect('product_image_list')
    else:
        form = ProductImageForm(instance=image)
    return render(request, 'admin_panel/product/image/edit_image.html', {'form': form})

def product_image_restore(request, image_id):
    image = get_object_or_404(ProductImage, id=image_id)
    image.restore()  
    return redirect('product_image_list')

def product_image_delete(request, image_id):
    image = get_object_or_404(ProductImage, id=image_id)
    image.soft_delete()  
    return redirect('product_image_list')
