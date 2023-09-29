class User:
    def __init__(self, id, name=None, imageId=None, email=None, flags=None, options=None, permissions=None):
        self.id = id
        self.name = name
        self.image_id = imageId
        self.email = email
        self.flags = flags
        self.options = options
        self.permissions = permissions


class Member:
    def __init__(self, admin, owner, userInfo, guildId=None):
        self.guild_id = guildId
        self.admin = admin
        self.owner = owner
        self.user_info = User(**userInfo)


class UnreadMsg:
    def __init__(self, msgId, count, time, mentions):
        self.msg_id = msgId
        self.count = count
        self.time = time
        self.mentions = mentions


class Attachment:
    def __init__(self, id, filename, type):
        self.id = id
        self.filename = filename
        self.type = type


class Msg:
    def __init__(self, id, guildId, content,author=None,  created=None, modified=None, msgSaved=None, requestId=None, mentionsEveryone=None, mentions=None, attachments=None):
        self.id = id
        self.author = User(**author) if author is not None else None
        self.content = content
        self.guild_id = guildId
        self.created = created
        self.modified = modified
        self.msg_saved = msgSaved
        self.request_id = requestId
        self.mentions_everyone = mentionsEveryone
        self.mentions = [User(**mention) for mention in mentions] if mentions is not None else None
        self.attachments = [Attachment(**attachment)
                            for attachment in attachments] if attachments is not None else None


class Dm:
    def __init__(self, id, userInfo, unread):
        self.id = id
        self.user_info = User(**userInfo)
        self.unread = UnreadMsg(**unread)


class Guild:
    def __init__(self, id, name=None, imageId=None, ownerId=None, dm=None, saveChat=None, unread=None):
        self.id = id
        self.dm = dm
        self.name = name
        self.image_id = imageId
        self.owner_id = ownerId
        self.save_chat = saveChat
        self.unread = UnreadMsg(**unread) if unread is not None else None

class Typing:
    def __init__(self, guildId, userInfo, time):
        self.guild_id = guildId
        self.user_info = User(**userInfo)
        self.time = time

class Invite:
    def __init__(self, guildId, invite):
        self.guild_id = guildId
        self.invite = invite
