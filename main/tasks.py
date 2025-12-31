from celery import shared_task, group
import logging
from datetime import datetime, timedelta, date
from .models import *
from .api import *
import time
import pytz
from django.db import transaction
from datetime import datetime
from django.contrib.auth import get_user_model

# UPS = update_player_history
timezone = pytz.timezone('America/New_York')  # Replace with your desired time zone

# Set up logging
logger = logging.getLogger(__name__)

@shared_task
def get_clan_war_status():
    """Runs once every 46 hours"""
    clans = GlobalClan.objects.all()
    for clan in clans:
        clan = clean_tag(str(clan))
        war_info = get_clan_war_information(clan)
        if not (war_info == {'reason': 'accessDenied'} or war_info["state"] == 'notInWar'):
            target_time = datetime.strptime(war_info["endTime"], "%Y%m%dT%H%M%S.%fZ")
            scheduled_time_1 = target_time - timedelta(seconds=15)
            scheduled_time_2 = target_time + timedelta(minutes=4)

            fetch_war_info.apply_async(
                args=[clan, 1],
                eta=scheduled_time_1
            )
            fetch_war_info.apply_async(
                args=[clan, 2],
                eta=scheduled_time_2
            )
        
@shared_task
def fetch_war_info(clan_tag, time):
    """Runs based on get_clan_war_status"""
    clan_tag = clean_tag(clan_tag)
    war_info = get_clan_war_information(clan_tag)
    point_fetched = "-15"

    # change the second == to != 
    if war_info == {'reason': 'accessDenied'} or (war_info["state"] != 'warEnded' and time == 2):
        return  
    
    if time == 2:
        point_fetched = "+4"
        recent_instance = ClanWarInformation.objects.latest('id')
        recent_instance.delete()

    clan, created = GlobalClan.objects.get_or_create(clan_tag=clan_tag)
    current_time = str(datetime.now().strftime("%H-%M-%S"))
    ClanWarInformation.objects.create(clan=clan, war_info=war_info, current_time=current_time, point_fetched=point_fetched)
    # print(war_info)

    date_started = war_info["preparationStartTime"]
    converted_date = datetime.strptime(date_started, '%Y%m%dT%H%M%S.000Z').date()

    clan_name = war_info["clan"]["name"]

    for player in war_info["clan"]["members"]:
        player_tag = clean_tag(player["tag"])
        player_info, created = GlobalPlayer.objects.get_or_create(player_tag=player_tag)
        roster_number = player["mapPosition"]

        num_attacks = 0
        num_missed_attacks = 0
        attack_1_stars = 0
        attack_1_destruction = 0
        attack_2_stars = 0
        attack_2_destruction = 0

        try:
            num_attacks = len(player["attacks"])
            attack_1_stars = player["attacks"][0]["stars"]
            attack_1_destruction = player["attacks"][0]["destructionPercentage"]
            attack_2_stars = player["attacks"][1]["stars"]
            attack_2_destruction = player["attacks"][1]["destructionPercentage"]
        except KeyError:
            pass
        except IndexError:
            pass
        num_missed_attacks = war_info["attacksPerMember"] - num_attacks

        PlayerWarInformation.objects.create(player=player_info, date_started=converted_date, clan_name=clan_name, clan_tag=clan_tag,
                                            roster_number=roster_number, num_attacks=num_attacks, attack_1_stars=attack_1_stars, num_missed_attacks=num_missed_attacks,
                                            attack_1_destruction=attack_1_destruction, attack_2_stars=attack_2_stars, attack_2_destruction=attack_2_destruction)

    num_wars = 0
    num_wins = 0
    num_losses = 0
    num_draws = 0
    total_players = 0
    total_stars = 0
    total_destruction = 0

    average_war_size = 0
    average_total_stars = 0
    average_stars_per_player = 0
    average_total_destruction = 0
    win_rate = 0
    percent_attacks_completed = 0

    num_attacks_completed = 0
    num_total_attacks = 0

    current_date = datetime(2025, 1, 3)
    current_time = datetime.now().strftime('%H:%M:%S')  # this is temporary

    if current_date.month == 1:
        # If it's January, go to December of the previous year
        previous_month = 12
        year = current_date.year - 1
    else:
        # Otherwise, just subtract one month
        previous_month = current_date.month - 1
        year = current_date.year

    # Create a new datetime object for the previous month with the same day (1st of the previous month)
    previous_date = datetime(year, previous_month, 1)

    for i, war in enumerate(reversed(clan.war_information.all())):
        if not (war.war_info == {'reason': 'accessDenied'} or war.war_info.get('state') == 'notInWar') :
            start_time = war.war_info["preparationStartTime"]
            date_obj = datetime.strptime(start_time, "%Y%m%dT%H%M%S.%fZ")

            year = date_obj.year
            month = date_obj.month
            num_wars += 1
            total_players += len(war.war_info["clan"]["members"])
            total_stars += war.war_info["clan"]["stars"]
            total_destruction += war.war_info["clan"]["destructionPercentage"]

            num_attacks_completed += war.war_info["clan"]["attacks"]
            num_total_attacks += war.war_info["attacksPerMember"] * total_players

            clan_stars = war.war_info["clan"]["stars"]
            clan_destruction = war.war_info["clan"]["destructionPercentage"]
            opponent_stars = war.war_info["opponent"]["stars"]
            opponent_destruction = war.war_info["opponent"]["destructionPercentage"]  
            
            if clan_stars > opponent_stars or clan_stars == opponent_stars and clan_destruction > opponent_destruction:
                num_wins += 1
            elif clan_stars < opponent_stars or clan_stars == opponent_stars and clan_destruction < opponent_destruction:
                num_losses += 1
            else:
                num_draws += 1
            if i == 4:
                break
        
    try:
        average_war_size = total_players / num_wars
        average_total_stars = total_stars / num_wars
        average_stars_per_player = average_total_stars / average_war_size
        average_total_destruction = total_destruction / num_wars

        win_rate = num_wins / num_wars
        percent_attacks_completed = num_attacks_completed / num_total_attacks
    except ZeroDivisionError:
        pass

    ClanLastFiveWars.objects.filter(clan=clan).delete()

    ClanLastFiveWars.objects.create(
        clan=clan,  # Match based on the clan
        num_wars=num_wars,
        num_wins=num_wins,
        num_losses=num_losses,
        num_draws=num_draws,
        total_players=total_players,
        total_stars=total_stars,
        total_destruction=total_destruction,
        average_war_size=average_war_size,
        average_total_stars=average_total_stars,
        average_stars_per_player=average_stars_per_player,
        average_total_destruction=average_total_destruction,
        month_year=previous_date,
        percent_attacks_completed=percent_attacks_completed,
        win_rate=win_rate,
        current_time=current_time
    )
    
    clan_general_info = get_all_clan_data(clan)
    members = clan_general_info["memberList"]
    clan_name = clan_general_info["name"]
    clan_tag = clean_tag(clan_general_info["tag"])
    
    for member in members:
        num_wars = 0
        num_attacks = 0
        num_missed_attacks = 0
        total_stars = 0
        total_destruction = 0
        average_total_stars = 0
        average_total_destruction = 0


        player_tag = clean_tag(member["tag"])
        player, created = GlobalPlayer.objects.get_or_create(player_tag=player_tag)
        for war in reversed(player.war_information.all()):
            start_time = str(war.date_started)
            year = int(start_time[0:4])
            month = int(start_time[5:7])

            if war.clan_tag == clan_tag:
                if year == current_date.year and month == current_date.month:
                    continue
                elif (year == previous_date.year and month == previous_date.month):
                    num_wars += 1
                    num_attacks += war.num_attacks
                    num_missed_attacks += war.num_missed_attacks
                    total_stars += war.attack_1_stars + war.attack_2_stars
                    total_destruction += war.attack_1_destruction + war.attack_2_destruction
                else:
                    break
        try: 
            average_total_stars = total_stars / num_wars
            average_total_destruction = total_destruction / num_wars
        except ZeroDivisionError:
            pass
        PlayerLastFiveWars.objects.filter(player=player).delete()
        PlayerLastFiveWars.objects.create(player=player, clan_name=clan_name, clan_tag=clan_tag, 
                                            current_time=current_time, month_year=previous_date,
                                            num_wars=num_wars, num_attacks=num_attacks, num_missed_attacks=num_missed_attacks,
                                            total_stars=total_stars, total_destruction=total_destruction, average_total_stars=average_total_stars, average_total_destruction=average_total_destruction)

