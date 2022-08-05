import os
from django.core.paginator import Paginator
from django.shortcuts import render, get_object_or_404, redirect
from django.contrib.auth.decorators import login_required
from .models import Product, Comment, Offer
from django.contrib import messages
from .forms import NewCommentForm
from django.http import JsonResponse, HttpResponseRedirect
from .decorators import talents_only, hunters_only
from accounts.views import UserProfile
from django.core.mail import EmailMessage
from django.conf import settings

# Create your views here.
def home(request):
    products = Product.objects.all()
    paginator = Paginator(products, 3)

    page_num = request.GET.get('page')
    page_obj = paginator.get_page(page_num)

    return render(request, 'products/home.html', {'products': products, 'page_obj' : page_obj})


@login_required(login_url="/accounts/login")
@talents_only
def create(request):
    if request.method == 'POST':
        title = request.POST.get('title')
        description = request.POST.get('description')
        image = request.FILES.get("image", None)
        project_url = request.POST.get('project_url')

        product = Product()

        product.title = title
        product.description = description
        product.image = image
        product.project_url = project_url
        if len(request.FILES) != 0:
            product.image = image
       
        product.hunter = request.user
        product.save()

        messages.add_message(request, messages.SUCCESS, "product created successfully"

                             )

        return HttpResponseRedirect(request.META["HTTP_REFERER"])

    return render(request, 'products/create.html')


@login_required(login_url="/accounts/login")
@talents_only
def edit_product(request, product_id):
    product = get_object_or_404(Product, id=product_id)

    if request.method == "POST":
        if len(request.FILES) != 0:
            if len(product.image) > 0:
                os.remove(product.image.path)
            product.image = request.FILES['image']
        product.title = request.POST.get('title')
        product.description = request.POST.get('description')
        product.project_url = request.POST.get('project_url')
        product.save()
        messages.success(request, "Product Updated Successfully")
        return redirect('user_products')

    context = {'product':product}
    return render(request, 'products/edit.html', context)

@login_required(login_url="/accounts/login")
@talents_only
def delete_product(request, product_id):

    product = get_object_or_404(Product, id=product_id)
    product.remove()
    return HttpResponseRedirect(request.META["HTTP_REFERER"])


@login_required(login_url="/accounts/login")
@hunters_only
def vote(request):
    if request.POST.get('action') == 'post':
        result = ''
        id = int(request.POST.get('productid'))
        product = get_object_or_404(Product, id=id)
        if product.votes.filter(id=request.user.id).exists():
            product.votes.remove(request.user)
            product.vote_count -= 1
            result = product.vote_count
            product.save()
        else:
            product.votes.add(request.user)
            product.vote_count += 1
            result = product.vote_count
            product.save()

        return JsonResponse({'result': result, })



@login_required
@hunters_only
def collection(request):
    products = Product.objects.filter(users_collection=request.user)
    return render(request, "products/user_collection.html", {"collection": products})



@login_required
@hunters_only
def add_to_collection(request, id):
    product = get_object_or_404(Product, id=id)
    if product.users_collection.filter(id=request.user.id).exists():
        product.users_collection.remove(request.user)
        messages.success(request, product.title + " has been removed from your collection")
    else:
        product.users_collection.add(request.user)
        messages.success(request, "Added " + product.title + " to your collection")
    return HttpResponseRedirect(request.META["HTTP_REFERER"])



@login_required(login_url="/accounts/login")
def detail(request, product_id):

    product = get_object_or_404(Product, id=product_id)
    profile = UserProfile.objects.get(user=request.user)

    collect = bool

    # Heart Rating
    if product.users_collection.filter(id=request.user.id).exists():
        collect = True
    
    offer = False

    # Heart Rating
    if product.offers.filter(user=request.user).exists():
        offer = True
    
    # offers received
    counter = product.offers.filter(product=product_id).count()
    

    allcomments = product.comments.filter(status=True)

    comment_form = NewCommentForm()

    return render(request, 'products/detail.html', {'product': product, 'comment_form': comment_form, 'allcomments': allcomments, 'collect': collect, 'offer': offer, 'counter': counter, 'profile': profile})


@login_required(login_url="/accounts/login")
def addcomment(request):

    if request.method == 'POST':

        if request.POST.get('action') == 'delete':
            id = request.POST.get('nodeid')
            
            c = Comment.objects.get(id=id)
            c.delete()
            return JsonResponse({'remove': id})
        else:
            comment_form = NewCommentForm(request.POST)
            
            if comment_form.is_valid():
                user_comment = comment_form.save(commit=False)
                result = comment_form.cleaned_data.get('content')
                user = request.user.username
                user_comment.author = request.user
                user_comment.save()
                return JsonResponse({'result': result, 'user': user})


def search(request):

    title = request.GET.get('title')
    payload = []
    
    if title:
        title_objs = Product.objects.filter(title__icontains=title)

        for title_obj in title_objs:
            payload.append({"title": title_obj.title, "id": title_obj.id })
    return JsonResponse({'status': 200, 'data': payload})


@login_required(login_url="/accounts/login")
@talents_only
def user_products(request):
    products = Product.objects.filter(hunter=request.user)
    
    return render(request, "products/user_products.html", {"projects": products})

@login_required
@hunters_only
def offer(request):
    offers = Offer.objects.filter(user=request.user)
    return render(request, "products/offers.html", {"offers": offers})


@login_required(login_url="/accounts/login")
@hunters_only
def make_offer(request):
    product = get_object_or_404(Product)

    if request.method == "POST":
           
        sender_email = request.user.email
        message = request.POST.get("message", None)

        email = EmailMessage(
            f'offer for {product.title}',
            f"{message}. \n \n \n You may choose to reply via {sender_email}.",
            settings.EMAIL_HOST_USER,
            [product.hunter],
        )

        email.fail_silently=True
        email.send()

        messages.success(request, "Message sent successfully")

        offer = Offer()
        offer.message = message
        offer.sender_email = sender_email

        offer.user = request.user
        offer.product = product
        offer.save()

        
    return HttpResponseRedirect(request.META["HTTP_REFERER"])



