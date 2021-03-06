"""
Bot starter
"""
# bot.py
import os
import random

import discord
from discord.ext import commands
from dotenv import load_dotenv

from bot_heard_round import emoji
from bot_heard_round.combat_status import CombatRound, CombatStatus
from bot_heard_round.fleet import CombatColumn, FleetList

intents = discord.Intents.default()
intents.members = True

load_dotenv()
TOKEN = os.getenv('DISCORD_TOKEN')

COMMAND_PREFIX = os.getenv('COMMAND_PREFIX', '!')
bot = commands.Bot(command_prefix=COMMAND_PREFIX, intents=intents)
COMBAT_CATEGORY_NAME = 'combat'
BOT_MASTER_ROLE = 'bot-master'


@bot.event
async def on_ready():
    """

    :return:
    """
    print(f'{bot.user.name} has connected to Discord!')


@bot.event
async def on_command_error(ctx, error):
    """

    :param ctx:
    :param error:
    :return:
    """
    if isinstance(error, commands.errors.CheckFailure):
        await ctx.send('You do not have the correct role for this command.')
    elif isinstance(error, commands.errors.MissingRequiredArgument):
        await ctx.send(error)
    elif isinstance(error, commands.errors.CommandNotFound):
        await ctx.send(
            "Unknown command - try {0}help to see the available commands".format(COMMAND_PREFIX)
        )
    else:
        control = discord.utils.get(ctx.guild.roles, name=BOT_MASTER_ROLE)

        await ctx.send(
            f'{control.mention} there was a problem running this command please investigate'
        )
        raise error


CONTROL_ROLE_NAME = 'Control' if os.getenv('UPPERCASE_CONTROL') else 'control'


@bot.command(
    name='start-combat',
)
async def start_combat(ctx: commands.context.Context, target: str):
    """

    :param ctx:
    :param target:
    :return:
    """
    attacker = ctx.author

    if len(ctx.message.mentions) == 0:
        await ctx.reply("Please use the mention format (ie `@person-to-attack`)")
        return

    if len(ctx.message.mentions) > 1:
        await ctx.reply("Only allowed to attack one person")
        return

    defender = ctx.message.mentions[0]

    guild: discord.Guild = ctx.guild

    await ctx.send(
        'Starting combat, {} attacks {}...'.format(ctx.author.mention, target)
    )

    category: discord.CategoryChannel = discord.utils.get(guild.categories, name='combat')

    control = discord.utils.get(guild.roles, name=CONTROL_ROLE_NAME)

    if not category:
        category = await guild.create_category(
            COMBAT_CATEGORY_NAME,
            overwrites={
                guild.default_role: discord.PermissionOverwrite(read_messages=False),
                control: discord.PermissionOverwrite(read_messages=True),
            }
        )

    while True:
        random_bytes = random.getrandbits(16)

        channel_name = f"combat-{random_bytes}"
        # Next, create the combat-* role
        channel = discord.utils.get(guild.roles, name=channel_name, category=category)

        if not channel:
            channel = await guild.create_text_channel(
                name=channel_name,
                category=category,
                overwrites={
                    attacker: discord.PermissionOverwrite(read_messages=True),
                    defender: discord.PermissionOverwrite(read_messages=True)
                }
            )
            break

    combat_status = CombatStatus(attacker, defender)

    status = await combat_status.send_message(channel)
    await status.pin()

    await channel.send(
        'Combat started, {} attacks {}\n'
        '{} copy your `fleet-list` from your spreadsheet to import your fleet'.format(
            attacker.mention,
            defender.mention,
            attacker.mention
        )
    )

    def check_for_message(author):
        def check(message: discord.Message):
            if message.channel != channel:
                return False

            if message.author != author:
                return False

            content = message.content

            try:
                FleetList.from_str(content)
                return True
            except ValueError as error:
                print(error)
                return False

        return check

    attacker_fleet_msg = await bot.wait_for(
        'message',
        check=check_for_message(attacker)
    )

    await attacker_fleet_msg.reply('Importing fleet now...')
    combat_status.add_fleet_for(True, attacker_fleet_msg.content)

    await combat_status.update_message()

    await channel.send(
        '{} copy your `fleet-list` from your spreadsheet to import your fleet'.format(
            defender.mention
        )
    )

    defender_fleet_msg = await bot.wait_for(
        'message',
        check=check_for_message(defender)
    )

    await defender_fleet_msg.reply('Importing fleet now...')

    combat_status.add_fleet_for(False, defender_fleet_msg.content)
    await combat_status.update_message()

    await start_combat_loop(combat_status)