@shared_task
def get_monthly_clan_war_info():
    """Runs on the 3rd of each month"""
    print("here")
    clans = GlobalClan.objects.all()
    current_date = datetime(2025, 1, 3)
    current_time = datetime.now().strftime('%H:%M:%S')  # this is temporary

    if current_date.month == 1:
        # If it's January, go to December of the previous year
        previous_month = 12
        year = current_date.year - 1
    else:
        # Otherwise, just subtract one month
        previous_month = current_date.month - 1
        year = current_date.year

    # Create a new datetime object for the previous month with the same day (1st of the previous month)
    previous_date = datetime(year, previous_month, 1)

    for clan in clans:
        num_wars = 0
        num_wins = 0
        num_losses = 0
        num_draws = 0
        total_players = 0
        total_stars = 0
        total_destruction = 0

        average_war_size = 0
        average_total_stars = 0
        average_stars_per_player = 0
        average_total_destruction = 0
        win_rate = 0
        percent_attacks_completed = 0

        num_attacks_completed = 0
        num_total_attacks = 0


        for war in reversed(clan.war_information.all()):
            if not (war.war_info == {'reason': 'accessDenied'} or war.war_info.get('state') == 'notInWar') :
                start_time = war.war_info["preparationStartTime"]
                date_obj = datetime.strptime(start_time, "%Y%m%dT%H%M%S.%fZ")

                year = date_obj.year
                month = date_obj.month

                if year == current_date.year and month == current_date.month:
                    continue
                elif (year == previous_date.year and month == previous_date.month):
                    num_wars += 1
                    total_players += len(war.war_info["clan"]["members"])
                    total_stars += war.war_info["clan"]["stars"]
                    total_destruction += war.war_info["clan"]["destructionPercentage"]

                    num_attacks_completed += war.war_info["clan"]["attacks"]
                    num_total_attacks += war.war_info["attacksPerMember"] * total_players

                    clan_stars = war.war_info["clan"]["stars"]
                    clan_destruction = war.war_info["clan"]["destructionPercentage"]
                    opponent_stars = war.war_info["opponent"]["stars"]
                    opponent_destruction = war.war_info["opponent"]["destructionPercentage"]  
                    
                    if clan_stars > opponent_stars or clan_stars == opponent_stars and clan_destruction > opponent_destruction:
                        num_wins += 1
                    elif clan_stars < opponent_stars or clan_stars == opponent_stars and clan_destruction < opponent_destruction:
                        num_losses += 1
                    else:
                        num_draws += 1
                else:
                    break
            
        try:
            average_war_size = total_players / num_wars
            average_total_stars = total_stars / num_wars
            average_stars_per_player = average_total_stars / average_war_size
            average_total_destruction = total_destruction / num_wars

            win_rate = num_wins / num_wars
            percent_attacks_completed = num_attacks_completed / num_total_attacks
        except ZeroDivisionError:
            pass

        ClanMonthlyDataWar.objects.create(
            clan=clan,  # Match based on the clan
            num_wars=num_wars,
            num_wins=num_wins,
            num_losses=num_losses,
            num_draws=num_draws,
            total_players=total_players,
            total_stars=total_stars,
            total_destruction=total_destruction,
            average_war_size=average_war_size,
            average_total_stars=average_total_stars,
            average_stars_per_player=average_stars_per_player,
            average_total_destruction=average_total_destruction,
            month_year=previous_date,
            percent_attacks_completed=percent_attacks_completed,
            win_rate=win_rate,
            current_time=current_time
        )
        
        clan_general_info = get_all_clan_data(clan)
        members = clan_general_info["memberList"]
        clan_name = clan_general_info["name"]
        clan_tag = clean_tag(clan_general_info["tag"])
        
        for member in members:
            num_wars = 0
            num_attacks = 0
            num_missed_attacks = 0
            total_stars = 0
            total_destruction = 0
            average_total_stars = 0
            average_total_destruction = 0


            player_tag = clean_tag(member["tag"])
            player, created = GlobalPlayer.objects.get_or_create(player_tag=player_tag)
            for war in reversed(player.war_information.all()):
                start_time = str(war.date_started)
                year = int(start_time[0:4])
                month = int(start_time[5:7])

                if war.clan_tag == clan_tag:
                    if year == current_date.year and month == current_date.month:
                        continue
                    elif (year == previous_date.year and month == previous_date.month):
                        num_wars += 1
                        num_attacks += war.num_attacks
                        num_missed_attacks += war.num_missed_attacks
                        total_stars += war.attack_1_stars + war.attack_2_stars
                        total_destruction += war.attack_1_destruction + war.attack_2_destruction
                    else:
                        break
            try: 
                average_total_stars = total_stars / num_wars
                average_total_destruction = total_destruction / num_wars
            except ZeroDivisionError:
                pass
            PlayerMonthlyDataWar.objects.create(player=player, clan_name=clan_name, clan_tag=clan_tag, 
                                                current_time=current_time, month_year=previous_date,
                                                num_wars=num_wars, num_attacks=num_attacks, num_missed_attacks=num_missed_attacks,
                                                total_stars=total_stars, total_destruction=total_destruction, average_total_stars=average_total_stars, average_total_destruction=average_total_destruction)

