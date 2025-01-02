from django import template
import pytz
from datetime import datetime, date
from main.api import clean_tag
from main.models import PlayerMonthlyData, GlobalPlayer

register = template.Library()

@register.filter
def replace_space_with_underscore(value):
    return value.replace(" ", "_")

@register.filter
def get_max_level_previous_TH(hero, town_hall):
    if hero == "Barbarian King":
        th_level = {7: 0, 8: 10, 9:20, 10:30, 11:40, 12:50, 13:65, 14:75, 15:80, 16:90, 17:95}
        return th_level.get(town_hall, 0)  # Default value is 0 if town_hall is not 10, 11, or 12
    elif hero == "Archer Queen":
        th_level = {8: 0, 9:10, 10:30, 11:40, 12:50, 13:65, 14:75, 15:80, 16:90, 17:95}
        return th_level.get(town_hall, 0)  # Default value is 0 if town_hall is not 10, 11, or 12
    elif hero == "Minion Prince":
        th_level = {9:0, 10:10, 11:20, 12:30, 13:40, 14:50, 15:60, 16:70, 17:80}
        return th_level.get(town_hall, 0)  # Default value is 0 if town_hall is not 10, 11, or 12
    elif hero == "Grand Warden":
        th_level = {11:0, 12:20, 13:40, 14:50, 15:55, 16:65, 17:70}
        return th_level.get(town_hall, 0)  # Default value is 0 if town_hall is not 10, 11, or 12
    elif hero == "Royal Champion":
        th_level = {13:0, 14:25, 15:30, 16:40, 17:45}
        return th_level.get(town_hall, 0)  # Default value is 0 if town_hall is not 10, 11, or 12
    elif hero == "Battle Machine":
        th_level = {5:0, 6:5, 7:10, 8:20, 9:25, 10:30, 11:35}
        return th_level.get(town_hall, 0)  # Default value is 0 if town_hall is not 10, 11, or 12
    elif hero == "Battle Copter":
        th_level = {8:15, 9:25, 10:30, 11:35}
        return th_level.get(town_hall, 0)  # Default value is 0 if town_hall is not 10, 11, or 12


@register.filter
def get_max_level_current_TH(hero, town_hall):
    if hero == "Barbarian King":
        th_level = {7: 0, 8: 10, 9:20, 10:30, 11:40, 12:50, 13:65, 14:75, 15:80, 16:90, 17:95, 18:100}
        return th_level.get(town_hall + 1, 0)  # Default value is 0 if town_hall is not 10, 11, or 12
    elif hero == "Archer Queen":
        th_level = {8: 0, 9:10, 10:30, 11:40, 12:50, 13:65, 14:75, 15:80, 16:90, 17:95, 18:100}
        return th_level.get(town_hall + 1, 0)  # Default value is 0 if town_hall is not 10, 11, or 12
    elif hero == "Minion Prince":
        th_level = {9:0, 10:10, 11:20, 12:30, 13:40, 14:50, 15:60, 16:70, 17:80, 18:90}
        return th_level.get(town_hall + 1, 0)  # Default value is 0 if town_hall is not 10, 11, or 12
    elif hero == "Grand Warden":
        th_level = {11:0, 12:20, 13:40, 14:50, 15:55, 16:65, 17:70, 18:75}
        return th_level.get(town_hall + 1, 0)  # Default value is 0 if town_hall is not 10, 11, or 12
    elif hero == "Royal Champion":
        th_level = {13:0, 14:25, 15:30, 16:40, 17:45, 18:50}
        return th_level.get(town_hall + 1, 0)  # Default value is 0 if town_hall is not 10, 11, or 12
    elif hero == "Battle Machine":
        th_level = {5:0, 6:5, 7:10, 8:20, 9:25, 10:30, 11:35}
        return th_level.get(town_hall + 1, 0)  # Default value is 0 if town_hall is not 10, 11, or 12
    elif hero == "Battle Copter":
        th_level = {8:15, 9:25, 10:30, 11:35}
        return th_level.get(town_hall + 1, 0)  # Default value is 0 if town_hall is not 10, 11, or 12


    return town_hall

@register.filter
def equipment_to_hero(equipment):
    if equipment in ["Barbarian Puppet", "Rage Vial", "Earthquake Boots", "Vampstache", "Giant Gauntlet", "Spiky Ball"]:
        return "Barbarian King"
    elif equipment in ["Archer Puppet", "Invisibility Vial", "Giant Arrow", "Healer Puppet", "Frozen Arrow", "Magic Mirror"]:
        return "Archer Queen"
    elif equipment in ["Henchmen Puppet", "Dark Orb"]:
        return "Minion Prince"
    elif equipment in ["Eternal Tome", "Life Gem", "Rage Gem", "Healing Tome", "Fireball", "Lavaloon Puppet"]:
        return "Grand Warden"
    elif equipment in ["Royal Gem", "Seeking Shield", "Hog Rider Puppet", "Haste Vial", "Rocket Spear", "Electro Boots"]:
        return "Royal Champion"
    return "New equipment - not yet configured"

@register.filter
def check_in_use_1(equipment, player):
    """Returns a string (yes or no)"""
    for hero in player["heroes"]:
        try:
            for hero_equipment in hero["equipment"]:
                if equipment == hero_equipment["name"]:
                    return "Yes"
        except KeyError:
            pass
    return "No"

@register.filter
def check_in_use_2(equipment, player):
    """This returns a bool (True or False)"""
    for hero in player["heroes"]:
        try:
            for hero_equipment in hero["equipment"]:
                if equipment == hero_equipment["name"]:
                    return True
        except KeyError:
            pass
    return False

@register.filter
def not_in(value, arg):
    return value not in arg.split(',')

