"""
Author: Asaf Biran
Program Name - FinalProjectProtocol
Description: Encodes game states into separated text strings for TCP
             transit and parses incoming packets back into typed variables.
"""


def build_update(lane, alive, lives):
    return f"{lane},{alive},{lives}\n".encode('utf-8')


def build_spawn_obs(lane):
    return f"SPAWN_OBS,{lane}\n".encode('utf-8')


def build_spawn_heart(lane):
    return f"SPAWN_HEART,{lane}\n".encode('utf-8')


def parse_msg(msg):
    if not msg:
        return None

    if "START" in msg:
        return ["START"]

    try:
        parts = msg.split(',')
        if parts[0] == "SPAWN_OBS":
            return ["SPAWN_OBS", int(parts[1])]
        elif parts[0] == "SPAWN_HEART":
            return ["SPAWN_HEART", int(parts[1])]
        elif len(parts) == 3:
            return ["UPDATE", int(parts[0]), parts[1] == "True", int(parts[2])]
    except:
        pass

    return None