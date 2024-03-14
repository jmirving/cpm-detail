import requests
import service.detail
import configparser

config = configparser.ConfigParser()
config.read_file(open(r'api-key.txt'))

#game tag
game_tag="3nderWiggin"
#tag_line
tag_line="NA1"
#api key
api_key = config.get('API Key', 'api_key')

# get the puuid
puuid = service.detail.get_puuid(game_tag, tag_line, api_key)

#get last match id
last_match = service.detail.get_last_match(puuid, api_key)

#get match details
get_match_detail_url = str.format("https://americas.api.riotgames.com/lol/match/v5/matches/{0}?api_key={1}",last_match, api_key)
match_detail_response = requests.get(get_match_detail_url)
match_detail_response_dict = match_detail_response.json()
participants = match_detail_response_dict.get("info").get("participants")

participant_id = ""
for participant in participants:
    if participant.get("puuid") == puuid:
        participant_id = participant.get("participantId")

#get match timeline
get_match_timeline_url = str.format("https://americas.api.riotgames.com/lol/match/v5/matches/{0}/timeline?api_key={1}",last_match, api_key)
match_timeline_response = requests.get(get_match_timeline_url)
match_timeline_response_dict = match_timeline_response.json()
frames = match_timeline_response_dict.get("info").get("frames")

minute_count = 0;
minion_data_dict = {}
for frame in frames:
    participant_frame = frame.get("participantFrames").get(str(participant_id))
    minions_killed = participant_frame.get("minionsKilled")
    minion_data_dict[minute_count] = minions_killed

    minute_count = minute_count + 1

previous_value = 0
for frame in minion_data_dict:
    minions = minion_data_dict[frame]
    frame_diff = minions - previous_value
    minions_killed_output_string = str.format("Min: {0} - CS: {1} - CS Diff: {2}", frame, minions, frame_diff)
    print(minions_killed_output_string)
    previous_value = minions