@register.filter
def does_not_start_with(value, arg):
    """Returns True if the value does not start with the provided argument."""
    return not value.startswith(arg)

@register.filter
def is_in_list(value, arg):
    """Returns True if the value is in the provided list."""
    return value in arg

@register.filter
def filter_from_lassi(troops):
    # Start filtering from "L.A.S.S.I"
    start = False
    filtered_troops = []
    for troop in troops:
        if troop['name'] == "L.A.S.S.I":
            start = True
        if start:
            filtered_troops.append(troop)
    return filtered_troops

@register.filter
def filter_until_lassi(troops):
    # Start collecting troops up until "L.A.S.S.I"
    stop = False
    filtered_troops = []
    for troop in troops:
        if troop['name'] == "L.A.S.S.I":
            stop = True
            break  # Stop before adding "L.A.S.S.I"
        filtered_troops.append(troop)
    return filtered_troops

def get_day_with_ordinal(day):
    if 11 <= day % 100 <= 13:  # Handle special cases for 11th, 12th, 13th
        suffix = "th"
    else:
        suffix = {1: "st", 2: "nd", 3: "rd"}.get(day % 10, "th")
    return f"{day}{suffix}"

@register.simple_tag
def format_date(month, day, year):
    try:
        # Convert month number to full month name
        month_names = {
            1: "January", 2: "February", 3: "March", 4: "April",
            5: "May", 6: "June", 7: "July", 8: "August",
            9: "September", 10: "October", 11: "November", 12: "December"
        }
        month_name = month_names[month]
        # Add ordinal suffix to the day
        formatted_day = get_day_with_ordinal(int(day))
        # Return formatted date
        return f"{month_name} {formatted_day}, {year}"
    except (ValueError, AttributeError, KeyError):
        return f"{month}/{day}/{year}"  # Default format if something goes wrong
    
@register.simple_tag
def format_time(hour, minute):
    try:
        str_hour = str(hour)
        str_minute = str(minute)
        AM_PM = "A.M."
        if hour > 12:
            AM_PM = "P.M."
            str_hour = str(hour - 12)
        if hour == 0:
            str_hour = "12"
        if minute < 10:
            str_minute = f"0{str(minute)}"
        return f"{str_hour}:{str_minute} {AM_PM} "
    except:
        return None

@register.filter(name='convert_to_est')
def convert_to_est(value):
    try:
        # Parse the timestamp string into a datetime object
        dt = datetime.strptime(value, '%Y%m%dT%H%M%S.%fZ')

        # Localize to UTC first
        utc_zone = pytz.utc
        dt_utc = pytz.utc.localize(dt)

        # Convert to Eastern Standard Time (EST)
        est_zone = pytz.timezone('US/Eastern')
        dt_est = dt_utc.astimezone(est_zone)

        # Return the formatted time
        return dt_est.strftime('%B %d, %Y %I:%M %p EST')
    except Exception as e:
        return value  # Return the original value if there's an error
    
@register.filter
def mul(value, arg):
    try:
        return float(value) * float(arg)
    except (ValueError, TypeError):
        return ''
    
@register.filter
def first_element(value):
    """Returns the first element of a list or None if the list is empty."""
    if isinstance(value, list) and value:
        return value[0]
    return None

@register.simple_tag
def clan_type_display(clan_type):
    if clan_type == "open":
        return "Open"
    elif clan_type == "closed":
        return "Closed"
    else:
        return "Invite Only"
    
@register.simple_tag
def war_frequency_display(war_frequency):
    war_frequency_map = {
        "always": "Always",
        "never": "Never",
        "onceAWeek": "Once a Week",
        "twiceAWeek": "Twice a Week",
        "unknown": "Not Set",
        "rarely": "Rarely",
    }
    return war_frequency_map.get(war_frequency, f"Not found: {war_frequency}")

@register.filter
def extract_day(value):
    if isinstance(value, (date, datetime)):
        return value.day  # Directly return the day for date or datetime
    try:
        # Parse if it's a string
        date_obj = datetime.strptime(value, "%b. %d, %Y")
        return date_obj.day
    except (ValueError, TypeError):
        return None
    
@register.filter
def convert_date_to_month_year(date_obj):
    """
    Convert a datetime.date object to "Month Year" format.
    """
    return date_obj.strftime("%B %Y")

@register.simple_tag
def role_display(role):
    role_map = {
        "leader": "Leader",
        "coLeader": "Co-Leader",
        "admin": "Elder",
        "member": "Member",
    }
    return role_map.get(role, role) 

@register.filter
def break_loop(value, arg):
    if value == arg:
        raise StopIteration
    return value

@register.filter
def sort_equipment(equipment, player):
    hero_order = ["Barbarian King", "Archer Queen", "Minion Prince", "Grand Warden", "Royal Champion"]
    equipment.sort(key=lambda x: (hero_order.index(equipment_to_hero(x["name"])), not check_in_use_2(x["name"], player)))
    return equipment

@register.filter
def last_item(queryset):
    """
    Returns the last item in a queryset or list.
    """
    if queryset:
        return queryset[-1]  # Get the last item
    return None

@register.filter
def format_email(email, email_level):
    if not email:
        return "None"

    # Split the email into local part and domain
    local, domain = email.split('@')
    
    # Keep the first 3 characters of the local part and mask the rest
    censored_local = local[:3] + '*****'
    
    # Return the censored email
    return f"{censored_local}@{domain} ({email_level})"

@register.filter
def fetch_player_name(tag):
    # Clean the tag and find the corresponding player
    data = GlobalPlayer.objects.get(player_tag=clean_tag(str(tag)))

    # Retrieve the latest monthly data for the player
    monthly_data = PlayerMonthlyData.objects.filter(player=data).last()
    return monthly_data.data["name"]
