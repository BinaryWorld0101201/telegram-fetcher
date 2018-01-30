#!/usr/bin/env python3

from telethon import TelegramClient
from telethon.tl.functions.contacts import ResolveUsernameRequest
from telethon.tl.functions.channels import GetParticipantRequest
from telethon.errors.rpc_error_list import UserNotParticipantError
from telethon.tl import types
# import json
import config
from datetime import date, datetime


def json_serial(obj):
    """JSON serializer for objects not serializable by default json code"""

    if isinstance(obj, (datetime, date)):
        return obj.isoformat()
    raise TypeError("Type %s not serializable" % type(obj))


LIMIT = 500

client = TelegramClient('fetcher-session', config.api_id, config.api_hash)
client.connect()

if not client.is_user_authorized():
    client.sign_in(phone=config.phone)
    me = client.sign_in(code=int(input('Enter code: ')))

channel = client(ResolveUsernameRequest(config.channel)).chats[0]

total, messages, senders = client.get_message_history(
        channel, limit=1, offset_id=0)
cursor = messages[0].id + 1
users = []
users_added = set()


def check_participant(u):
    try:
        client(GetParticipantRequest(channel, u))
        return True
    except UserNotParticipantError:
        return False


while True:
    total, messages, senders = client.get_message_history(
            channel, limit=LIMIT, offset_id=cursor)
    if not messages:
        break

    for m, s in zip(messages, senders):
        if isinstance(m, types.MessageService):
            if isinstance(m.action, types.MessageActionChatJoinedByLink):
                if check_participant(s):
                    users.append((m.date, s.to_dict()))
                    users_added.add(s.id)
            elif isinstance(m.action, types.MessageActionChatAddUser):
                for u_id in m.action.users:
                    if u_id == s.id:
                        user = s
                    else:
                        user = client.get_entity(u_id)
                    if check_participant(s):
                        users.append((m.date, user.to_dict()))
                        users_added.add(user.id)

    cursor = messages[-1].id
    print(cursor)
    if cursor <= 1:
        break

import IPython
IPython.embed()
