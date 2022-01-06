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


#the main page with all the listings
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
            price = form.cleaned_data["current_price"]
            url = form.cleaned_data["Image_url"]
            created_listing = Auction_listing(Title=title,Description=Description,current_price=price ,Image_url=url,Seller=request.user)
            created_listing.save()

            # Adding to categories
            listing = Auction_listing.objects.get(Title=title,Description=Description,current_price=price ,Image_url=url,Seller=request.user)
            item_select = request.POST.get('Item_category') # selected category
            category_options = Category.objects.get(Heading=item_select)
            category_options.Items.add(listing)
            category_options.save()

        return HttpResponseRedirect(reverse("index"))
    else:
        category_options = Category.objects.all() #get all categories
        Form = PostForm()
        return render(request, "auctions/create.html" ,{"form":Form, "Categories":category_options})
                
        
        
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
    
    Comments = Listing_Comments.objects.filter(Comment_item=Item)
    if Bids.objects.filter(Bid_item=ID).exists():
        pass
   # check the users whatchlist for the item
    if Watchlist.objects.filter(Person_watching=request.user ,item=ID).exists(): #add ability to remove if there
        Watched = 'Remove from watchlist'
        
    else:
        Watched = 'Add to watchlist' # add ability to add if there

    # if auction is closed see if this user won or lost
    won = None
    lost = None
    if Item.Auction_open == False:
        the_highest_bid = Item.current_price
        exact_bid = Bids.objects.get(highest_amount=the_highest_bid,Bid_item=Item)
        if exact_bid.Bidder == request.user:   #if this user won
            won = True               
        else :
            lost = True
    return render(request, "auctions/Item.html" , {"Item": Item , "Comments":Comments ,"Watchlist":Watched ,"button":button,"won":won, "lost":lost})

#Adding and removing to watchlists
def add_watchlist(request,ID):
    if Watchlist.objects.filter(Person_watching=request.user ,item=ID).exists():         # if the item exists on this users watchlist then delete
        watchlist_item = Watchlist.objects.get(Person_watching=request.user ,item=ID)
        watchlist_item.delete()
        return HttpResponseRedirect(reverse("Specific_listing",args=[ID])) 
       
    else:
        auction_item = Auction_listing.objects.get(id=ID)                                # if the item doesnt exist on this users watchlist then add
        watchlist_item = Watchlist(Person_watching=request.user ,item=auction_item)
        watchlist_item.save()
        return HttpResponseRedirect(reverse("Specific_listing",args=[ID]))

# Bidding on items
def Place_bid(request,ID):
    if request.method == "POST":
        bid = request.POST["Bid"]
        if bid == '':
            return HttpResponseRedirect(reverse("Specific_listing", args=[ID]))
        else:
            item = Auction_listing.objects.filter(id=ID)
            current_bids = Bids.objects.filter(Bid_item__in=item ,highest_amount__gte=bid).count() # See if there are any bids greater than this so far
           # Add if there are none
            if current_bids == 0:
                item = Auction_listing.objects.get(id=ID)
                new_bid = Bids(Bidder=request.user,highest_amount=bid, State=True) 
                new_bid.save()
                new_bid.Bid_item.add(item)

                # Changing the current price of an item
                item.current_price = bid
                item.save()
                messages.add_message(request, messages.INFO, "Successfully placed bid")
                return HttpResponseRedirect(reverse("Specific_listing", args=[ID]))
            else:
                messages.add_message(request, messages.INFO, "Unsuccessfully placed bid")
                return HttpResponseRedirect(reverse("Specific_listing", args=[ID]))
                   
    else:
        return HttpResponseRedirect(reverse("Specific_listing", args=[ID]))

# Closing the bids by seting State to false
def close_bid(request,ID):
    item = Auction_listing.objects.get(id=ID)
    all_bids = Bids.objects.filter(Bid_item=item).update(State=False) 
    item.Auction_open = False
    item.save()
    return HttpResponseRedirect(reverse("Specific_listing", args=[ID]))


# Returning Items that the user put on a watchlist
def watchlist(request):
    watch_list = Watchlist.objects.filter(Person_watching=request.user)
    return render(request, "auctions/watchlist.html" ,{"lists":watch_list})    

# listing differnt categories   
def Categories(request):
    Sections = Category.objects.all()
    return render(request, "auctions/categories.html" ,{"Categories":Sections})

# adding comments for each Item
def Comment(request,ID):
    if request.method == "POST":
        text = request.POST["Comment_text"]
        the_item = Auction_listing.objects.get(id=ID)
        new_comment = Listing_Comments(Text=text , Comment_item=the_item)
        new_comment.save()
        return HttpResponseRedirect(reverse("Specific_listing", args=[ID]))
    else:
        return HttpResponseRedirect(reverse("Specific_listing",args=[ID]))
    
#Showing items in each category
def Category_items(request,Heading):
    category_name = Category.objects.get(Heading=Heading)
    items = category_name.Items.all()
    print(items)
    return render(request, "auctions/categories.html" ,{"Items":items})    

 
