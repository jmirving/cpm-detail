import datetime
from datetime import datetime
import time


class MatchDetails:
    def __init__(self, metadata):
        self.matchId = metadata.get('metadata', {}).get('matchId')
        self.gameCreation = (datetime.fromtimestamp(metadata.get('info', {}).get('gameCreation') // 1000)).strftime(
            "%m-%d %I:%M %p")
        self.gameDuration = time.strftime('%H:%M:%S', time.gmtime(metadata.get('info', {}).get('gameDuration')))
        self.gameMode = metadata.get('info', {}).get('gameMode')
        self.puuid = metadata.get("puuid")

    def merge(self, metadata):
        return metadata.update(self)


class ParticipantMatchDetails:
    def __init__(self, info):
        self.kills = info.get('kills')
        self.deaths = info.get('deaths')
        self.assists = info.get('assists')
        self.kda = round(info.get('challenges', {}).get('kda'), 1)
        self.deaths = info.get('deaths')
        self.championId = info.get('championId')
        self.championName = info.get('championName')
        self.championTransform = info.get('championTransform')
        self.lane = info.get('lane')
        self.role = info.get('role')
        self.individualPosition = info.get('individualPosition')
        self.win = 'Victory' if info.get('win') else 'Defeat'
        self.participantId = info.get('participantId')
        self.riotIdGameName = info.get('riotIdGameName')
        self.puuid = info.get('puuid')
        self.win_color = 'gold' if self.win == 'Victory' else 'red'


def merge(obj1, obj2):
    obj1.__dict__.update(obj2.__dict__)
    return obj1
