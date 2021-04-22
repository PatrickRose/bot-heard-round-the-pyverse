# bot.py
import os
import random
import re

import discord
from discord.ext import commands
from dotenv import load_dotenv

from bot_heard_round.CombatColumn import CombatColumn
from bot_heard_round.CombatStatus import CombatRound, CombatStatus

intents = discord.Intents.default()
intents.members = True

load_dotenv()
TOKEN = os.getenv('DISCORD_TOKEN')

command_prefix = os.getenv('COMMAND_PREFIX', '!')
bot = commands.Bot(command_prefix=command_prefix, intents=intents)
combat_category_name = 'combat'
bot_master_role = 'bot-master'


@bot.event
async def on_ready():
    print(f'{bot.user.name} has connected to Discord!')


@bot.event
async def on_command_error(ctx, error):
    if isinstance(error, commands.errors.CheckFailure):
        await ctx.send('You do not have the correct role for this command.')
    elif isinstance(error, commands.errors.MissingRequiredArgument):
        await ctx.send(error)
    elif isinstance(error, commands.errors.CommandNotFound):
        await ctx.send("Unknown command - try {0}help to see the available commands".format(command_prefix))
        pass
    else:
        control = discord.utils.get(ctx.guild.roles, name=bot_master_role)

        await ctx.send(f'{control.mention} there was a problem running this command please investigate')
        raise error


control_role_name = 'Control' if os.getenv('UPPERCASE_CONTROL') else 'control'


@bot.command(
    name='start-combat',
)
async def start_combat(ctx: commands.context.Context, target: str):
    attacker = ctx.author

    if len(ctx.message.mentions) == 0:
        await ctx.reply("Please use the mention format (ie `@person-to-attack`)")
        return
    elif len(ctx.message.mentions) > 1:
        await ctx.reply("Only allowed to attack one person")
        return

    defender = ctx.message.mentions[0]

    guild: discord.Guild = ctx.guild

    await ctx.send(
        'Starting combat, {} attacks {}...'.format(ctx.author.mention, target)
    )

    category: discord.CategoryChannel = discord.utils.get(guild.categories, name='combat')

    control = discord.utils.get(guild.roles, name=control_role_name)

    if not category:
        category = await guild.create_category(
            combat_category_name,
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

    status = await channel.send(combat_status)
    await status.pin()

    await channel.send(
        'Combat started, {} attacks {}\nPlease use the `{}fleet-list` command to import your fleet'.format(
            attacker.mention,
            defender.mention,
            command_prefix
        )
    )


@bot.command(
    name='clear-combat',
)
@commands.has_role(control_role_name)
async def clear_combat(ctx: commands.context.Context):
    guild = ctx.guild

    category = discord.utils.get(guild.categories, name=combat_category_name)

    if not category:
        return

    channels = category.text_channels
    await ctx.reply(f'Deleting {len(channels)} channels, please wait...')

    channel: discord.TextChannel
    for channel in channels:
        await channel.delete()

    await ctx.reply('Done!')


async def combat_status_from_context(ctx: commands.context.Context):
    channel: discord.TextChannel = ctx.channel
    pins = await channel.pins()
    if not pins:
        raise ValueError('No pinned message found, did you run this in a combat channel?')
    message: discord.Message = pins[0]

    return (message, await CombatStatus.from_message(message))


@bot.command(name='fleet-list')
async def add_fleet_list(ctx: commands.context.Context, fleet_list: str):
    try:
        message, combat_status = await combat_status_from_context(ctx)
    except ValueError as e:
        await ctx.reply(
            '{} - tag `@{}` if you need help'.format(
                e.args[0],
                bot_master_role
            )
        )
        return

    # if combat_status.combat_round != CombatRound.PENDING:
    #     await ctx.reply(
    #         'Combat has started! You can\'t change your fleet!'
    #     )
    #     return

    user = ctx.author

    combat_status.add_fleet_for(user, fleet_list)

    await message.edit(content=combat_status)

    await ctx.reply('Added your ships to the list')

    if combat_status.ready_for_combat():
        await start_combat_loop(message, combat_status)


async def start_combat_loop(message: discord.Message, combat_status: CombatStatus):
    channel = message.channel

    combat_status.combat_round = CombatRound.MISSILE_ONE

    await message.edit(content=combat_status)

    await channel.send('COMBAT HAS STARTED!')

    react_message: discord.Message = await channel.send(
        'React to this message with :crossed_swords: to fight, or with :flag_white: to retreat')

    for emoji in ['⚔', '🏳']:
        await react_message.add_reaction(emoji)

    attack_react = await bot.wait_for(
        'reaction_add',
        check=lambda reaction, user: reaction.message == react_message and reaction.emoji in ['⚔',
                                                                                              '🏳'] and user == combat_status.attacker
    )
    defend_react = await bot.wait_for(
        'reaction_add',
        check=lambda reaction, user: reaction.message == react_message and reaction.emoji in ['⚔',
                                                                                              '🏳'] and user == combat_status.defender
    )

    if '⚔' not in [attack_react[0].emoji, defend_react[0].emoji]:
        combat_status.combat_round = CombatRound.FINISHED
        await message.edit(content=combat_status)
        await channel.send('Both players have retreated, combat finished')
        return

    await channel.send('Combat will continue for another round')

    ship_list = {}
    ship_text = []

    possible_emojis = [
        '🤖', '👽', '👻'
    ]

    for ship in combat_status.attacker_fleet.where_column(CombatColumn.WAITING):
        emoji = possible_emojis[len(ship_list)]
        ship_list[emoji] = ship[0]
        ship_text.append("{}: {}".format(emoji, str(ship[0])))

    ## Ask the attacker to add 3 ships
    attacker_ships_message = await channel.send(
        "{}, please react to this with the ships you want to add. Choose 🚫 to stop adding\n{}".format(
            combat_status.attacker.mention,
            "\n".join(ship_text)
        )
    )

    await attacker_ships_message.add_reaction('🚫')

    for emoji in ship_list:
        await attacker_ships_message.add_reaction(emoji)

    activated = [
        await bot.wait_for(
            'reaction_add',
            check=lambda reaction, user: reaction.message == attacker_ships_message and (
                    reaction.emoji == '🚫' or reaction.emoji in ship_list) and user == combat_status.attacker
        ),
        await bot.wait_for(
            'reaction_add',
            check=lambda reaction, user: reaction.message == attacker_ships_message and (
                    reaction.emoji == '🚫' or reaction.emoji in ship_list) and user == combat_status.attacker
        ),
        await bot.wait_for(
            'reaction_add',
            check=lambda reaction, user: reaction.message == attacker_ships_message and (
                    reaction.emoji == '🚫' or reaction.emoji in ship_list) and user == combat_status.attacker
        )
    ]

    for ship in activated:
        emoji = ship[0].emoji
        if emoji in ship_list:
            combat_status.attacker_fleet.move_ship(ship_list[emoji], CombatColumn.MIDDLE)
            await channel.send('Moving ship {}'.format(str(ship_list[emoji])))

    await message.edit(content=combat_status)


bot.run(TOKEN)

# Local Variables:
# jedi:environment-root: "bot_heard_round"
# End:
