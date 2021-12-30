from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.db import IntegrityError
from django.http import HttpResponse, HttpResponseRedirect
from django.shortcuts import render 
from django.urls import reverse
from django.db.models import Max
from auctions.forms import *
    

from .models import *


#the mai page with all the listings
def index(request):
    #get all listings
    listing_object = Auction_listing.objects.all() 
    return render(request, "auctions/index.html" , {"listings": listing_object})


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


# Creating a new listing
@login_required
def Create_listing(request):
    if request.method == "POST":
        form = PostForm(request.POST)
        if form.is_valid():
            title = form.cleaned_data["Title"]
            Description = form.cleaned_data["Description"]
            price = form.cleaned_data["Start_bid"]
            url = form.cleaned_data["Image_url"]
            created_listing = Auction_listing(Title=title,Description=Description,Start_bid=price ,Image_url=url,Seller=request.user)
            created_listing.save()
        return render(request, "auctions/create.html" )
    else:
        Form = PostForm()
        return render(request, "auctions/create.html" ,{"form":Form})
                
        
        
 #Fix the Order of Specific  and Visual looks  but then  we pretty much done   
        

def Specific_listing(request,ID):
    #if this user made the listing and give them the ability to close
    creator = Auction_listing.objects.get(id=ID)
    Item = Auction_listing.objects.get(id=ID)
    if (creator.Seller == request.user) and (Bids.objects.filter(Bid_item=Item ,State=True).exists()):
        button = 'Close Auction'
    else:
        button = None
        highest_bid = Bids.objects.filter(Bid_item=Item).aggregate(Max('highest_amount'))
        # get the dictionary value
        best_bid = highest_bid['highest_amount__max']
    try:
        highest_bidder = Bids.objects.get(Bid_item=Item, highest_amount=best_bid)
    except:
        highest_bidder = None
    
   # if (highest_bidder.Bidder == request.user):
     #   pass
    Comments = Listing_Comments.objects.filter(Comment_item=Item)
    if Bids.objects.filter(Bid_item=ID).exists():
        pass
    #is_active = Bids.objects.get(Bid_item=Item)
    #if is_active.State == True:
    #    pass
    #else:
       # pass
    if Watchlist.objects.filter(Person_watching=request.user ,item=ID).exists():
        Watched = 'Remove from watchlist'
        #w_list = Watchlist(Person_watching=request.user, item=ID )
    else:
        Watched = 'Add to watchlist'
    return render(request, "auctions/Item.html" , {"Item": Item , "Comments":Comments ,"Watchlist":Watched ,"button":button})


def add_watchlist(request,ID):
    if Watchlist.objects.filter(Person_watching=request.user ,item=ID).exists():
        watchlist_item = Watchlist.objects.get(Person_watching=request.user ,item=ID)
        watchlist_item.delete()
        return HttpResponseRedirect(reverse("Specific_listing",args=[ID])) 
        #w_list = Watchlist(Person_watching=request.user, item=ID )
    else:
        auction_item = Auction_listing.objects.get(id=ID)
        watchlist_item = Watchlist(Person_watching=request.user ,item=auction_item)
        watchlist_item.save()
        return HttpResponseRedirect(reverse("Specific_listing",args=[ID]))  


#def remove_watchlist():
#    if request.user.is_authenticated:
#        remove_auction = Auction.objects.get(id=auction_id)
#        watchlist = WatchList.objects.get(user = request.user).auctions.remove(remove_auction)  

def Place_bid(request,ID):
    if request.method == "POST":
        bid = request.POST["Bid"]
        item = Auction_listing.objects.filter(id=ID)
        current_bids = Bids.objects.filter(Bid_item__in=item ,highest_amount__gte=bid).count()
        if current_bids == 0:
            item = Auction_listing.objects.get(id=ID)
            new_bid = Bids(Bidder=request.user,highest_amount=bid, State=True) 
            new_bid.save()
            new_bid.Bid_item.add(item)
            messages.add_message(request, messages.INFO, "Successfully placed bid")
            return HttpResponseRedirect(reverse("Specific_listing", args=[ID]))
        else:
            return HttpResponseRedirect(reverse("Specific_listing", args=[ID]))           
    else:
        return HttpResponseRedirect(reverse("Specific_listing", args=[ID]))

# Closing the bids by seting State to false
def close_bid(request,ID):
    item = Auction_listing.objects.get(id=ID)
    all_bids = Bids.objects.filter(Bid_item=item).update(State=False) 
    return HttpResponseRedirect(reverse("Specific_listing", args=[ID]))


def watchlist(request):
    watch_list = Watchlist.objects.filter(Person_watching=request.user)
    return render(request, "auctions/watchlist.html" ,{"lists":watch_list})    
    
def Categories(request):
    Sections = Category.objects.all()
    return render(request, "auctions/categories.html" ,{"Categories":Sections})

    
def Comment(request,ID):
    if request.method == "POST":
        text = request.POST["Comment_text"]
        the_item = Auction_listing.objects.get(id=ID)
        new_comment = Listing_Comments(Text=text , Comment_item=the_item)
        new_comment.save()
        return HttpResponseRedirect(reverse("Specific_listing", args=[ID]))
    else:
        return HttpResponseRedirect(reverse("Specific_listing",args=[ID]))
    
def Category_items(request,Heading):
    items = Category.objects.filter(Heading=Heading)
    pass     

 
