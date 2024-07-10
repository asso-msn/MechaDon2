import discord


def member(member: discord.Member):
    def similar(*args):
        args = [x.lower() for x in args if x]
        if len(set(args)) == 1:
            return args[0]
        return False

    result = member.nick
    if result:
        if not similar(result, member.global_name):
            result += f" aka {member.global_name}"
    else:
        result = member.global_name

    if result:
        if not (
            (member.nick and similar(member.nick, member.name))
            or similar(member.global_name, member.name)
        ):
            result += f" (@{member.name})"
    else:
        result = member.name

    for c in ("_", "*", "`", "~", "|", ">", "#"):
        result = result.replace(c, f"\\{c}")

    return result
