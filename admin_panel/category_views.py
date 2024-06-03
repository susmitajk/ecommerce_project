
from django.shortcuts import render, get_object_or_404, redirect
from django.http import HttpResponseServerError
from category.models import Category
from .forms import CategoryForm
from django.http import JsonResponse

# listing categories
def category_list(request):
    category = Category.available_objects.all().order_by('-id')
    context = {'category': category}
    return render(request, 'admin_panel/category/category_list.html', context=context)

# add new category view
def add_category(request):
    if request.method == 'POST':
        form = CategoryForm(request.POST, request.FILES)
        if form.is_valid():
            try:
                print(form.cleaned_data)
                form.save()
                return redirect('category_list')
            except Exception as e:
                print(f"Error saving product: {e}")
                return HttpResponseServerError("Error saving product")
        else:
            print(form.errors)
    else:
        form = CategoryForm()
    return render(request, 'admin_panel/category/create_category.html', {'form': form})


# Edit category view
def edit_category(request, category_id):
    category = get_object_or_404(Category, pk=category_id)
    if request.method == 'POST':
        form = CategoryForm(request.POST, request.FILES, instance=category)
        if form.is_valid():
            form.save()
            return redirect('category_list')  # Redirect to category list page after successful edit
    else:
        form = CategoryForm(instance=category)
    return render(request, 'admin_panel/category/edit_category.html', {'form': form})

# Activate the category
def activate_category(request, category_id):
    category = get_object_or_404(Category, id=category_id)
    category.restore()  # Restore function defined in the model
    return redirect('category_list')

# Deactivate the category
def deactivate_category(request, category_id):
    category = get_object_or_404(Category, id=category_id)
    category.soft_delete() # Soft delete function defined in the model
    return redirect('category_list')