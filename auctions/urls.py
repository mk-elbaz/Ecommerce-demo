from django.urls import path
from django.contrib.staticfiles.urls import staticfiles_urlpatterns
from django.conf.urls.static import static
from commerce import settings

from . import views

urlpatterns = [
    path("", views.index, name="index"),
    path("login", views.login_view, name="login"),
    path("logout", views.logout_view, name="logout"),
    path("register", views.register, name="register"),
    path("activeListings", views.activeListings, name="activeListings"),
    path("listing/<int:listing_id>", views.listing, name="listing"),
    path("categories", views.categories, name="categories"),
    path("categories/<str:category>", views.categoriesPage, name="categoriesPage"),
    path("createListing", views.createListing, name="createListing"),
    path("watchlist", views.watchlist, name="watchlist"),
    path("watchlistAdd/<int:listing_id>", views.watchlistAdd, name="watchlistAdd"),  
    path("listing/<int:listing_id>/close", views.closeListing, name="closeListing"),


]

urlpatterns += static(settings.MEDIA_URL, document_root= settings.MEDIA_ROOT)
