import requests
import datetime
from datetime import datetime
import time

def get_puuid(game_tag, tag_line, api_key):
    # get the puuid
    get_puuid_url = str.format("https://americas.api.riotgames.com/riot/account/v1/accounts/by-riot-id/{0}/{1}?api_key={2}",
                               game_tag, tag_line, api_key)
    puuid_response_dict = get_response_json(get_puuid_url)
    return puuid_response_dict.get("puuid")


def get_last_match(puuid, api_key):
    get_match_url = str.format("https://americas.api.riotgames.com/lol/match/v5/matches/by-puuid/{0}/ids?start=0&count=20&api_key={1}", puuid,
               api_key)
    match_response = requests.get(get_match_url)
    match_response_dict = match_response.json()
    return match_response_dict[0]


def get_matches(puuid, api_key, num_matches):
    get_match_url = str.format(
        "https://americas.api.riotgames.com/lol/match/v5/matches/by-puuid/{0}/ids?start=0&count={1}&api_key={2}", puuid,
        num_matches,
        api_key)
    match_response = requests.get(get_match_url)
    match_response_list = match_response.json()

    return match_response_list


def get_matches_ux(matches, puuid, api_key):
    matches_dict = {}
    for match in matches:
        match_id = match
        get_match_detail_url = str.format("https://americas.api.riotgames.com/lol/match/v5/matches/{0}?api_key={1}",
                                          match_id, api_key)
        match_id_response_dict = get_response_json(get_match_detail_url)

        timestamp = match_id_response_dict.get('info',{}).get('gameCreation') // 1000

        a = datetime.fromtimestamp(timestamp)

        date_time_str = a.strftime("%m-%d %I:%M %p")

        gameDuration = time.strftime('%H:%M:%S', time.gmtime(match_id_response_dict.get('info',{}).get('gameDuration')))

        match_id_dict = {'gameCreation':date_time_str,'gameDuration':gameDuration,'gameMode':match_id_response_dict.get('info',{}).get('gameMode'),'match':match_id}

        participants = match_id_response_dict.get("info").get("participants")

        for participant in participants:
            if participant.get("puuid") == puuid:
                match_id_dict['deaths'] = participant.get("deaths")
                match_id_dict['kills'] = participant.get("kills")
                match_id_dict['assists'] = participant.get("assists")
                kda = round(participant.get('challenges', {}).get("kda"),1)
                match_id_dict['kda'] = kda
                match_id_dict['championId'] = participant.get("championId")
                match_id_dict['championName'] = participant.get("championName")
                match_id_dict['championTransform'] = participant.get("championTransform")
                match_id_dict['lane'] = participant.get("lane")
                match_id_dict['role'] = participant.get("role")
                match_id_dict['individualPosition'] = participant.get("individualPosition")
                match_id_dict['win'] = participant.get("win")
                match_id_dict['participantId'] = participant.get("participantId")
                match_id_dict['riotIdGameName'] = participant.get("riotIdGameName")


        matches_dict[match_id] = match_id_dict

    return matches_dict


def get_users_participant_id(match_id, puuid, api_key):
    get_match_detail_url = str.format("https://americas.api.riotgames.com/lol/match/v5/matches/{0}?api_key={1}",
                                      match_id, api_key)
    match_detail_response_dict = get_response_json(get_match_detail_url)

    participants = match_detail_response_dict.get("info").get("participants")

    for participant in participants:
        if participant.get("puuid") == puuid:
            return participant.get("participantId")

    print(f"Participant {puuid} not found in participant list for match {match_id}")


def get_match_timeline(match_id, api_key):
    get_match_timeline_url = str.format(
        "https://americas.api.riotgames.com/lol/match/v5/matches/{0}/timeline?api_key={1}", match_id, api_key)
    return get_response_json(get_match_timeline_url)


def get_response_json(url):
    response = requests.get(url)
    status_code = response.status_code
    if (status_code != 200):
        print(f"Status code: {status_code} for url: {url}")
        exit(1)
    return response.json()