@bot.command(
    name='clear-combat',
)
@commands.has_role(CONTROL_ROLE_NAME)
async def clear_combat(ctx: commands.context.Context):
    """

    :param ctx:
    :return:
    """
    guild = ctx.guild

    category = discord.utils.get(guild.categories, name=COMBAT_CATEGORY_NAME)

    if not category:
        return

    channels = category.text_channels
    await ctx.reply(f'Deleting {len(channels)} channels, please wait...')

    channel: discord.TextChannel
    for channel in channels:
        await channel.delete()

    await ctx.reply('Done!')


def reaction_check(message, expected_user, valid_reactions):
    """

    :rtype: function
    """

    def check_activated(reaction, user):
        return reaction.message == message \
               and reaction.emoji in valid_reactions \
               and user == expected_user

    return check_activated


async def request_ships(combat_status: CombatStatus, apply_attackers: bool):
    """

    :param combat_status:
    :param apply_attackers:
    :return:
    """
    channel: discord.TextChannel = combat_status.message.channel
    user_to_respond = combat_status.attacker if apply_attackers else combat_status.defender
    fleet = combat_status.attacker_fleet if apply_attackers else combat_status.defender_fleet

    ship_list = {}
    ship_text = []

    for fleet_column in fleet.where_column(CombatColumn.WAITING):
        if not fleet_column.ships:
            continue

        emoji_to_send = emoji.POSSIBLE_EMOJI[fleet_column.column_number - 1]

        ship_list[emoji_to_send] = fleet_column
        ship_text.append(
            "{}: Column {}: {}".format(emoji_to_send,
                                       fleet_column.column_number,
                                       fleet_column.ships_as_str
                                       ))

    if not ship_text:
        await channel.send(
            'No unassigned ships left in fleet, skipping {}'.format(user_to_respond.display_name)
        )
        return

    ships_message = await channel.send(
        "{}, please react to this with the ships you want to add.\n{}".format(
            user_to_respond.mention,
            "\n".join(ship_text)
        )
    )

    for emoji_to_send in ship_list:
        await ships_message.add_reaction(emoji_to_send)

    reaction, _ = await bot.wait_for(
        'reaction_add',
        check=reaction_check(
            ships_message,
            user_to_respond,
            ship_list
        )
    )

    fleet_column = ship_list[reaction.emoji]

    column_message = await channel.send(
        "{}, please react to this with which column you want to add fleet column {} to".format(
            user_to_respond.mention,
            fleet_column.column_number
        )
    )

    columns = {
        emoji.LEFT_EMOJI: CombatColumn.LEFT,
        emoji.CENTRE_EMOJI: CombatColumn.MIDDLE,
        emoji.RIGHT_EMOJI: CombatColumn.RIGHT
    }

    for emoji_to_send in columns:
        if fleet.where_column(columns[emoji_to_send]):
            continue

        await column_message.add_reaction(emoji_to_send)

    reaction, _ = await bot.wait_for(
        'reaction_add',
        check=reaction_check(
            column_message,
            user_to_respond,
            columns
        )
    )

    await channel.send(
        "Moving fleet {} to column {}".format(
            fleet_column.column_number,
            columns[reaction.emoji].value
        )
    )

    fleet_column.combat_column = columns[reaction.emoji]

    await combat_status.update_message()


