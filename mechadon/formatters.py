import discord


def member(member: discord.Member):
    if member.nick:
        return f"{member.nick} aka {member._user}"
    return str(member._user)
