import requests
from main.models import *
import time
from datetime import datetime

headers = {
    "authorization": "Bearer eyJ0eXAiOiJKV1QiLCJhbGciOiJIUzUxMiIsImtpZCI6IjI4YTMxOGY3LTAwMDAtYTFlYi03ZmExLTJjNzQzM2M2Y2NhNSJ9.eyJpc3MiOiJzdXBlcmNlbGwiLCJhdWQiOiJzdXBlcmNlbGw6Z2FtZWFwaSIsImp0aSI6ImE0YmQyNzcyLTBjOWMtNGRlZi04MTVhLTliNDI4MDVlZjliMiIsImlhdCI6MTczNTg1MjcwMSwic3ViIjoiZGV2ZWxvcGVyLzYwYjgyNGZhLTBhYjUtZjZhOC04Zjk1LTFkZTY5YTVlYWFlNSIsInNjb3BlcyI6WyJjbGFzaCJdLCJsaW1pdHMiOlt7InRpZXIiOiJkZXZlbG9wZXIvc2lsdmVyIiwidHlwZSI6InRocm90dGxpbmcifSx7ImNpZHJzIjpbIjQ1Ljc5LjIxOC43OSJdLCJ0eXBlIjoiY2xpZW50In1dfQ.OrnUTTTl4P6ctN7yqpqBLrrLORI1J7d0tuGgWNdxyzUtyIwK6TFYB0Up68iGhZu6zFMmzwoGPsLOQ8tF76HooQ"
}


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