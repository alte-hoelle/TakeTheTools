from django.urls import path
from lendit.views import (
    addToCart,
    addUser,
    Cart,
    Checkout,
    clearbasket,
    exportBarcodes,
    exportBarcodesPDF,
    Home,
    Overview,
    registerUser,
    ToolCreate,
    ToolList,
    UserList,
)

urlpatterns = [
    path("", Home.as_view(), name="home"),
    path("display_users/", registerUser, name="reguser"),
    path("tools/", ToolList.as_view(), name="tools"),
    path("users/", UserList.as_view(), name="users"),
    path("overview/", Overview, name="overview"),
    path("register_user/", registerUser, name="register_user"),
    path('tool/create', ToolCreate.as_view(), name='tool_create'),
    path("adduser/", addUser, name="adduser"),
    path("export/", exportBarcodes, name="export"),
    path("add_pdf/", exportBarcodesPDF, name="add_pdf"),
    path("cart/", Cart, name="cart"),
    path("add_to_cart/", addToCart, name="add_to_cart"),
    path("clearbasket/", clearbasket, name="clearbasket"),
    path("checkout/", Checkout, name="checkout"),
]
