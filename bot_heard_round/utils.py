"""
Utility methods
"""

import discord


def get_user_from_nick_or_name(name_nick: str, members: list[discord.User]) -> discord.User:
    """
    :param name_nick:
    :param members:
    :return: The discord user, otherwise none
    """
    user = discord.utils.get(members, nick=name_nick)
    if not user:
        user = discord.utils.get(members, name=name_nick)
    return user
