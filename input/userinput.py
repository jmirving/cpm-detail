#game tag
game_tag="3nderWiggin"
#tag_line
tag_line="NA1"

def getuser():
    user_input = dict()
    user_input['game_tag'] = input("Enter username as visible in game: ")
    user_input['tag_line'] = input("Enter tag line without the leading #. This is the #value under your game name if you hover your profile picture. ")
    return user_input