@shared_task
def get_monthly_clan_general_info():
    """Runs with end_of_trophy_season_updates on the last Sunday of each month"""
    clans = GlobalClan.objects.all()
    for clan in clans:
        data = get_all_clan_data(clean_tag(str(clan)))
        day_fetched = datetime.now() 
        if day_fetched.day <= 7:
            month_year = (day_fetched.replace(day=1) - timedelta(days=1)).replace(day=1)
        else:
            month_year = day_fetched.replace(day=1)
        time_fetched = datetime.now().time()
        # print(clan)
        ClanMonthlyDataGeneral.objects.create(clan=clan, data=data, day_fetched=day_fetched, month_year=month_year, time_fetched=time_fetched)

@shared_task
def update_players_being_tracked():
    """Runs with end_of_trophy_season_updates on the last Sunday of each month"""
    clans = GlobalClan.objects.all()
    print('hi')
    for clan in clans:
        clan_general_info = get_all_clan_data(clan)
        members = clan_general_info["memberList"]
        for member in members:
            player_tag = clean_tag(member["tag"])
            GlobalPlayer.objects.get_or_create(player_tag=player_tag)

@shared_task
def update_player_history():
    """Runs with end_of_trophy_season_updates on the last Sunday of each month"""
    try:
        tags = GlobalPlayer.objects.values_list('player_tag', flat=True)
        
        # Split tags into chunks of 10
        chunk_size = 10
        tag_chunks = [tags[i:i + chunk_size] for i in range(0, len(tags), chunk_size)]

        for chunk in tag_chunks:
            for tag in chunk:
                try:
                    time_fetched = datetime.now().time()
                    # Process single tag
                    player, created = GlobalPlayer.objects.get_or_create(player_tag=clean_tag(tag))
                    day_fetched = datetime.now()
                    
                    # Determine month-year
                    if day_fetched.day <= 7:
                        month_year = (day_fetched.replace(day=1) - timedelta(days=1)).replace(day=1)
                    else:
                        month_year = day_fetched.replace(day=1)
                    
                    # Get player data
                    data = get_all_player_data(tag)

                    # Save player data in transaction
                    with transaction.atomic():
                        PlayerMonthlyData.objects.create(
                            player=player,
                            data=data,
                            day_fetched=day_fetched,
                            month_year=month_year,
                            time_fetched=time_fetched,
                        )
                except Exception as e:
                    logger.error(f"Error processing tag {tag}: {e}")

    except Exception as e:
        logger.error(f"Error updating player history: {e}")

