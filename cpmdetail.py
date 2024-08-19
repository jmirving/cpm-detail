import configparser
import models.match_detail
import service.riotapi
from errors.not_found_error import NotFoundError

JUNGLE_CS = "jungle_cs"

LANE_CS = "lane_cs"

config = configparser.ConfigParser()
config.read_file(open(r'api-key.txt'))
api_key = config.get('API Key', 'api_key')

try:
    def get_matches(puuid):
        return service.riotapi.get_matches(puuid, api_key, 5)


    def get_match_detail(matches, puuid):
        detailed_matches_dict = {}
        for match in matches:
            match_id = match
            match_detail_dict = service.riotapi.get_match_detail(match_id, api_key)
            match_detail_dict['puuid'] = puuid
            participants_dict = match_detail_dict.get("info").get("participants")
            participant_dict = [participant for (index, participant) in enumerate(participants_dict) if
                                participant.get("puuid") == puuid]
            participant_detail_dict = {k: v for participant_dict in participant_dict for (k, v) in
                                       participant_dict.items()}
            match_detail_dict = models.match_detail.merge(models.match_detail.MatchDetails(match_detail_dict),
                                                          models.match_detail.ParticipantMatchDetails(
                                                              participant_detail_dict))
            detailed_matches_dict[match_id] = match_detail_dict

        return detailed_matches_dict


    def get_matches_from_user_input(game_tag, tag_line):
        puuid = service.riotapi.get_puuid(game_tag, tag_line, api_key)
        matches = get_matches(puuid)
        return get_match_detail(matches, puuid)

    def get_match_timeline(match_id):
        # get match timeline
        match_timeline = service.riotapi.get_match_timeline(match_id, api_key)

        return match_timeline.get("info").get("frames")


    def get_cs_per_frame(participant_id, match_id):
        frames = get_match_timeline(match_id)
        minute_count = 0
        participant_events_per_minute = {}
        events_per_minute = {}
        for frame in frames:
            # gets participant info for a given minute
            participant_frame = frame.get("participantFrames").get(participant_id)
            minions_killed = participant_frame.get("minionsKilled")
            jungle_minions_killed = participant_frame.get("jungleMinionsKilled")
            exp = participant_frame.get("xp")
            participant_frame_dict = {LANE_CS: minions_killed, ("%s" % JUNGLE_CS): jungle_minions_killed, "exp": exp}
            participant_events_per_minute[minute_count] = participant_frame_dict

            # get events for a given minute
            events_this_minute = frame.get("events")
            participant_events_dict = {}
            participant_events_this_minute = 0
            for event in events_this_minute:
                print(str(f"Event: {event}"))
                event_participant_id = event.get("participantId")
                print(str(f"Is this eventPID [{event_participant_id}] = the PID [{int(participant_id)}]? {event_participant_id == int(participant_id)}"))
                if event_participant_id is not None and int(event_participant_id) == int(participant_id):
                    print(str(f"PID {event_participant_id} is not None and matches the user PID {participant_id}"))
                    participant_events_dict[participant_events_this_minute] = {"event_type": event.get("type"), "context": "self"}

                elif "assistingParticipantIds" in event and int(participant_id) in event.get("assistingParticipantIds"):
                    print(str(f"assistingParticipantIds is present and matches the user PID {participant_id}"))
                    participant_events_dict[participant_events_this_minute] = {"event_type": event.get("type"), "context": "assist"}

                elif "killerId" in event and int(participant_id) == event.get("killerId"):
                    print(str(f"killerId is present and matches the user PID {participant_id}"))
                    participant_events_dict[participant_events_this_minute] = {"event_type": event.get("type"), "context": "killer"}

                elif "victimId" in event and int(participant_id) == event.get("victimId"):
                    print(str(f"victimId is present and matches the user PID {participant_id}"))
                    participant_events_dict[participant_events_this_minute] = {"event_type": event.get("type"), "context": "victim"}

                participant_events_this_minute = participant_events_this_minute + 1

            if len(participant_events_dict) > 0:
                print(str(f"Event present!"))
                events_per_minute[minute_count] = participant_events_dict

            # go to the next frame
            minute_count = minute_count + 1

        # Using the metadata we gathered above, calculate the differences in CS
        lane_cs_previous_value = 0
        jungle_cs_previous_value = 0
        exp_previous_value = 0
        frame_count = 0
        output_dict = {}

        for frame in participant_events_per_minute:
            participant_event = participant_events_per_minute[frame]
            lane_cs = participant_event[LANE_CS]
            jungle_cs = participant_event[JUNGLE_CS]
            total_cs = lane_cs + jungle_cs
            lane_frame_diff = lane_cs - lane_cs_previous_value
            jungle_frame_diff = jungle_cs - jungle_cs_previous_value

            exp_in_frame = participant_event["exp"]
            exp_frame_diff = exp_in_frame - exp_previous_value

            if frame in events_per_minute:
                events = events_per_minute[frame]
            else:
                events = {"event_type": "None", "context": "None"}

            output_dict[frame_count] = {"total": total_cs, "lane_diff": lane_frame_diff,
                                        "jungle_diff": jungle_frame_diff, "exp": exp_in_frame, "exp_diff": exp_frame_diff, "events": events}

            # increments
            lane_cs_previous_value = lane_cs_previous_value + lane_frame_diff
            jungle_cs_previous_value = jungle_cs_previous_value + jungle_frame_diff
            exp_previous_value = exp_previous_value + exp_frame_diff
            frame_count = frame_count + 1

        return output_dict

except NotFoundError:
    print("cpmdetail: Not found!")
    raise
