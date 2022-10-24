from django.urls import path
from django.contrib.staticfiles.urls import staticfiles_urlpatterns

from . import views

urlpatterns = [
    path("", views.index, name="index"),
    path("login", views.login_view, name="login"),
    path("logout", views.logout_view, name="logout"),
    path("register", views.register, name="register"),

    path("listing/<id>", views.listing, name="listing"),
    path("listing/<id>/bid", views.bid, name="bid"),
    path("listing/<id>/close_bid", views.close_bid, name="close_bid"),
    path("create", views.create, name="create"),
    path("watch/<id>", views.watch, name="watch"),
    path("unwatch/<id>", views.unwatch, name="unwatch"),
    path("watchlist", views.watchlist, name="watchlist"),
    path("categories", views.categories, name="categories"),
    path("filter/", views.filter, name="filter"),
    path("comment/<id>", views.comment, name="comment")
]

urlpatterns += staticfiles_urlpatterns()
