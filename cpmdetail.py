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
        minion_data_dict = {}
        for frame in frames:
            participant_frame = frame.get("participantFrames").get(str(participant_id))
            minions_killed = participant_frame.get("minionsKilled")
            jungle_minions_killed = participant_frame.get("jungleMinionsKilled")
            minions_dict = {LANE_CS: minions_killed, ("%s" % JUNGLE_CS): jungle_minions_killed}
            minion_data_dict[minute_count] = minions_dict

            minute_count = minute_count + 1

        lane_cs_previous_value = 0
        jungle_cs_previous_value = 0
        frame_count = 0
        output_dict = {}
        for frame in minion_data_dict:
            minions = minion_data_dict[frame]
            lane_cs = minions[LANE_CS]
            jungle_cs = minions[JUNGLE_CS]

            total_cs = lane_cs + jungle_cs
            lane_frame_diff = lane_cs - lane_cs_previous_value
            jungle_frame_diff = jungle_cs - jungle_cs_previous_value

            output_dict[frame_count] = {"total": total_cs, "lane_diff": lane_frame_diff,
                                        "jungle_diff": jungle_frame_diff}

            # increments
            lane_cs_previous_value = lane_cs_previous_value + lane_frame_diff
            jungle_cs_previous_value = jungle_cs_previous_value + jungle_frame_diff
            frame_count = frame_count + 1

        return output_dict

except NotFoundError:
    print("cpmdetail: Not found!")
    raise