@shared_task
def end_of_trophy_season_updates():
    """Will run on the last Sunday of each month"""
    update_players_being_tracked()
    get_monthly_clan_general_info()
    update_player_history()

@shared_task
def get_CWL_war_tags(day):
    """Run on the 4th through 10th day of each month"""
    if day == 4:
        clans = GlobalClan.objects.all()
        for clan in clans:
            CWLGlobalClan.objects.create(clan_tag=str(clan))
    clans = CWLGlobalClan.objects.all()

    current_date = datetime.now()
    month_year = current_date.strftime("%m_%Y")


    dont_include_daily = set()
    dont_include_at_all = set()

    for clan in clans:
        if clean_tag(clan.clan_tag) not in dont_include_daily:
            try:
                group_info = get_CWL_group_information(clan.clan_tag)
                league = get_clan_data(clean_tag(clan.clan_tag))["warLeague"]["name"]

                clan_tags = {clean_tag(clan_["tag"]) for clan_ in group_info["clans"]}  # Use a set for unique tags
                dont_include_daily.update(clan_tags)  # Add all tags to dont_include in one operation
                
                if group_info["rounds"][-1]["warTags"][-1] != "#0":
                    CWLGroupData.objects.create(group_data=group_info, month_year=month_year, league=league)
                    dont_include_at_all.update(clan_tags)
            except KeyError:
                continue
        
    CWLGlobalClan.objects.filter(clan_tag__in=dont_include_at_all).delete()

    if day == 10:
        CWLGlobalClan.objects.all().delete()


