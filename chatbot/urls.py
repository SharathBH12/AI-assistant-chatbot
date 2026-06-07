from django.urls import path
from . import views

urlpatterns = [

    path('', views.home, name='home'),

    path('register/', views.register_page, name='register'),

    path('login/', views.login_page, name='login'),

    path('logout/', views.logout_page, name='logout'),

    path('chat/', views.chat_page, name='chat'),

    path(
        'chat/<int:chat_id>/',
        views.chat_detail,
        name='chat_detail'
    ),

    path(
        'new-chat/',
        views.new_chat,
        name='new_chat'
    ),

    path(
        'rename-chat/<int:chat_id>/',
        views.rename_chat,
        name='rename_chat'
    ),

    path(
        'delete-chat/<int:chat_id>/',
        views.delete_chat,
        name='delete_chat'
    ),

    path(
        'pin-chat/<int:chat_id>/',
        views.pin_chat,
        name='pin_chat'
    ),

    path(
        'share/<uuid:share_id>/',
        views.shared_chat,
        name='shared_chat'
    ),

    path(
        'export-pdf/<int:chat_id>/',
        views.export_pdf,
        name='export_pdf'
    ),
    
    path(
    'profile/',
    views.profile_page,
    name='profile'
    ),
]