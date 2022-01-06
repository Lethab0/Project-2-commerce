from django import forms
from auctions.models import Auction_listing

class PostForm(forms.ModelForm):
    Description = forms.CharField(widget=forms.Textarea)
    class Meta:
        model = Auction_listing
        fields = ['Title', 'current_price','Image_url',]
       
        

