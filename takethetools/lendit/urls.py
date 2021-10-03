from django.urls import path

from .views import (
    Home,
    LendLogView,
    Notes,
    ToolCreate,
    ToolList,
    UserList,
    add_to_cart,
    add_user,
    cart,
    checkout,
    clearbasket,
    export_barcodes,
    export_barcodes_pdf,
    register_user,
    test_view,
)

urlpatterns = [
    path("", Home.as_view(), name="home"),
    path("display_users/", register_user, name="reguser"),
    path("tools/", ToolList.as_view(), name="tools"),
    path("notes/", Notes.as_view(), name="notes"),
    path("users/", UserList.as_view(), name="users"),
    path("overview/", LendLogView.as_view(), name="overview"),
    path("register_user/", register_user, name="register_user"),
    path("tool/create", ToolCreate.as_view(), name="tool_create"),
    path("adduser/", add_user, name="adduser"),
    path("export/", export_barcodes, name="export"),
    path("add_pdf/", export_barcodes_pdf, name="add_pdf"),
    path("cart/", cart, name="cart"),
    path("add_to_cart/", add_to_cart, name="add_to_cart"),
    path("clearbasket/", clearbasket, name="clearbasket"),
    path("checkout/", checkout, name="checkout"),
    path("<str:barcode_ean13_no_check_bit>/add/", test_view, name="test_view"),
    path(
        "<str:barcode_ean13_no_check_bit>/add/", test_view, name="lendlog_button_view"
    ),
]
