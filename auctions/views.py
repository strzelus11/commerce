from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.decorators import login_required
from django.db import IntegrityError
from django.core.exceptions import ValidationError
from django.http import Http404, HttpResponse, HttpResponseRedirect
from django.shortcuts import render, get_object_or_404
from django.urls import reverse
from django.contrib import messages

from .forms import CommentForm, ListingForm

from .models import User, Listing, Bid, Comment


def index(request):
    return render(request, "auctions/index.html", {
        "listings": Listing.objects.all().order_by("-created_at"),
        "bids": Bid.objects.all()
    })


def listing(request, id):   
    current = Listing.objects.get(pk=id)
    bid = Bid.objects.get(auction=current)
    comments = Comment.objects.filter(auction=current)
    return render(request, "auctions/listings.html", {
        "listing": current,
        "bid": bid,
        "user": request.user,
        "comments": comments,
        "comment_form": CommentForm()
    })


@login_required(login_url="auctions/login.html")
def bid(request, id):
    amount = request.POST["bid"]
    if amount:
        amount = float(amount)
        amount = round(amount, 4)
        listing = get_object_or_404(Listing, id=id)
        if amount > get_object_or_404(Bid, auction=listing).bid_amount:
            bid = get_object_or_404(Bid, auction=listing)
            bid.user = request.user
            bid.bid_amount = amount
            bid.save()
            listing.bid_count += 1
            listing.save()
            messages.add_message(request, messages.SUCCESS, "You added a bid successfully.")
            return HttpResponseRedirect(reverse("index"))
        else: 
            raise ValidationError("Bid must be greater than current Bid value")
    else:
        raise ValidationError("Bid must be greater than current Bid value")


@login_required(login_url="auctions/login.html")
def create(request):
    form = ListingForm(request.POST)
    if form.is_valid():
        auction = Listing(user=request.user, **form.cleaned_data)
        if not auction.image_url:
            auction.image_url = 'auctions/static/image.png'
        auction.save()
        starting_bid = auction.starting_bid
        bid = Bid(bid_amount=starting_bid, user=request.user, auction=auction)
        bid.save()
        messages.add_message(request, messages.SUCCESS, "You created a listing successfully.")
        return HttpResponseRedirect(reverse("index"))

    return render(request, "auctions/create.html", {
        "form": form
    })


@login_required(login_url="auctions/login.html")
def watch(request, id):
    auction = get_object_or_404(Listing, id=id)
    request.user.watchlist.add(auction)
    request.user.watchlist_counter += 1
    request.user.save()
    messages.add_message(request, messages.SUCCESS, "Listing added to your watchlist.")
    return HttpResponseRedirect(reverse("watchlist"))


@login_required(login_url="auctions/login.html")
def unwatch(request, id):
    auction = get_object_or_404(Listing, id=id)
    request.user.watchlist.remove(auction)
    request.user.watchlist_counter -= 1
    request.user.save()
    messages.add_message(request, messages.ERROR, "Listing removed from your watchlist.")
    return HttpResponseRedirect(reverse("index"))


def categories(request):
    return render(request, "auctions/categories.html")


def filter(request):
    q = request.POST.get("category", False)
    return render(request, "auctions/category.html", {
        "listings": Listing.objects.filter(category__contains=q),
        "query": q
    })


@login_required(login_url="auctions/login.html")
def close_bid(request, id):
    auction = get_object_or_404(Listing, id=id)
    bid = get_object_or_404(Bid, auction=auction)
    auction.winner = bid.user.username
    auction.is_active = False
    auction.save()
    return HttpResponseRedirect(reverse("index"))


@login_required(login_url="auctions/login.html")
def comment(request, id):
    anonymous = User.first_name
    if request.user is not anonymous:
        form = CommentForm(request.POST)
        if form.is_valid():
            f = form.cleaned_data
            comment = Comment(
                user=request.user,
                auction=get_object_or_404(Listing, id=id),
                **f
            )
            comment.save()
            return HttpResponseRedirect(reverse('listing', kwargs={
                'id': id
            }))
        raise Http404
    return render(request, 'auctions/login.html', {
        'message': 'Must be logged in to be able to comment!'
    })   


@login_required(login_url="auctions/login.html")
def watchlist(request):
    return render(request, "auctions/watchlist.html", {
        "watchlist": request.user.watchlist.all()
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
            messages.add_message(request, messages.SUCCESS, "Hello, you are logged in!")
            return HttpResponseRedirect(reverse("index"))
        else:
            messages.add_message(request, messages.ERROR, "Invalid username or password")
            return render(request, "auctions/login.html")
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