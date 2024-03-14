import requests

def get_puuid(game_tag, tag_line,api_key):
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


def get_response_json(url):
    response = requests.get(url)
    status_code = response.status_code
    if (status_code != 200):
        print(f"Status code: {status_code} for url: {url}")
        exit(1)
    return response.json()