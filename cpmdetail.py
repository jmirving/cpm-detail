import configparser
import models.match_detail
import service.riotapi
import pandas as pd

from errors.not_found_error import NotFoundError

csv_file_path = 'static/data/champ_expert_mapper.csv'
champ_expert_mapper = pd.read_csv(csv_file_path)

JUNGLE_CS = "jungle_cs"

LANE_CS = "lane_cs"

config = configparser.ConfigParser()
config.read_file(open(r'api-key.txt'))
api_key = config.get('API Key', 'api_key')

def ensure_string(value):
    if isinstance(value, int):
        return str(value)
    return value

try:
    def get_matches(puuid):
        return service.riotapi.get_matches(puuid, api_key, 5)


    def get_matches_detail(matches, puuid):
        print(f"Getting match details for {matches}:{puuid}")
        detailed_matches_dict = {}
        for match_id in matches:
            detailed_matches_dict[match_id] = get_single_match_detail(match_id, puuid)

        return detailed_matches_dict


    def get_single_match_detail(match_id, puuid):
        match_detail_dict = service.riotapi.get_match_detail(match_id, api_key)
        match_detail_dict['puuid'] = puuid
        participants_dict = match_detail_dict.get("info").get("participants")
        participant_dict = [participant for (index, participant) in enumerate(participants_dict) if
                            participant.get("puuid") == puuid]
        participant_detail_dict = {k: v for participant_dict in participant_dict for (k, v) in
                                   participant_dict.items()}
        match_details = models.match_detail.MatchDetails(match_detail_dict)
        participant_details = models.match_detail.ParticipantMatchDetails(participant_detail_dict)
        return models.match_detail.merge(match_details, participant_details)


    def get_puuid_from_data(game_tag, tag_line):
        return service.riotapi.get_puuid(game_tag, tag_line, api_key)


    def get_matches_from_user_input(game_tag, tag_line):
        puuid = get_puuid_from_data(game_tag, tag_line)
        matches = get_matches(puuid)
        return get_matches_detail(matches, puuid)


    def get_last_match(puuid):
        return service.riotapi.get_last_match(puuid, api_key)


    def get_match_timeline(match_id):
        # get match timeline
        match_timeline = service.riotapi.get_match_timeline(match_id, api_key)

        return match_timeline.get("info").get("frames")


    def get_cs_per_frame(participant_id, match_id):
        participant_id = ensure_string(participant_id)
        frames = get_match_timeline(match_id)
        minute_count = 0
        participant_frames_array = {}
        events_per_minute = {}
        for frame in frames:
            print(f"Got frame: {frame}")
            # gets participant info for a given minute
            participant_frame = frame.get("participantFrames").get(participant_id)
            print(f"Getting participant frame {participant_frame} for participant ID {participant_id}")
            minions_killed = participant_frame.get("minionsKilled")
            jungle_minions_killed = participant_frame.get("jungleMinionsKilled")
            exp = participant_frame.get("xp")
            level = participant_frame.get("level")
            gold = participant_frame.get("totalGold")
            participant_frame_dict = {LANE_CS: minions_killed, JUNGLE_CS: jungle_minions_killed, "exp": exp,
                                      "level": level, "gold": gold}
            participant_frames_array[minute_count] = participant_frame_dict

            # get events for a given minute
            events_this_minute = frame.get("events")
            participant_events_dict = {}
            participant_events_this_minute = 0
            for event in events_this_minute:
                # print(str(f"Event: {event}"))
                event_participant_id = event.get("participantId")
                # print(str(f"Is this eventPID [{event_participant_id}] = the PID [{int(participant_id)}]? {event_participant_id == int(participant_id)}"))
                if event_participant_id is not None and int(event_participant_id) == int(participant_id):
                    # print(str(f"PID {event_participant_id} is not None and matches the user PID {participant_id}"))
                    participant_events_dict[participant_events_this_minute] = {"event_type": event.get("type"),
                                                                               "context": "self"}

                elif "assistingParticipantIds" in event and int(participant_id) in event.get("assistingParticipantIds"):
                    # print(str(f"assistingParticipantIds is present and matches the user PID {participant_id}"))
                    participant_events_dict[participant_events_this_minute] = {"event_type": event.get("type"),
                                                                               "context": "assist"}

                elif "killerId" in event and int(participant_id) == event.get("killerId"):
                    # print(str(f"killerId is present and matches the user PID {participant_id}"))
                    participant_events_dict[participant_events_this_minute] = {"event_type": event.get("type"),
                                                                               "context": "killer"}

                elif "victimId" in event and int(participant_id) == event.get("victimId"):
                    # print(str(f"victimId is present and matches the user PID {participant_id}"))
                    participant_events_dict[participant_events_this_minute] = {"event_type": event.get("type"),
                                                                               "context": "victim"}

                participant_events_this_minute = participant_events_this_minute + 1

            if len(participant_events_dict) > 0:
                # print(str(f"Event present!"))
                events_per_minute[minute_count] = participant_events_dict

            # go to the next frame
            minute_count = minute_count + 1

        # Using the metadata we gathered above, calculate the differences in CS
        lane_cs_previous_value = 0
        jungle_cs_previous_value = 0
        exp_previous_value = 0
        gold_previous_value = 0
        frame_count = 0
        output_dict = {}

        for frame in participant_frames_array:
            participant_event = participant_frames_array[frame]
            lane_cs = participant_event[LANE_CS]
            jungle_cs = participant_event[JUNGLE_CS]
            total_cs = lane_cs + jungle_cs
            lane_frame_diff = lane_cs - lane_cs_previous_value
            jungle_frame_diff = jungle_cs - jungle_cs_previous_value

            exp_in_frame = participant_event["exp"]
            exp_frame_diff = exp_in_frame - exp_previous_value
            level = participant_event["level"]

            gold_in_frame = participant_event["gold"]
            gold_frame_diff = gold_in_frame - gold_previous_value

            if frame in events_per_minute:
                events = events_per_minute[frame]
            else:
                events = {"event_type": "None", "context": "None"}

            output_dict[frame_count] = {"total": total_cs, "lane_diff": lane_frame_diff,
                                        "jungle_diff": jungle_frame_diff,
                                        "exp": exp_in_frame, "level": level, "exp_diff": exp_frame_diff,
                                        "gold": gold_in_frame, "gold_diff": gold_frame_diff,
                                        "events": events}

            # increments
            lane_cs_previous_value = lane_cs_previous_value + lane_frame_diff
            jungle_cs_previous_value = jungle_cs_previous_value + jungle_frame_diff
            exp_previous_value = exp_previous_value + exp_frame_diff
            gold_previous_value = gold_previous_value + gold_frame_diff
            frame_count = frame_count + 1

        return output_dict


    def get_comparison(participant_id, match_id, champ_name):
        # look up 1 or more skilled players on this champ from a static look up table
        print(str(f"Getting experts for {champ_name}"))
        results = champ_expert_mapper[champ_expert_mapper['champ_name'].str.lower() == champ_name.lower()]
        # return 1 or more results
        expert = results['expert'].values[0]
        tag = results['tag'].values[0]
        print(str(f"Getting puuid for {expert}:{tag}"))
        expert_puuid = get_puuid_from_data(expert, tag)
        print(str(f"Retrieved {expert_puuid}"))

        expert_last_match = get_last_match(expert_puuid)
        expert_match_detail = get_single_match_detail(expert_last_match, expert_puuid)
        expert_participant_id = expert_match_detail.participantId
        expert_cs_per_frame = get_cs_per_frame(expert_participant_id, expert_last_match)
        user_cs_per_frame = get_cs_per_frame(participant_id, match_id)

        # Find the size of the smaller list/array
        size_expert_cs = len(expert_cs_per_frame)
        size_user_cs = len(user_cs_per_frame)

        comparison_frames_array = {}

        # Determine the minimum size
        min_size = min(size_expert_cs, size_user_cs)
        for i in range(min_size):
            # Access diffs from user cs array
            user_lane_diff = user_cs_per_frame[i]['lane_diff']
            user_jungle_diff = user_cs_per_frame[i]['jungle_diff']
            user_total_diff = user_lane_diff + user_jungle_diff

            # Access diffs from expert cs array
            expert_lane_diff = expert_cs_per_frame[i]['lane_diff']
            expert_jungle_diff = expert_cs_per_frame[i]['jungle_diff']
            expert_total_diff = expert_lane_diff + expert_jungle_diff

            comparison_frames_array[i] = {"your_cs_added": user_total_diff,
                                          "your_exp_added": user_cs_per_frame[i]['exp_diff'],
                                          "your_gold_added": user_cs_per_frame[i]['gold_diff'],
                                          "expert_cs_added": expert_total_diff,
                                          "expert_exp_added": expert_cs_per_frame[i]['exp_diff'],
                                          "expert_gold_added": expert_cs_per_frame[i]['gold_diff']}

        return comparison_frames_array



except NotFoundError:
    print("cpmdetail: Not found!")
    raise