class WarInfo:
    def __init__(self, member_data, name, tag="", stars=0, percent=0):
        self.tag = tag
        self.stars = stars
        self.name = name
        self.percent = percent
        self.wars = []  # Initialize an empty list to store wars
        self.member_data = member_data

@shared_task
def process_CWL_information():
    """Run on the 12th of each month"""
    all_info = CWLGroupData.objects.all()
    time1 = time.perf_counter()

    for data in all_info:
        war_info_dict = {}  # Create an empty dictionary to store WarInfo instances

        # Initialize WarInfo instances for each clan
        for clan in data.group_data["clans"]:
            tag = clean_tag(clan["tag"])
            member_data = {}
            for member in clan["members"]:
                member_data[clean_tag(member["tag"])] = {"warsIn": 0, "attacks": 0, "stars": 0, "percent": 0, "townHall": member["townHallLevel"], "name": member["name"]}

            war_info_dict[tag] = WarInfo(tag=tag, member_data=member_data, name=clan["name"])

        # Process each day's war data
        for day in data.group_data["rounds"]:
            for war_tag in day["warTags"]:
                war_info = get_CWL_war_information(clean_tag(war_tag))
                clan_tag = clean_tag(war_info["clan"]["tag"])
                opponent_tag = clean_tag(war_info["opponent"]["tag"])

                # Only append the war if it hasn't already been added
                if war_info not in war_info_dict[clan_tag].wars:
                    war_info_dict[clan_tag].wars.append(war_info)
                if war_info not in war_info_dict[opponent_tag].wars:
                    war_info_dict[opponent_tag].wars.append(war_info)

                # Update stars and destruction percentage for both clans
                for persp in ["clan", "opponent"]:
                    war_info_dict[clean_tag(war_info[persp]["tag"])].stars += war_info[persp]["stars"]
                    war_info_dict[clean_tag(war_info[persp]["tag"])].percent += war_info[persp]["destructionPercentage"] * war_info["teamSize"]

                # Add bonus stars based on performance
                if war_info["clan"]["stars"] > war_info["opponent"]["stars"] or war_info["clan"]["destructionPercentage"] > war_info["opponent"]["destructionPercentage"]:
                    war_info_dict[clean_tag(war_info["clan"]["tag"])].stars += 10
                elif war_info["opponent"]["stars"] > war_info["clan"]["stars"] or war_info["opponent"]["destructionPercentage"] > war_info["clan"]["destructionPercentage"]:
                    war_info_dict[clean_tag(war_info["opponent"]["tag"])].stars += 10

        sorted_war_info = sorted(
            war_info_dict.items(),
            key=lambda item: (item[1].stars, item[1].percent),
            reverse=True  # Sort both stars and percent in descending order
        )
        general_info = []
        for i, clan in enumerate(sorted_war_info):
            general_info.append({"placement": i + 1, "stars": clan[1].stars, "tag": clan[0], "percent": clan[1].percent, "name": clan[1].name})
        # Output the results for each clan
        for tag, war_info in war_info_dict.items():
            for war in war_info.wars:
                if tag == clean_tag(war["clan"]["tag"]):
                    persp = "clan"
                else:
                    persp = "opponent"
                for member in war[persp]["members"]:
                    cleaned_member = war_info.member_data[clean_tag(member["tag"])]
                    # print(cleaned_member, clean_tag(member["tag"]))
                    cleaned_member["warsIn"] += 1
                    try:
                        attack = member["attacks"][0]
                        cleaned_member["attacks"] += 1
                        cleaned_member["stars"] += attack["stars"]
                        cleaned_member["percent"] += attack["destructionPercentage"]
                    except KeyError:
                        continue

            for clan in general_info:
                if clan['tag'] == tag:
                    placement = clan['placement']
                    stars = clan["stars"]
                    percent = clan["percent"]
            
            clan, created = GlobalClan.objects.get_or_create(clan_tag=clean_tag(tag))           
            ClanCWLInformation.objects.create(clan=clan, stars=stars, percent=percent, placement=int(placement), all_clan_placement=general_info, each_war_data=war_info.wars, member_data=war_info.member_data, month_year=data.month_year, league=data.league)
    
        

@shared_task
def delete_all_CWL_group_info():
    """Runs on the 20th of each month"""
    CWLGroupData.objects.all().delete()

@shared_task
def test_task():
    User = get_user_model()  # Get the user model
    user = User.objects.get(username="Ranntern")  # Find user by username
    user.username = "NewNewNewNameNameName"  # Update username
    user.save()  

