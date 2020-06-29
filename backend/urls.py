from django.urls import path
from backend import views as bv
from frontend import views as fv


urlpatterns = [
    path("admin/dashboard/", bv.AdminIndex.as_view(), name="admin_index"),
    path("admin/users/", bv.AdminUsers.as_view(), name="admin_users"),
    path("admin/logout/", fv.UserLogout.as_view(), name="admin_logout"),
    path("admin/payments/", bv.PaymentDetails.as_view(), name="payment_details"),
    path("admin/all-payments/", bv.AllPaymentsByUsers.as_view(), name="all_payment_details"),
    path("admin/cash-out-requests/", bv.CashOutRequest.as_view(), name="cash_out_request"),
    path("admin/user-details/<int:id>/", bv.EditDetails.as_view(), name="edit-details"),
    path("admin/buy-cash-applies/", bv.BuyCashApplies.as_view(), name="buy_cash_applies"),
    path("admin/reports/", bv.Reports.as_view(), name="reports"),

    # function base operation
    path("admin/payment-approve/<int:id>/", bv.approve_payment, name="approve_payment"),
    path("admin/payment-disapprove/<int:id>/", bv.disapprove_payment, name="disapprove_payment"),
    path("admin/cash-out-approve/<int:id>/", bv.cash_out_request_approve, name="cash_out_approve"),
    path("admin/cash-out-refuse/<int:id>/", bv.cash_out_request_refuse, name="cash_out_refuse"),
    path("admin/approve-buying-from-host/<int:id>/", bv.approve_buying_from_host, name="approve_buying_host"),
    path("admin/disapprove-buying-from-host/<int:id>/", bv.disapprove_buying_from_host, name="disapprove_buying_host"),
]
