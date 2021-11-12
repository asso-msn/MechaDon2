import discord


def member(member: discord.Member):
    if member.nick:
        return f'{member.nick} ({member._user})'
    return str(member._user)
