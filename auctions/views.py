from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.decorators import login_required 
from django.db import IntegrityError
from django.http import HttpResponse, HttpResponseRedirect
from django.shortcuts import render
from django.urls import reverse
from django.core.exceptions import ObjectDoesNotExist

from .models import User, Product, WatchList, Bid, Comment
from .forms import ProductForm, BidForm, CommentForm

def index(request):
    products = Product.objects.all()

    return render(request, "auctions/index.html", {
        "products": products
    })


def login_view(request):
    if request.method == "POST":

        # Attempt to sign user in
        username = request.POST["username"]
        password = request.POST["password"]
        user = authenticate(request, username=username, password=password)

        # Check if authentication successful
        if user is not None:
            login(request, user)
            return HttpResponseRedirect(reverse("index"))
        else:
            return render(request, "auctions/login.html", {
                "message": "Invalid username and/or password."
            })
    else:
        return render(request, "auctions/login.html")


def logout_view(request):
    logout(request)
    return HttpResponseRedirect(reverse("index"))


def register(request):
    if request.method == "POST":
        username = request.POST["username"]
        email = request.POST["email"]

        # Ensure password matches confirmation
        password = request.POST["password"]
        confirmation = request.POST["confirmation"]
        if password != confirmation:
            return render(request, "auctions/register.html", {
                "message": "Passwords must match."
            })

        # Attempt to create new user
        try:
            user = User.objects.create_user(username, email, password)
            user.save()
        except IntegrityError:
            return render(request, "auctions/register.html", {
                "message": "Username already taken."
            })
        login(request, user)
        return HttpResponseRedirect(reverse("index"))
    else:
        return render(request, "auctions/register.html")


# create new listing
def create(request):
    # when submitting form 
    if request.method == 'POST':
        # add submitted data to product form and validate
        product = ProductForm(request.POST)
        
        # if validation looks good
        if product.is_valid():
            # save product model to db and get it's id back
            product_id = product.save().id
            
            # get current logging in user id 
            user_id = request.user.id

            # query db to get this user 
            user = User.objects.get(pk=user_id)

            # query db to get latest saved product 
            product = Product.objects.get(pk=product_id)

            # add product to user and redirct
            user.products.add(product)
                
            return HttpResponseRedirect(reverse('index'))
        else:
            return render(request, 'audtions/create.html', {
                'error': True,
                'error_form': form
            })

    form = ProductForm()
    return render(request, 'auctions/create.html', {
        'form': form
    })


