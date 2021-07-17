from django.urls import path
from .views import (
    addToCart,
    addUser,
    Cart,
    Checkout,
    clearbasket,
    exportBarcodes,
    exportBarcodesPDF,
    Home,
    registerUser,
    ToolCreate,
    ToolList,
    LendLogView,
    UserList,
    test_view,
    Notes
)

urlpatterns = [
    path("", Home.as_view(), name="home"),
    path("display_users/", registerUser, name="reguser"),
    path("tools/", ToolList.as_view(), name="tools"),
    path("notes/", Notes.as_view(), name="notes"),
    path("users/", UserList.as_view(), name="users"),
    path("overview/", LendLogView.as_view(), name="overview"),
    path("register_user/", registerUser, name="register_user"),
    path('tool/create', ToolCreate.as_view(), name='tool_create'),
    path("adduser/", addUser, name="adduser"),
    path("export/", exportBarcodes, name="export"),
    path("add_pdf/", exportBarcodesPDF, name="add_pdf"),
    path("cart/", Cart, name="cart"),
    path("add_to_cart/", addToCart, name="add_to_cart"),
    path("clearbasket/", clearbasket, name="clearbasket"),
    path("checkout/", Checkout, name="checkout"),
    path('<str:barcode_ean13_no_check_bit>/add/', test_view, name='test_view'),
    path('<str:barcode_ean13_no_check_bit>/add/', test_view, name='lendlog_button_view'),
]

