
from django.urls import path

from .views import Home, Users, Overview, ToolList, registerUser, addUser, registerTool, addTool

from .views import Cart, Checkout, addToCart, clearbasket, exportBarcodes, exportBarcodesPDF

urlpatterns = [
    path('', Home, name='home'),

    path('display_users/', registerUser, name='reguser'),
    path('tools/', ToolList.as_view(), name='tools'),

    path('users/', Users, name='users'),
    path('overview/', Overview, name='overview'),
    path('register_user/', registerUser, name='register_user'),

    path('register_tool/', registerTool, name='register_tool'),
    path('addtool/', addTool, name='addtool'),
    path('adduser/', addUser, name='adduser'),

    path('export/', exportBarcodes, name='export'),
    path('add_pdf/', exportBarcodesPDF, name='add_pdf'),

    path('cart/', Cart, name='cart'),
    path('add_to_cart/', addToCart, name='add_to_cart'),

    path('clearbasket/', clearbasket, name='clearbasket'),

    path('checkout/', Checkout, name='checkout'),
]
