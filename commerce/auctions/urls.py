from django.urls import path
from django.conf import settings
from django.conf.urls.static import static

from . import views


urlpatterns = [
    path("", views.index, name="index"),
    path("bid/<int:ID>", views.Place_bid, name="Place_bid"),
    path("close_bid/<int:ID>", views.close_bid, name="close_bid"),
    path("Create", views.Create_listing, name="Create_listing"),
    path("item/<str:ID>", views.Specific_listing, name="Specific_listing"),
    path("Categories", views.Categories, name="Categories"),
    path("Category_items/<str:Heading>", views.Category_items, name="Category_items"),
    path("watchlist", views.watchlist, name="watchlist"),
    path("Comment/<int:ID>", views.Comment, name="Comment"),
    path("watchlist/<int:ID>", views.add_watchlist, name="add_watchlist"),
    path("login", views.login_view, name="login"),
    path("logout", views.logout_view, name="logout"),
    path("register", views.register, name="register")

]
if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
