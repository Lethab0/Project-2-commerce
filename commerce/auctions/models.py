from django.contrib.auth.models import AbstractUser
from django.db import models
from django.conf import settings


class User(AbstractUser):
    pass

class Profile(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE , null=True)
    Username = models.CharField(max_length=30)
    email = models.CharField( max_length=30)
    password = models.CharField(max_length=15)
    models.CharField(max_length=30)

class Auction_listing(models.Model):
    Seller = models.ForeignKey(User, on_delete=models.CASCADE , null=True)
    Title = models.CharField(max_length=30)
    Description = models.CharField(max_length=100)
    Start_bid = models.IntegerField(null=False, default=0)
    Image_url = models.CharField(max_length=300, null=True)

class Bids(models.Model):
    Bidder = models.ForeignKey(User,on_delete=models.CASCADE , null=True)
    Bid_item = models.ManyToManyField(Auction_listing)
    highest_amount = models.DecimalField(max_digits=5, decimal_places=2 , default=0) 
    State = models.BooleanField(default=False)

class Listing_Comments(models.Model):
    Comment_item = models.ForeignKey(Auction_listing,on_delete=models.CASCADE)
    Text = models.CharField(max_length=200)

class Category(models.Model):
    Heading = models.CharField(max_length=15 , null=True)
    Items = models.ManyToManyField(Auction_listing)

class Watchlist(models.Model):
    Person_watching = models.ForeignKey(User, on_delete=models.CASCADE , null=True)
    item = models.OneToOneField(Auction_listing ,on_delete=models.CASCADE , null=True)



    
#ID = models.AutoField(primary_key=True)