
from django.urls import path
from .views import Home, Registeruser, Users, Overview, Tools, registerUser, addUser, registerTool, addTool
from .views import Cart, Checkout, addToCart, clearbasket, exportBarcodes, exportBarcodesPDF

urlpatterns = [
    path('', Home, name='home'),

    path('display_users/', Registeruser, name='reguser'),
    path('tools/', Tools, name='tools'),
    path('users/', Users, name='users'),
    path('overview/', Overview, name='overview'),
    path('register/', registerUser, name='register'),
    path('registert/', registerTool, name='registert'),

    path('addtool/', addTool, name='addtool'),
    path('adduser/', addUser, name='adduser'),

    path('export/', exportBarcodes, name='export'),
    path('add_pdf/', exportBarcodesPDF, name='add_pdf'),

    path('cart/', Cart, name='cart'),
    path('add_to_cart/', addToCart, name='add_to_cart'),

    path('clearbasket/', clearbasket, name='clearbasket'),

    path('checkout/', Checkout, name='checkout'),
]
