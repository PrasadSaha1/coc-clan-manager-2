from django.db import models
from django.contrib.auth.models import User
from datetime import date, time
from django.contrib.postgres.fields import ArrayField

class SavedClan(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='saved_clans')
    clan_tag = models.CharField(max_length=20)

    def __str__(self):
        return self.clan_tag
    
class SavedPlayer(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='saved_players')
    player_tag = models.CharField(max_length=20)

    def __str__(self):
        return self.player_tag
    
class GlobalPlayer(models.Model):
    player_tag = models.CharField(max_length=20, unique=True)

    def __str__(self):
        return self.player_tag

class PlayerWarInformation(models.Model):
    player = models.ForeignKey(GlobalPlayer, on_delete=models.CASCADE, related_name='war_information')

    date_started = models.DateField()
    clan_name = models.CharField(max_length=50)
    clan_tag = models.CharField(max_length=20)
    roster_number = models.IntegerField()
    num_attacks = models.IntegerField()
    num_missed_attacks = models.IntegerField(default=0)
    attack_1_stars = models.IntegerField()
    attack_1_destruction = models.IntegerField()
    attack_2_stars = models.IntegerField()
    attack_2_destruction = models.IntegerField()

class PlayerMonthlyData(models.Model):
    player = models.ForeignKey(GlobalPlayer, on_delete=models.CASCADE, related_name='monthly_data')
    data = models.JSONField(default=list)
    month_year = models.DateField(default=date.today)
    time_fetched = models.TimeField(default=time(9, 0))  # Default is 09:00:00
    day_fetched = models.DateField(default=date.today)
   
class PlayerMonthlyDataWar(models.Model):
    """Assumes a player does not change clan"""
    player = models.ForeignKey(GlobalPlayer, on_delete=models.CASCADE, related_name='monthly_data_war')

    num_wars = models.IntegerField()
    num_attacks = models.IntegerField()
    num_missed_attacks = models.IntegerField()
    total_stars = models.IntegerField()
    total_destruction = models.IntegerField()
    average_total_stars = models.FloatField()
    average_total_destruction = models.FloatField(default=0)

    clan_name = models.CharField(default="", max_length=50)
    clan_tag = models.CharField(max_length=20, default="")
    month_year = models.DateField(default=date.today)
    current_time = models.CharField(max_length=50, default="N/A")

class GlobalClan(models.Model):
    clan_tag = models.CharField(max_length=20, unique=True)

    def __str__(self):
        return self.clan_tag

class CWLGlobalClan(models.Model):
    clan_tag = models.CharField(max_length=20, unique=True)

class ClanWarInformation(models.Model):
    clan = models.ForeignKey(GlobalClan, on_delete=models.CASCADE, related_name='war_information')
    current_time = models.CharField(default="N/A", max_length=50)
    war_info = models.JSONField(default=list)
    point_fetched = models.CharField(max_length=50, default="+4")  # +4 or -15

class ClanMonthlyDataGeneral(models.Model):
    clan = models.ForeignKey(GlobalClan, on_delete=models.CASCADE, related_name='monthly_data_general')
    data = models.JSONField(default=list)
    month_year = models.DateField(default=date.today)
    day_fetched = models.DateField(default=date.today)
    time_fetched = models.TimeField(default=time(9, 0))  # Default is 09:00:00

class ClanMonthlyDataWar(models.Model):
    clan = models.ForeignKey(GlobalClan, on_delete=models.CASCADE, related_name='monthly_data_war')

    num_wins = models.IntegerField(default=0)
    num_losses = models.IntegerField(default=0)
    num_draws = models.IntegerField(default=0)

    num_wars = models.FloatField(default=0.0)
    total_players = models.FloatField(default=0.0)
    total_stars = models.FloatField(default=0.0)
    total_destruction = models.FloatField(default=0.0)

    average_war_size = models.FloatField(default=0.0)
    average_total_stars = models.FloatField(default=0.0)
    average_stars_per_player = models.FloatField(default=0.0)
    average_total_destruction = models.FloatField(default=0.0)

    win_rate = models.FloatField(default=0.0)
    percent_attacks_completed = models.FloatField(default=0.0)

    month_year = models.DateField(default=date.today)
    current_time = models.CharField(max_length=50, default="N/A")

class ClanLastFiveWars(models.Model):
    clan = models.ForeignKey(GlobalClan, on_delete=models.CASCADE, related_name='last_five_wars')

    num_wins = models.IntegerField(default=0)
    num_losses = models.IntegerField(default=0)
    num_draws = models.IntegerField(default=0)

    num_wars = models.FloatField(default=0.0)
    total_players = models.FloatField(default=0.0)
    total_stars = models.FloatField(default=0.0)
    total_destruction = models.FloatField(default=0.0)

    average_war_size = models.FloatField(default=0.0)
    average_total_stars = models.FloatField(default=0.0)
    average_stars_per_player = models.FloatField(default=0.0)
    average_total_destruction = models.FloatField(default=0.0)

    win_rate = models.FloatField(default=0.0)
    percent_attacks_completed = models.FloatField(default=0.0)

    month_year = models.DateField(default=date.today)
    current_time = models.CharField(max_length=50, default="N/A")

class PlayerLastFiveWars(models.Model):
    """Assumes a player does not change clan"""
    player = models.ForeignKey(GlobalPlayer, on_delete=models.CASCADE, related_name='last_five_wars')

    num_wars = models.IntegerField()
    num_attacks = models.IntegerField()
    num_missed_attacks = models.IntegerField()
    total_stars = models.IntegerField()
    total_destruction = models.IntegerField()
    average_total_stars = models.FloatField()
    average_total_destruction = models.FloatField(default=0)

    clan_name = models.CharField(default="", max_length=50)
    clan_tag = models.CharField(max_length=20, default="")
    month_year = models.DateField(default=date.today)
    current_time = models.CharField(max_length=50, default="N/A")

class CWLGroupData(models.Model):
    group_data = models.JSONField(default=list)
    league = models.CharField(max_length=50, default="None")
    month_year = models.CharField(max_length=20, default="None")

class ClanCWLInformation(models.Model):
    clan = models.ForeignKey(GlobalClan, on_delete=models.CASCADE, related_name='cwl_information')
    league = models.CharField(max_length=50, default="None")
    month_year = models.CharField(max_length=20, default="None")
    
    placement = models.IntegerField(default=0)
    all_clan_placement = models.JSONField(default=list)

    stars = models.IntegerField(default=0)
    percent = models.FloatField(default=0)

    each_war_data = ArrayField(
        models.JSONField(),  # Each element in the array is a JSON object
        blank=True,
        default=list
    )

    member_data = models.JSONField(default=list)
