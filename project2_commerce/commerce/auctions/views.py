from django.contrib.auth import authenticate, login, logout
from django.contrib import messages
from django.db import IntegrityError
from django.http import HttpResponseRedirect
from django.shortcuts import render
from django.urls import reverse

from .models import User, Auctions, AuctionsForm, Bids, BidsForm


def index(request):

    # Get all objects from Acutions.
    auctions = Auctions.objects.all()
    return render(request, "auctions/index.html", {
        "auctions": auctions
    })


def login_view(request):
    if request.method == "POST":

        # Attempt to sign user in.
        username = request.POST["username"]
        password = request.POST["password"]
        user = authenticate(request, username=username, password=password)

        # Check if authentication successful.
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

        # Ensure password matches confirmation.
        password = request.POST["password"]
        confirmation = request.POST["confirmation"]
        if password != confirmation:
            return render(request, "auctions/register.html", {
                "message": "Passwords must match."
            })

        # Attempt to create new user.
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
    

def create_listing(request):
        if request.method == "POST":

            # Add an item to the auction list.
            data = {
                'title': request.POST.get("title"),
                'description': request.POST.get("description"),
                'starting_price': request.POST.get("starting_price"),
                'current_price': request.POST.get("starting_price"),
                'image_url': request.POST.get("image_url"),
                'category': request.POST.get("category"),
                'username': request.user.username,
                'closed': request.POST.get("closed")
            }
            auctions_form = AuctionsForm(data)
            if auctions_form.is_valid():
                auctions_form.save()
                return HttpResponseRedirect(reverse('index'))
            else:
                messages.error(request, 'An item has not been added.')
                return HttpResponseRedirect(reverse("create_listing"))
        else:
            return render(request, "auctions/create_listing.html", {
                "auctions_form": AuctionsForm()
            })
        

def listing(request, title):
    if request.method == "POST":
        auction =  Auctions.objects.get(title=title)

        # Add, remove watchlist.
        if "watchlist" in request.POST:
            if request.POST["watchlist"] == "add":
                request.session["watchlist"] += [title]
            elif request.POST["watchlist"] == "remove":
                request.session["watchlist"].remove(title)
                request.session.modified = True
            return HttpResponseRedirect(reverse('listing', args=(title,)))
        
        # On submit close auction, remove an item from active listings.
        if "close" in request.POST:
            auction.closed = True
            auction.save()
            try:
                bid = Bids.objects.get(title=title)
                bid.closed = True
                bid.save()
            except Bids.DoesNotExist:
                pass
            return HttpResponseRedirect(reverse('index'))
        
        # Update Bids status.
        if "price" in request.POST:
            price = float(request.POST.get("price"))
            # Update current price of an item
            auction.current_price = price
            auction.save()
            try:
                bid = Bids.objects.get(title=title)
                if price > bid.price:
                    bid.price = price
                    bid.winner = request.user.username
                    bid.bids += 1
                    bid.save()
                    messages.success(request, 'Submitted a bid successfully')
                    return HttpResponseRedirect(reverse('listing', args=(title,)))
                else:
                    # Error: user must input a bid greater than other bids.
                    messages.error(request, 'Input a bid greater than other bids')
                    return HttpResponseRedirect(reverse('listing', args=(title,)))

            # When Bidding for the first time.
            except Bids.DoesNotExist: 
                if price >= Auctions.objects.get(title=title).starting_price:
                    data = {
                        'title': title,
                        'price': price,
                        'winner': request.user.username,
                        'bids': 1
                    }
                    bidsform = BidsForm(data)
                    if bidsform.is_valid():
                        bidsform.save()
                        messages.success(request, 'Submitted a bid successfully')
                        return HttpResponseRedirect(reverse('listing', args=(title,)))
                else:
                    # Error: user must input a bid at least as large as the starting price.
                    messages.error(request, 'Input a bid at least as large as the starting price')
                    return HttpResponseRedirect(reverse('listing', args=(title,)))
                
    else:
        # Check if an item is already in watchlist.
        if "watchlist" not in request.session:
            request.session["watchlist"] = []
        if title in request.session["watchlist"]:
            watchlist = True
        else : 
            watchlist = False
        if request.user.is_authenticated:
            logged_in = True
        else:
            logged_in = False

        # Check if the item is listed by the user.
        auction = Auctions.objects.get(title=title)
        if request.user.username == auction.username:
            host = True
        else:
            host = False

        # Check if the user's bid is the current bid.
        try:
            bid = Bids.objects.get(title=title)
            bids = bid.bids
            if request.user.username == bid.winner:
                is_winner = True
            else:
                is_winner = False
        except Bids.DoesNotExist:
            bids = 0
            is_winner = False

        
        item = Auctions.objects.get(title=title)
        return render(request, "auctions/listing.html", {
            "item": item,
            "watchlist": watchlist,
            "logged_in": logged_in,
            "host": host,
            "bid_form": BidsForm(),
            'bids': bids,
            'is_winner': is_winner
        })
    

def closed_listing(request):
    items = Auctions.objects.filter(closed=True)
    return render(request, "auctions/closed_listing.html", {
        "items": items
    })
