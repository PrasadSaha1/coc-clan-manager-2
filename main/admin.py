from django.contrib import admin
from .models import (
    SavedClan,
    SavedPlayer,
    GlobalPlayer,
    PlayerWarInformation,
    PlayerMonthlyData,
    PlayerMonthlyDataWar,
    GlobalClan,
    ClanWarInformation,
    ClanMonthlyDataGeneral,
    ClanMonthlyDataWar
)

# Registering each model individually
admin.site.register(SavedClan)
admin.site.register(SavedPlayer)
admin.site.register(GlobalPlayer)
admin.site.register(PlayerWarInformation)
admin.site.register(PlayerMonthlyData)
admin.site.register(PlayerMonthlyDataWar)
admin.site.register(GlobalClan)
admin.site.register(ClanWarInformation)
admin.site.register(ClanMonthlyDataGeneral)
admin.site.register(ClanMonthlyDataWar)