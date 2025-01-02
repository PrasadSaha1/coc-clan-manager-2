import requests
from main.models import *

headers = {
    "authorization": "Bearer eyJ0eXAiOiJKV1QiLCJhbGciOiJIUzUxMiIsImtpZCI6IjI4YTMxOGY3LTAwMDAtYTFlYi03ZmExLTJjNzQzM2M2Y2NhNSJ9.eyJpc3MiOiJzdXBlcmNlbGwiLCJhdWQiOiJzdXBlcmNlbGw6Z2FtZWFwaSIsImp0aSI6IjkwOWMxNmU3LTIwOTYtNDEzMy05ODAwLTk4ZjRjOWFlY2NlNCIsImlhdCI6MTczMTE4NTQ5Miwic3ViIjoiZGV2ZWxvcGVyLzYwYjgyNGZhLTBhYjUtZjZhOC04Zjk1LTFkZTY5YTVlYWFlNSIsInNjb3BlcyI6WyJjbGFzaCJdLCJsaW1pdHMiOlt7InRpZXIiOiJkZXZlbG9wZXIvc2lsdmVyIiwidHlwZSI6InRocm90dGxpbmcifSx7ImNpZHJzIjpbIjY3LjgzLjIwMi4xMzAiXSwidHlwZSI6ImNsaWVudCJ9XX0.3P1pnIYig0c_css_lu2GQ7sJ2uICw-7ysoCsZ3l7_vgibkFxRGSNuSjsfp0ghwaAVtqfXKmw9VMGEyfT9JS6lw"
}

def find_clan_with_tag(clan_tag, information=None):
    response = requests.get(f"https://api.clashofclans.com/v1/clans/%23{clan_tag}", headers=headers)
    response_json = response.json()

    #information_to_export = []
    #for info in information:
     #   information_to_export.append(response_json[info])
    return response_json

def get_clan_badge(clan_tag):
    response = requests.get(f"https://api.clashofclans.com/v1/clans/%23{clan_tag}", headers=headers)
    response_json = response.json()
    return response_json["badgeUrls"]["medium"]

def clean_tag(tag):
    return tag.replace("#", "").strip().upper()

def get_member_data(clan_tag):
    response = requests.get(f"https://api.clashofclans.com/v1/clans/%23{clan_tag}/members", headers=headers)
    response_json = response.json()
    return response_json

def get_all_clan_data(clan_tag):
    response = requests.get(f"https://api.clashofclans.com/v1/clans/%23{clan_tag}", headers=headers)
    response_json = response.json()
    return response_json

def get_all_player_data(player_tag):
    response = requests.get(f"https://api.clashofclans.com/v1/players/%23{player_tag}", headers=headers)
    response_json = response.json()
    return response_json

def get_clan_war_information(clan_tag):
    response = requests.get(f"https://api.clashofclans.com/v1/clans/%23{clan_tag}/currentwar", headers=headers)
    response_json = response.json()
    return response_json
