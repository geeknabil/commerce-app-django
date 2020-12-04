from django.forms import ModelForm, Textarea, TextInput, NumberInput
from .models import Product, Bid, Comment

class ProductForm(ModelForm):
    class Meta:
        model = Product
        fields = ['title', 'description', 'starting_bid', 'img']
        widgets = {
            'title': TextInput(attrs={'class': 'form-control'}),
            'description': Textarea(attrs={'rows': 3,'class': 'form-control'}),
            'starting_bid': NumberInput(attrs={'class': 'form-control'}),
            'img': TextInput(attrs={'class': 'form-control'})
        }



class BidForm(ModelForm):
    class Meta:
        model = Bid
        fields = ['price']
        widgets = {'price': NumberInput(attrs={"placeholder": "Add your bid here:"})}
        labels = {
            "price": ""
        }

class CommentForm(ModelForm):
    class Meta:
        model = Comment
        fields = ['comment']
        widgets = {'comment': TextInput(attrs={"placeholder": "Add your comment here: "})}
        labels = {
            'comment': ""
        }