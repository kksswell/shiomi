from django.urls import path

from . import views

urlpatterns = [
    path('bootstrap/', views.bootstrap, name='bootstrap'),
    path('server/status/', views.server_status, name='server-status'),
    path('servers/', views.servers, name='servers'),
    path('user/profile/', views.profile, name='user-profile'),
    path('auth/steam/', views.steam_login, name='steam-login'),
    path('auth/steam/return/', views.steam_return, name='steam-return'),
    path('auth/steam/dev/', views.steam_dev_login, name='steam-dev-login'),
    path('auth/logout/', views.logout, name='logout'),
    path('shop/products/', views.shop_products, name='shop-products'),
    path('shop/purchase/', views.create_purchase, name='shop-purchase'),
    path('rules/', views.rules, name='rules'),
    path('bonus/rewards/', views.rewards, name='case-rewards'),
    path('bonus/spin/', views.spin_case, name='case-spin'),
]
