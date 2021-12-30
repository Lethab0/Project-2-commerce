from django import forms
from auctions.models import Auction_listing

class PostForm(forms.ModelForm):
    Description = forms.CharField(widget=forms.Textarea)
    Image_url = forms.ImageField(required=False)
    class Meta:
        model = Auction_listing
        fields = ['Title', 'Start_bid',]
       
        