async def start_combat_loop(combat_status: CombatStatus):
    """

    :param combat_status:
    :return:
    """
    channel: discord.TextChannel = combat_status.message.channel

    messages = {
        CombatRound.MISSILE_ONE: 'COMBAT HAS STARTED!',
        CombatRound.MISSILE_TWO:
            'Second round of combat. If nobody retreats Railgun combat will start!',
        CombatRound.RAIL_GUN: 'Final combat round. ALL DEFENCE WILL BE ZERO THIS ROUND',
    }

    for combat_round in messages:
        combat_status.combat_round = combat_round

        if combat_round != CombatRound.MISSILE_ONE:
            await allow_fleet_switch(channel, combat_status)
        else:
            await handle_patrol_mode(channel, combat_status)

        await combat_status.update_message()

        await channel.send(messages[combat_round])

        react_message: discord.Message = await channel.send(
            'React to this message with :crossed_swords: to fight, or with :flag_white: to retreat'
        )

        for combat_emoji in ['???', '????']:
            await react_message.add_reaction(combat_emoji)

        attack_react, _ = await bot.wait_for(
            'reaction_add',
            check=reaction_check(react_message, combat_status.attacker, ['???', '????'])
        )
        defend_react, _ = await bot.wait_for(
            'reaction_add',
            check=reaction_check(react_message, combat_status.defender, ['???', '????'])
        )

        if '???' not in [attack_react.emoji, defend_react.emoji]:
            combat_status.combat_round = CombatRound.FINISHED
            await combat_status.update_message()
            await channel.send('Both players have retreated, combat finished')
            return

        await channel.send('Combat will continue for another round')

        if combat_status.combat_round == CombatRound.MISSILE_ONE:
            apply_order = [
                True,
                False,
                False,
                True,
                True,
                False
            ]

            for apply_attacker_ships in apply_order:
                await request_ships(combat_status, apply_attacker_ships)

        for message in combat_status.resolve_combat_round():
            await channel.send(message)

            await combat_status.update_message()
            await channel.send(str(combat_status))

        if '????' in [attack_react.emoji, defend_react.emoji]:
            await channel.send('A player has retreated, combat finished')

    combat_status.combat_round = CombatRound.FINISHED
    await combat_status.update_message()


async def handle_patrol_mode(channel: discord.TextChannel, combat_status: CombatStatus):
    """
    Handle patrol mode
    :param channel:
    :param combat_status:
    :return:
    """
    for user_to_mention, fleet in [(combat_status.attacker, combat_status.attacker_fleet),
                                   (combat_status.defender, combat_status.defender_fleet)]:
        message = await channel.send(
            '{}, please confirm whether your fleet is in patrol mode or not'
            '(Your spreadsheet says that it {})'
            'If so, react with {} otherwise react with {}'.format(
                user_to_mention.mention,
                'is' if fleet.patrol_mode else 'is not',
                emoji.TICK_EMOJI,
                emoji.CROSS_EMOJI
            )
        )

        for emoji_to_add in [emoji.TICK_EMOJI, emoji.CROSS_EMOJI]:
            await message.add_reaction(emoji_to_add)

        react, _ = await bot.wait_for(
            'reaction_add',
            check=reaction_check(
                message,
                user_to_mention,
                [emoji.TICK_EMOJI, emoji.CROSS_EMOJI]
            )
        )

        fleet.patrol_mode = react == emoji.TICK_EMOJI


async def allow_fleet_switch(channel: discord.TextChannel, combat_status: CombatStatus):
    """

    :param channel:
    :param combat_status:
    :return:
    """
    for user_to_mention, fleet in [(combat_status.attacker, combat_status.attacker_fleet),
                                   (combat_status.defender, combat_status.defender_fleet)]:
        try:
            emojis_to_add, waiting_fleet = fleet.swap_options()
        except FleetList.NoWaitingFleetError:
            await channel.send(
                '{} has no waiting fleets, skipping fleet movement'.format(
                    user_to_mention.display_name
                )
            )
            continue

        message = await channel.send(
            '{} if you wish to swap a fleet column with a waiting fleet, '
            'react with the column you wish to move'.format(
                user_to_mention.mention
            )
        )

        for emoji_to_add in emojis_to_add:
            await message.add_reaction(emoji_to_add)

        react, _ = await bot.wait_for(
            'reaction_add',
            check=reaction_check(message, user_to_mention, emojis_to_add)
        )

        if not emojis_to_add[react.emoji]:
            continue

        if len(waiting_fleet) == 1:
            _, to_swap_in = waiting_fleet.popitem()
        else:
            lines = ['React with which waiting fleet you wish to swap in']

            ship_list = {}

            for emoji_to_send in waiting_fleet:
                lines.append(
                    "{}: Column {}: {}".format(
                        emoji_to_send,
                        waiting_fleet[emoji_to_send],
                        fleet.where_number(waiting_fleet[emoji_to_send])
                    )
                )

            message = await channel.send(
                "\n".join(lines)
            )

            swap_react, _ = await bot.wait_for(
                'reaction_add',
                check=reaction_check(
                    message,
                    user_to_mention,
                    ship_list
                )
            )

            to_swap_in = ship_list[swap_react.emoji]

        fleet.swap_columns(emojis_to_add[react.emoji], to_swap_in)
        await channel.send(
            '{} swapped {} with {}'.format(
                user_to_mention.mention,
                emojis_to_add[react.emoji],
                to_swap_in
            )
        )


bot.run(TOKEN)

# Local Variables:
# jedi:environment-root: "bot_heard_round"
# End:
