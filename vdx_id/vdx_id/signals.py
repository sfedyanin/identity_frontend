import django.dispatch


account_collected = django.dispatch.Signal(
    providing_args=["pk"])
all_paccount_accounts_collected = django.dispatch.Signal(
    providing_args=["paccount_pk"])
account_missing_host = django.dispatch.Signal(
    providing_args=["identity", "account", "platform", "server_pk"])

access_item_collected = django.dispatch.Signal(
    providing_args=["pk"])
all_access_item_memberships_collected = django.dispatch.Signal(
    providing_args=["access_item_id"])
all_platform_memberships_collected = django.dispatch.Signal(
    providing_args=["platform_pk"])

workorder_complete = django.dispatch.Signal(
    providing_args=["workorder_id"])