def product_page(request, product_id):
    # get the selected product
    product = Product.objects.get(pk=product_id)
    
    # create forms based on models to use later
    bid_form = BidForm()
    comment_form = CommentForm()

    if request.method == 'POST':

        # in every POST request pass comments to product_page.html   
        comments = Comment.objects.filter(product=product)
        
        # in every POST request should inform user with highest bid or no bids at all  
        no_bids_found = False
        highest_bid_price = None
        highest_bid_username = None 
        if not Bid.objects.filter(product=product).order_by("-id"):  
            no_bids_found = True
        else:
            highest_bid = Bid.objects.filter(product=product).order_by("-id")[0]
            highest_bid_price = highest_bid.price
            highest_bid_username = highest_bid.user.username

        
        if request.POST["who_submit"] == "watchlist":
            try:
                # get this user watchlist if exist
                watchlist = WatchList.objects.get(user=request.user)
                # get all products in that watchlist
                products = watchlist.products.all()
                
                # if selected product doesn't exist in watch list add it
                if not product in products: 
                    watchlist.products.add(product)
                    return render(request, 'auctions/product_page.html', {
                        'product': product,
                        'product_not_exist': True,
                        'bid_form': bid_form,
                        'comment_form': comment_form,
                        'latest_bid_price': highest_bid_price,
                        'latest_bid_username': highest_bid_username,
                        'no_bids_found': no_bids_found,
                        'comments': comments
                    })
                else:
                    # if selected product exist inform user with message
                    return render(request, 'auctions/product_page.html', {
                        'product': product,
                        'product_exist': True,
                        'bid_form': bid_form,
                        'comment_form': comment_form,
                        'latest_bid_price': highest_bid_price,
                        'latest_bid_username': highest_bid_username,
                        'no_bids_found': no_bids_found,
                        'comments': comments
                    })
            # if no watchlist for this user
            except ObjectDoesNotExist:
                # create new watchlist 
                watchlist = WatchList(user=request.user)
                watchlist.save()
                # add select product in that watchlist
                watchlist.products.add(product)
                return render(request, 'auctions/product_page.html', {
                    'product': product,
                    'product_not_exist': True,
                    'bid_form': bid_form,
                    'comment_form': comment_form,
                    'latest_bid_price': highest_bid_price,
                    'latest_bid_username': highest_bid_username,
                    'no_bids_found': no_bids_found,
                    'comments': comments
                })

        if request.POST["who_submit"] == 'bid':
            form = BidForm(request.POST)
            if form.is_valid():
                submitted_bid = form.cleaned_data["price"]    
          
                # if submitted bid not equal starting bid inform with error
                if submitted_bid < product.starting_bid:
                    return render(request, 'auctions/product_page.html', {
                        'product': product,
                        'bid_form': bid_form,
                        'comment_form': comment_form,
                        'bid_error': True,
                        'comments': comments
                    })
            
                # create new bid and save this bid to db
                bid = Bid(user=request.user, price=submitted_bid, product=product)
                bid.save()
                
                # if submitted bit is less than the latest saved bid delete this bid and render with error
                latest_bid = None
                if len(Bid.objects.filter(product=product)) == 1:
                    latest_bid = Bid.objects.filter(product=product).order_by('-id')[0]
                elif len(Bid.objects.filter(product=product)) > 1:
                    latest_bid = Bid.objects.filter(product=product).order_by('-id')[1]
        
                latest_bid_price = latest_bid.price
                latest_bid_username = latest_bid.user.username
                if submitted_bid < latest_bid_price:
                    bid.delete()
                    return render(request, 'auctions/product_page.html', {
                        'product': product,
                        'bid_form': bid_form,
                        'comment_form': comment_form,
                        'latest_bid_error': True,
                        'latest_bid_price': latest_bid_price,
                        'latest_bid_username': latest_bid_username,
                        'comments': comments
                    })
                else:
                    return render(request, 'auctions/product_page.html', {
                        'product': product,
                        'bid_form': bid_form,
                        'comment_form': comment_form,
                        'latest_bid_error': False,
                        'latest_bid_price': submitted_bid,
                        'latest_bid_username': request.user.username,
                        'comments': comments
                    })

            else:
                return render(request, 'acutions/product_page.html', {
                    'product': product,
                    'bid_form': form,
                    'comment_form': comment_form,
                    'comments': comments
                })

        if request.POST["who_submit"] == 'comment':
            form = CommentForm(request.POST)
            if form.is_valid():
                
                comment_content = form.cleaned_data['comment']
                comment = Comment(user=request.user, comment=comment_content, product=product)
                comment.save()
                comments = Comment.objects.filter(product=product)
                
                
                return render(request, 'auctions/product_page.html', {
                    "product": product,
                    'bid_form': bid_form,
                    'comment_form': comment_form,
                    'latest_bid_price': highest_bid_price,
                    'latest_bid_username': highest_bid_username,
                    'no_bids_found': no_bids_found,
                    'comments': comments
                })    
            else:
                return render(request, 'acutions/product_page.html', {
                    'product': product,
                    'bid_form': bid_form,
                    'comment_form': form
                })  

        if request.POST["who_submit"] == 'close':
            # get all users and see if the logged user who created this product
            products = request.user.products.all()
            if product in products:
                return render(request, 'auctions/product_page.html', {
                    'win': True,
                    'winner_name': highest_bid_username,
                    'winner_bid': highest_bid_price,
                    'product': product,
                    'comments': comments
                })
            else:
                return render(request, 'auctions/product_page.html', {
                    "product": product,
                    'bid_form': bid_form,
                    'comment_form': comment_form,
                    'latest_bid_price': highest_bid_price,
                    'latest_bid_username': highest_bid_username,
                    'no_bids_found': no_bids_found,
                    'comments': comments,
                    'closing_error': True
                })
            
    # should inform user when there is no bids while visiting the page for first time 
    no_bids_found = False
    highest_bid_price = None
    highest_bid_username = None 
    if not Bid.objects.filter(product=product).order_by("-id"):  
        no_bids_found = True
    else:
        highest_bid = Bid.objects.filter(product=product).order_by("-id")[0]
        highest_bid_price = highest_bid.price
        highest_bid_username = highest_bid.user.username
    
    comments = Comment.objects.filter(product=product)
    return render(request, 'auctions/product_page.html', {
        'product': product,
        'bid_form': bid_form,
        'comment_form': comment_form,
        'latest_bid_price': highest_bid_price,
        'latest_bid_username': highest_bid_username,
        'no_bids_found': no_bids_found,
        'comments': comments
    })

@login_required
def watching_list(request):
    
    # get user watchlist if exist
    try:
        watchlist = WatchList.objects.get(user=request.user)
        # if watchlist exist for this user get products from that watchlist and render
        products = watchlist.products.all()
        return render(request, 'auctions/watch_list.html', {
            'products': products
        })
    # if no watchlist for this user inform to go back and add products to create new watchlist for him
    except ObjectDoesNotExist:
        return render(request, 'auctions/watch_list.html', {
            'watchlist_not_exist': True
        })
    