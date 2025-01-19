import requests
from main.models import *
import time
from datetime import datetime

headers = {
    "authorization": "Bearer eyJ0eXAiOiJKV1QiLCJhbGciOiJIUzUxMiIsImtpZCI6IjI4YTMxOGY3LTAwMDAtYTFlYi03ZmExLTJjNzQzM2M2Y2NhNSJ9.eyJpc3MiOiJzdXBlcmNlbGwiLCJhdWQiOiJzdXBlcmNlbGw6Z2FtZWFwaSIsImp0aSI6ImE0YmQyNzcyLTBjOWMtNGRlZi04MTVhLTliNDI4MDVlZjliMiIsImlhdCI6MTczNTg1MjcwMSwic3ViIjoiZGV2ZWxvcGVyLzYwYjgyNGZhLTBhYjUtZjZhOC04Zjk1LTFkZTY5YTVlYWFlNSIsInNjb3BlcyI6WyJjbGFzaCJdLCJsaW1pdHMiOlt7InRpZXIiOiJkZXZlbG9wZXIvc2lsdmVyIiwidHlwZSI6InRocm90dGxpbmcifSx7ImNpZHJzIjpbIjQ1Ljc5LjIxOC43OSJdLCJ0eXBlIjoiY2xpZW50In1dfQ.OrnUTTTl4P6ctN7yqpqBLrrLORI1J7d0tuGgWNdxyzUtyIwK6TFYB0Up68iGhZu6zFMmzwoGPsLOQ8tF76HooQ"
}

def get_CWL_war_tags(day):
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


def process_CWL_information():
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
    
        
    print(time.perf_counter() - time1)

def find_clan_with_tag(clan_tag, information):
    response = requests.get(f"https://cocproxy.royaleapi.dev/v1/clans/%23{clan_tag}", headers=headers)
    response_json = response.json()

    information_to_export = []
    for info in information:
        information_to_export.append(response_json[info])
    return information_to_export

def get_clan_data(clan_tag):
    response = requests.get(f"https://cocproxy.royaleapi.dev/v1/clans/%23{clan_tag}", headers=headers)
    response_json = response.json()
    return response_json

def get_clan_badge(clan_tag):
    response = requests.get(f"https://cocproxy.royaleapi.dev/v1/clans/%23{clan_tag}", headers=headers)
    response_json = response.json()
    return response_json["badgeUrls"]["medium"]

def clean_tag(tag):
    return tag.replace("#", "").strip().upper()

def get_member_data(clan_tag):
    response = requests.get(f"https://cocproxy.royaleapi.dev/v1/clans/%23{clan_tag}/members", headers=headers)
    response_json = response.json()
    return response_json

def get_all_clan_data(clan_tag):
    response = requests.get(f"https://cocproxy.royaleapi.dev/v1/clans/%23{clan_tag}", headers=headers)
    response_json = response.json()
    return response_json

def get_all_player_data(player_tag):
    response = requests.get(f"https://cocproxy.royaleapi.dev/v1/players/%23{player_tag}", headers=headers)
    response_json = response.json()
    return response_json

def get_clan_war_information(clan_tag):
    response = requests.get(f"https://cocproxy.royaleapi.dev/v1/clans/%23{clan_tag}/currentwar", headers=headers)
    response_json = response.json()
    return response_json

def get_CWL_group_information(clan_tag):
    response = requests.get(f"https://cocproxy.royaleapi.dev/v1/clans/%23{clan_tag}/currentwar/leaguegroup", headers=headers)
    response_json = response.json()
    return response_json

def get_CWL_war_information(war_tag):
    response = requests.get(f"https://cocproxy.royaleapi.dev/v1/clanwarleagues/wars/%23{war_tag}", headers=headers)
    response_json = response.json()
    return response_json