from django.utils import timezone
from django.http import JsonResponse
from django.shortcuts import render, get_object_or_404, redirect
from store.models import Product
from offers.models import ProductOffer,CategoryOffer,ReferralOffer
from offers.forms import ProductOfferForm, CategoryOfferForm, ReferralOfferForm
from django.views.decorators.csrf import csrf_exempt

# Create your views here.

# ==================== Product Offer ========================== #

def product_offer_list(request):
    offers = ProductOffer.objects.all()
    return render(request, 'admin_panel/offers/product_offer_list.html', {'offers': offers})

def product_offer_create(request):
    if request.method == 'POST':
        form = ProductOfferForm(request.POST)
        if form.is_valid:
            form.save()
            return redirect('product_offer_list')
    else:
        form = ProductOfferForm()
    return render(request, 'admin_panel/offers/product_offer_create.html', {'form':form})
    

def product_offer_update(request, product_id):
    offer = get_object_or_404(ProductOffer, id= product_id)
    if request.method == 'POST':
        form = ProductOfferForm(request.POST, instance=offer)
        if form.is_valid():
            form.save()
            return redirect('product_offer_list')
    else:
        form = ProductOfferForm(instance = offer)
    return render(request, 'admin_panel/offers/product_offer_edit.html',{'form': form})

def product_offer_delete(request, product_id):
    offer = get_object_or_404(ProductOffer,id=product_id)
    if request.method == 'POST':
        offer.delete()
        return redirect('product_offer_list')



# ========================= Category Offer ===================== #

def category_offer_list(request):
    offers = CategoryOffer.objects.all()
    return render(request,'admin_panel/offers/category_offer_list.html', {'offers':offers})

def category_offer_create(request):
    if request.method == 'POST':
        form = CategoryOfferForm(request.POST)
        if form.is_valid:
            form.save()
            return redirect('category_offer_list')
    else:
        form = CategoryOfferForm()
    return render(request, 'admin_panel/offers/category_offer_create.html', {'form':form})

def category_offer_update(request,category_id):
    offer = get_object_or_404(CategoryOffer, id= category_id)
    if request.method == 'POST':
        form = CategoryOfferForm(request.POST, instance=offer)
        if form.is_valid():
            form.save()
            return redirect('category_offer_list')
    else:
        form = CategoryOfferForm(instance = offer)
    return render(request, 'admin_panel/offers/category_offer_edit.html',{'form': form})

def category_offer_delete(request,category_id):
    offer = get_object_or_404(CategoryOffer,id=category_id)
    if request.method == 'POST':
        offer.delete()
        return redirect('category_offer_list')

# ========================= Referral Offer ===================== #

def referral_offer_list(request):
    pass

def referral_offer_create(request):
    pass

def referral_offer_update(requst):
    pass

def referral_offer_delete(request):
    pass