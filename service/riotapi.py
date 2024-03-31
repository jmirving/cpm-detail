import requests

from errors.not_found_error import NotFoundError

def get_puuid(game_tag, tag_line, api_key):
    # get the puuid
    get_puuid_url = str.format("https://americas.api.riotgames.com/riot/account/v1/accounts/by-riot-id/{0}/{1}?api_key={2}",
                               game_tag, tag_line, api_key)
    puuid_response_dict = get_response_json(get_puuid_url)
    return puuid_response_dict.get("puuid")


def get_last_match(puuid, api_key):
    get_match_url = str.format("https://americas.api.riotgames.com/lol/match/v5/matches/by-puuid/{0}/ids?start=0&count=20&api_key={1}", puuid,
               api_key)
    match_response_dict = get_response_json(get_match_url)
    return match_response_dict[0]


def get_matches(puuid, api_key, num_matches):
    get_match_url = str.format(
        "https://americas.api.riotgames.com/lol/match/v5/matches/by-puuid/{0}/ids?start=0&count={1}&api_key={2}", puuid,
        num_matches,
        api_key)
    return get_response_json(get_match_url)


def get_match_detail(match_id, api_key):
    get_match_detail_url = str.format("https://americas.api.riotgames.com/lol/match/v5/matches/{0}?api_key={1}",
                                      match_id, api_key)
    return get_response_json(get_match_detail_url)


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
    try:
        response = requests.get(url)
        status_code = response.status_code
        if status_code != 200:
            if status_code == 404:
                raise NotFoundError
        return response.json()
    except NotFoundError:
        raise
