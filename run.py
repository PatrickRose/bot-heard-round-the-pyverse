"""
Bot starter
"""
# bot.py
import os
import random

import discord
import emoji
from discord.ext import commands
from dotenv import load_dotenv

from bot_heard_round.combat_status import CombatRound, CombatStatus
from bot_heard_round.fleet import CombatColumn, FleetList

ONE_EMOJI = emoji.emojize(':one:', use_aliases=True)
TWO_EMOJI = emoji.emojize(':two:', use_aliases=True)
THREE_EMOJI = emoji.emojize(':three:', use_aliases=True)
FOUR_EMOJI = emoji.emojize(':four:', use_aliases=True)
FIVE_EMOJI = emoji.emojize(':five:', use_aliases=True)

LEFT_EMOJI = emoji.emojize(':regional_indicator_l:', use_aliases=True)
CENTRE_EMOJI = emoji.emojize(':regional_indicator_c:', use_aliases=True)
RIGHT_EMOJI = emoji.emojize(':regional_indicator_r:', use_aliases=True)

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
            except ValueError as e:
                print(e)
                return False

        return check

    attacker_fleet_msg = await bot.wait_for(
        'message',
        check=check_for_message(attacker)
    )

    await attacker_fleet_msg.reply('Importing fleet now...')
    combat_status.add_fleet_for(True, attacker_fleet_msg.content)

    ## TODO: INCLUDE PATROL MODE HERE

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
    def check_activated(reaction, user):
        return reaction.message == message \
               and reaction.emoji in valid_reactions \
               and user == expected_user

    return check_activated


async def request_ships(combat_status: CombatStatus, apply_attackers: bool):
    channel: discord.TextChannel = combat_status.message.channel
    user_to_respond = combat_status.attacker if apply_attackers else combat_status.defender
    fleet = combat_status.attacker_fleet if apply_attackers else combat_status.defender_fleet

    ship_list = {}
    ship_text = []

    possible_emojis = [
        ONE_EMOJI,
        TWO_EMOJI,
        THREE_EMOJI,
        FOUR_EMOJI,
        FIVE_EMOJI,
    ]

    for fleet_column in fleet.where_column(CombatColumn.WAITING):
        if not fleet_column.ships:
            continue

        emoji_to_send = possible_emojis[fleet_column.column_number - 1]

        ship_list[emoji_to_send] = fleet_column
        ship_text.append(
            "{}: Column {}: {}".format(emoji_to_send, fleet_column.column_number, fleet_column.ships_as_str))

    if not ship_text:
        await channel.send('No unassigned ships left in fleet, skipping {}'.format(user_to_respond.display_name))
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
        LEFT_EMOJI: CombatColumn.LEFT,
        CENTRE_EMOJI: CombatColumn.MIDDLE,
        RIGHT_EMOJI: CombatColumn.RIGHT
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
        CombatRound.MISSILE_TWO: 'Second round of combat. If nobody retreats Railgun combat will start!',
        CombatRound.RAIL_GUN: 'Final combat round. ALL DEFENCE WILL BE ZERO THIS ROUND',
    }

    for combat_round in messages:
        combat_status.combat_round = combat_round

        if combat_round != CombatRound.MISSILE_ONE:
            # TODO: Allow moving of combat columns
            pass

        await combat_status.update_message()

        await channel.send(messages[combat_round])

        react_message: discord.Message = await channel.send(
            'React to this message with :crossed_swords: to fight, or with :flag_white: to retreat'
        )

        for combat_emoji in ['⚔', '🏳']:
            await react_message.add_reaction(combat_emoji)

        attack_react, _ = await bot.wait_for(
            'reaction_add',
            check=reaction_check(react_message, combat_status.attacker, ['⚔', '🏳'])
        )
        defend_react, _ = await bot.wait_for(
            'reaction_add',
            check=reaction_check(react_message, combat_status.defender, ['⚔', '🏳'])
        )

        if '⚔' not in [attack_react.emoji, defend_react.emoji]:
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

    combat_status.combat_round = CombatRound.FINISHED
    await combat_status.update_message()


bot.run(TOKEN)

# Local Variables:
# jedi:environment-root: "bot_heard_round"
# End:
