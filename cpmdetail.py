import requests
import service.riotapi
import input.userinput
import configparser

config = configparser.ConfigParser()
config.read_file(open(r'api-key.txt'))

user_input = input.userinput.getuser()
#game tag
game_tag=user_input.get('game_tag')
#tag_line
tag_line=user_input.get('tag_line')
#api key
api_key = config.get('API Key', 'api_key')

# get the puuid
puuid = service.riotapi.get_puuid(game_tag, tag_line, api_key)

#get last match id
match_id = service.riotapi.get_last_match(puuid, api_key)

#get participant id
participant_id = service.riotapi.get_users_participant_id(match_id, puuid, api_key)

#get match timeline
match_timeline = service.riotapi.get_match_timeline(match_id, api_key)
frames = match_timeline.get("info").get("frames")

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