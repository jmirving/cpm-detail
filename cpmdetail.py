import service.riotapi
import configparser
import datetime
from datetime import datetime
import time

config = configparser.ConfigParser()
config.read_file(open(r'api-key.txt'))
api_key = config.get('API Key', 'api_key')


def get_puuid(game_tag, tag_line):
    return service.riotapi.get_puuid(game_tag, tag_line, api_key)


def get_matches(puuid):
    return service.riotapi.get_matches(puuid, api_key, 5)


def get_match_detail(matches, puuid):
    matches_dict = {}
    for match in matches:
        match_id = match
        data = service.riotapi.get_match_detail(match_id, puuid, api_key)

        timestamp = data.get('info', {}).get('gameCreation') // 1000

        a = datetime.fromtimestamp(timestamp)

        date_time_str = a.strftime("%m-%d %I:%M %p")

        gameDuration = time.strftime('%H:%M:%S',
                                     time.gmtime(data.get('info', {}).get('gameDuration')))

        match_id_dict = {'gameCreation': date_time_str, 'gameDuration': gameDuration,
                         'gameMode': data.get('info', {}).get('gameMode'), 'match': match_id}

        participants = data.get("info").get("participants")

        for participant in participants:
            if participant.get("puuid") == puuid:
                match_id_dict['deaths'] = participant.get("deaths")
                match_id_dict['kills'] = participant.get("kills")
                match_id_dict['assists'] = participant.get("assists")
                kda = round(participant.get('challenges', {}).get("kda"), 1)
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


def get_matches_ux(matches, puuid):
    return service.riotapi.get_matches_ux(matches, puuid, api_key)


def get_participant(match_id, puuid):
    # get participant id
    return service.riotapi.get_users_participant_id(match_id, puuid, api_key)


def get_match_timeline(match_id):
    # get match timeline
    match_timeline = service.riotapi.get_match_timeline(match_id, api_key)
    return match_timeline.get("info").get("frames")

def get_cs_per_frame(participant_id, frames):
    minute_count = 0
    minion_data_dict = {}
    for frame in frames:
        participant_frame = frame.get("participantFrames").get(str(participant_id))
        minions_killed = participant_frame.get("minionsKilled")
        minion_data_dict[minute_count] = minions_killed

        minute_count = minute_count + 1

    previous_value = 0
    frame_count = 0
    output_string_list = []
    for frame in minion_data_dict:
        minions = minion_data_dict[frame]
        frame_diff = minions - previous_value
        output_string_list.append(str.format("CS: {1} - CS Since Last Frame: {2}", frame, minions, frame_diff))
        previous_value = minions
        frame_count = frame_count + 1

    return output_string_list