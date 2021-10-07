import auctions
from django.contrib.auth import authenticate, login, logout
from django.db import IntegrityError
from django.http import HttpResponse, HttpResponseRedirect
from django.shortcuts import render
from django.urls import reverse
from django.contrib.auth.decorators import login_required
from django.forms import ModelForm
from django import forms



from .models import *

#https://docs.djangoproject.com/en/3.0/topics/forms/
#https://docs.djangoproject.com/en/3.2/topics/forms/modelforms/


class newAuctionListingForm(ModelForm):
    class Meta:
        model = auctionListing
        fields = ['title', 'desc', 'startingBid', 'categoryType', 'image']
        widgets = {
            'title' : forms.TextInput(attrs={'class': 'form-control'}),
            'desc' : forms.Textarea(attrs={'class': 'form-control'}),
        }


class newBidForm(ModelForm):
    class Meta:
        model = bids
        fields = ['price']


class newCommentForm(ModelForm):
    class Meta:
        model = Comments
        fields = ['text']
        widgets = {
            'text': forms.TextInput(attrs={'class': 'form-control', 'id': 'comment' , 'rows': '5'}),
        }
        
        


def index(request):
    return render(request, "auctions/index.html")


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


def activeListings(req):
    listings = auctionListing.objects.filter(active=True).all()
    return render(req, "auctions/index.html", {
        "listings" : listings
    })





@login_required
def listing(req, listing_id):
    listingItem = auctionListing.objects.get(id = listing_id)
    if req.method == "POST":
        if not listingItem.closed:
            if req.POST.get('text') is not None:
                commentForm = newCommentForm(req.POST)
                if commentForm.is_valid():
                    newComment = commentForm.save(commit=False)
                    newComment.author = req.user
                    newComment.save()
                    listingItem.comments.add(newComment)
                    listingItem.save()
                else:
                    return render(req, "auctions/listing.html",{
                            "comment_form" : commentForm
                    })            
            user = User.objects.get(username = req.user)
            if req.POST.get('price') is not None:
                newPrice = float(req.POST.get('price'))
                if user != listingItem.listingOwner.username:
                    if newPrice <= listingItem.startingBid:
                        return render(req, "auctions/listing.html",{
                            "message" : "Invalid bid amount",
                            "form" : newBidForm(),
                            "listing" : listingItem
                        })
                    form = newBidForm(req.POST)
                    if form.is_valid():
                        newBid = form.save(commit=False)
                        newBid.user = user
                        newBid.save()
                        listingItem.bids.add(newBid)                        
                        listingItem.buyer = user                        
                        listingItem.startingBid = newPrice
                        listingItem.save()
                    else:
                        return render(req, "auctions/listing.html",{
                            "form" : form
                        })
            return HttpResponseRedirect(reverse("listing" , args=(listing_id,)))   
    else:    
        c = dict(Categories)
        comments = listingItem.comments.all()
        if req.user in listingItem.usersWatching.all():
            listingItem.watch = True
        else:
            listingItem.watch = False 
        return render(req, "auctions/listing.html", {
            "listing" : listingItem,
            "category" : c[listingItem.categoryType],
            "form" : newBidForm(),
            "message" : "",
            "comment_form" : newCommentForm(),
            "comments" : comments
        })


@login_required
def categories(req):
    return render(req, 'auctions/categories.html', {
        "categories": Categories,
    })

@login_required
def categoriesPage(req,category):
    listings = auctionListing.objects.filter(categoryType = category[0])
    #https://djangobook.com/course/lists-dictionaries-and-tuples/
    c = dict(Categories)
    return render(req, 'auctions/specificCateg.html', {
        "listings" : listings,
        "category" : c[category]
    })

@login_required
def watchlist(req):
    listings = req.user.listingsWatched.all()
    return render(req, "auctions/watchlist.html", {
        "listings" : listings
    })



@login_required
def watchlistAdd(req, listing_id):
    item = auctionListing.objects.get(id = listing_id)
    if req.user in item.usersWatching.all():
        item.usersWatching.remove(req.user)
    else:
        item.usersWatching.add(req.user)

    return HttpResponseRedirect(reverse("listing" , args=(listing_id,)))



#https://stackoverflow.com/questions/47718382/upload-image-via-modelform-in-django
@login_required
def createListing(req):
    if req.method == "POST":
        owner = User.objects.get(username = req.user)
        form = newAuctionListingForm(req.POST , req.FILES)
        if form.is_valid():
            newListing = form.save(commit=False)
            newListing.listingOwner = owner
            newListing.image = form.cleaned_data['image']
            newListing.save()
            return HttpResponseRedirect(reverse('index'))
        else:
            return render(req, "auctions/createListing.html" , {
                "form" : form
            })   
    else:
        return render(req, "auctions/createListing.html" , {
                "form" : newAuctionListingForm()
            }) 




def closeListing(req, listing_id):
    item = auctionListing.objects.get(id = listing_id)
    if req.user == item.listingOwner:
        item.active = False
        item.winner = item.buyer
        item.save()
        return HttpResponseRedirect(reverse("listing" , args=(listing_id,))) 
