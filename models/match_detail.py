import datetime
from datetime import datetime
import time


class MatchDetails:
    def __init__(self, dict):
        self.matchId = dict.get('metadata', {}).get('matchId')
        self.gameCreation = (datetime.fromtimestamp(dict.get('info', {}).get('gameCreation') // 1000)).strftime("%m-%d %I:%M %p")
        self.gameDuration = time.strftime('%H:%M:%S',time.gmtime(dict.get('info', {}).get('gameDuration')))
        self.gameMode = dict.get('info', {}).get('gameMode')
        self.puuid = dict.get("puuid")

    def merge(self, dict):
        return dict.update(self)

class ParticipantMatchDetails:
    def __init__(self,dict):
        self.kills = dict.get('kills')
        self.deaths = dict.get('deaths')
        self.assists = dict.get('assists')
        self.kda = round(dict.get('challenges', {}).get('kda'))
        self.deaths = dict.get('deaths')
        self.championId = dict.get('championId')
        self.championName = dict.get('championName')
        self.championTransform = dict.get('championTransform')
        self.lane = dict.get('lane')
        self.role = dict.get('role')
        self.individualPosition = dict.get('individualPosition')
        self.win = dict.get('win')
        self.participantId = dict.get('participantId')
        self.riotIdGameName = dict.get('riotIdGameName')
        self.puuid = dict.get('puuid')

def merge(obj1, obj2):
    obj1.__dict__.update(obj2.__dict__)
    return obj1