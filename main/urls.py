from . import views
from django.urls import path

urlpatterns = [
    path("home/", views.home, name="home"),
    path("", views.home, name="home"),
    path("settings/", views.settings, name="settings"),
    path("add_email", views.add_email, name="add_email"),
    path("change_username", views.change_username, name="change_username"),
    path("change_password", views.change_password, name="change_password"),
    path("resend_verification_email", views.resend_verification_email, name="resend_verification_email"),
    path("logout_view", views.logout_view, name="logout_view"),
    path("delete_account", views.delete_account, name="delete_account"),
    path("clan_search", views.clan_search, name="clan_search"),
    path("my_clans", views.my_clans, name="my_clans"),
    path("toggle_save_clan/<clan_tag>/", views.toggle_save_clan, name="toggle_save_clan"),
    path("view_clan/<clan_tag>/<mode>/", views.view_clan, name="view_clan"),
    path("my_players", views.my_players, name="my_players"),
    path("toggle_save_player/<player_tag>/", views.toggle_save_player, name="toggle_save_player"),
    path("view_player/<player_tag>", views.view_player, name="view_player"),
    path("view_player_history/<player_tag>", views.view_player_history, name="view_player_history"),
    path("view_clan_general_history/<clan_tag>", views.view_clan_general_history, name="view_clan_general_history"),
    path("view_clan_war_history/<clan_tag>", views.view_clan_war_history, name="view_clan_war_history"),
    path("view_CWL_war/<clan_tag>/<month>", views.view_CWL_war, name="view_CWL_war"),
]
