from django.urls import path, include

from .views import ExchangerView,getVideoChatToken



urlpatterns = [
    path(
        "exchangers/",
        ExchangerView.as_view(),
        name="exchangers",
    ),
    path(
        "video-chat/",
         getVideoChatToken,
        name="video-chat-token",
    ),

]