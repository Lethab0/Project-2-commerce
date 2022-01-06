from django.contrib.auth.models import AbstractUser
from django.db import models
from django.conf import settings


class User(AbstractUser):
    pass
#User Profile
class Profile(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE , null=True)
    Username = models.CharField(max_length=30)
    email = models.CharField( max_length=30)
    password = models.CharField(max_length=15)
    models.CharField(max_length=30)

# The iTem information
class Auction_listing(models.Model):
    Seller = models.ForeignKey(User, on_delete=models.CASCADE , null=True)
    Title = models.CharField(max_length=30)
    Description = models.CharField(max_length=100)
    current_price = models.IntegerField(null=False, default=0)
    Image_url = models.CharField(max_length=3000, null=True ,blank=True)
    Auction_open = models.BooleanField(null=False , default=True)

# all succesful placed bids
class Bids(models.Model):
    Bidder = models.ForeignKey(User,on_delete=models.CASCADE , null=True)
    Bid_item = models.ManyToManyField(Auction_listing)
    highest_amount = models.DecimalField(max_digits=5, decimal_places=2 , default=0) 
    State = models.BooleanField(default=False)

# The comments for the items
class Listing_Comments(models.Model):
    Comment_item = models.ForeignKey(Auction_listing,on_delete=models.CASCADE)
    Text = models.CharField(max_length=200)

# Item catagories
class Category(models.Model):
    Heading = models.CharField(max_length=15 , null=True)
    Items = models.ManyToManyField(Auction_listing, blank=True)

# Watchlist
class Watchlist(models.Model):
    Person_watching = models.ForeignKey(User, on_delete=models.CASCADE , null=True)
    item = models.ForeignKey(Auction_listing ,on_delete=models.CASCADE , null=True)
