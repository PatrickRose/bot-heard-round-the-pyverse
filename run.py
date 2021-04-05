# bot.py
import datetime
import json
import math
import os
import random
import re
import base64
import json
import enum

import discord
import tabulate
from discord.ext import commands
from dotenv import load_dotenv

intents = discord.Intents.default()
intents.members = True

load_dotenv()
TOKEN = os.getenv('DISCORD_TOKEN')

command_prefix = os.getenv('COMMAND_PREFIX', '!!')
bot = commands.Bot(command_prefix=command_prefix, intents=intents)
combat_category_name='combat'
attack_defend_regex = re.compile('(Attacker|Defender): `(.+)`')
round_regex = re.compile('`!!! Combat status( - round (\d)| - finished)? !!!`')
fleet_list_regex = re.compile('(Attacker|Defender) ships to apply: (.+)')
ship_regex = re.compile('`(.+?) \\((\w+) (\d+)/(\d+)\\)`')
bot_master_role = 'bot-master'

class ShipType(enum.Enum):
    CRUISER='Cruiser'
    FIGHTER='Fighter'

class Ship:

    def __init__(self, name: str, max_health: int, current_health: int, ship_type: ShipType):
        self.name = name
        self.max_health = max_health
        self.current_health = current_health
        self.ship_type = ship_type

    def __str__(self):
        return '{} ({} {}/{})'.format(
            self.name,
            self.ship_type,
            self.max_health,
            self.current_health
        )

class CombatRound(enum.Enum):
    PENDING=0,
    MISSILE_ONE=1,
    MISSILE_TWO=2,
    RAILGUN=3
    FINISHED=4

class CombatColumn(enum.Enum):
    WAITING='waiting'
    LEFT='left'
    MIDDLE='middle'
    RIGHT='right'

class Position:

    def __init__(self, combat_column: CombatColumn, position: int):
        self.combat_column = combat_column
        self.position = position

class FleetList:

    def __init__(self, ships: list[tuple[Ship,Position]] = None):
        if ships is None:
            ships = []

        self.ships = ships

    def where_column(self, column: CombatColumn):
        return list(
            filter(
                lambda x: x[1].combat_column == column,
                self.ships
            )
        )

    def move_ship(self, ship: Ship, column: CombatColumn):
        ships_in_column = self.where_column(column)

        if ships_in_column:
            position = max([x[1].position for x in ships_in_column])+1
        else:
            position = 0

        for curr_ship in self.ships:
            if curr_ship[0] == ship:
                curr_ship[1] = Position(column, position)
                break
            

    def add_ship(self, ship: Ship, position: Position):
        self.ships.append((ship, position))

    @classmethod
    def from_list(cls, fleet: list):
        ships = []

        for ship_def in fleet:
            ship = Ship(ship_def["name"], ship_def["max_health"], ship_def["current_health"], ship_def["type"])
            position = Position(CombatColumn.WAITING, -1)
            ships.append((ship,position))

        return FleetList(ships)


class CombatStatus:

    def __init__(self, attacker: discord.User, defender: discord.User, attacker_fleet=None, defender_fleet=None, combat_round=CombatRound.PENDING):
        if attacker_fleet is None:
            attacker_fleet = FleetList()
        if defender_fleet is None:
            defender_fleet = FleetList()

        self.attacker = attacker
        self.defender = defender
        self.attacker_fleet = attacker_fleet
        self.defender_fleet = defender_fleet
        self.combat_round = combat_round

    def add_fleet_for(self, user: discord.User, fleet: list):
        if user.id == self.attacker.id:
            self.attacker_fleet = FleetList.from_list(fleet)
        else:
            self.defender_fleet = FleetList.from_list(fleet)


    def __str__(self):
        attacker = self.attacker.nick or self.attacker.name
        defender = self.defender.nick or self.defender.name

        attacker_fleet_waiting = self.attacker_fleet.where_column(CombatColumn.WAITING)

        defender_fleet_waiting = self.defender_fleet.where_column(CombatColumn.WAITING)

        attacker_fleet_waiting.sort(
            key=lambda x: x[0].name
        )

        defender_fleet_waiting.sort(
            key=lambda x: x[0].name
        )

        if self.combat_round == CombatRound.PENDING:
            status = "`!!! Combat status !!!`"
        elif self.combat_round == CombatRound.MISSILE_ONE:
            status = "`!!! Combat status - round 1 !!!`"
        elif self.combat_round == CombatRound.MISSILE_TWO:
            status = "`!!! Combat status - round 2 !!!`"
        elif self.combat_round == CombatRound.RAILGUN:
            status = "`!!! Combat status - round 3 !!!`"
        else:
            status = "`!!! Combat status - finished !!!`"

        rows = [
            status,
            "Attacker: `{}`".format(attacker),
            "Defender: `{}`".format(defender)
        ]

        if attacker_fleet_waiting:
            rows.append(
                "Attacker ships to apply: {}".format(
                    ', '.join(['`{}`'.format(str(x[0])) for x in attacker_fleet_waiting])
                )
            )

        if defender_fleet_waiting:
            rows.append(
                "Defender ships to apply: {}".format(
                    ', '.join(['`{}`'.format(str(x[0])) for x in defender_fleet_waiting])
                )
            )

        attacker_fleet_ready = self.attacker_fleet.where_column(CombatColumn.MIDDLE)
        defender_fleet_ready = self.defender_fleet.where_column(CombatColumn.MIDDLE)

        if attacker_fleet_ready or defender_fleet_ready:

            attacker_fleet_ready.sort(key=lambda x: x[1].position, reverse=True)
            defender_fleet_ready.sort(key=lambda x: x[1].position)

            rows.append(
                '```\n' + tabulate.tabulate(
                    [str(x[0]) for x in attacker_fleet_ready] + ['------'] + [str(x[0]) for x in defender_fleet_ready]
                ) + '\n```'
            )
        

        return "\n".join(rows)

    def ready_for_combat(self):
        return self.attacker_fleet.ships and self.defender_fleet.ships

    @classmethod
    async def from_message(cls, message: discord.Message):
        content = message.content
        attacker: discord.User
        defender: discord.User
        defender_ships = FleetList()
        attacker_ships = FleetList()

        members = await message.guild.fetch_members().flatten()

        for line in content.split("\n"):

            match = round_regex.match(line)
            if match:
                if match.group(2) is None:
                    combat_round = CombatRound.PENDING if match.group(1) is None else CombatRound.FINISHED
                else:
                    combat_round = [
                        'EMPTY',
                        CombatRound.MISSILE_ONE,
                        CombatRound.MISSILE_TWO,
                        CombatRound.RAILGUN
                    ][int(match.group(2))]


            match = attack_defend_regex.match(line)

            if match:
                attack_defend = match.group(1)
                name_nick = match.group(2)

                user = discord.utils.get(members, nick=name_nick)

                if not user:
                    user = discord.utils.get(members, name=name_nick)

                if not user:
                    raise ValueError('Could not find user with name/nickname {}'.format(name_nick))

                if attack_defend == 'Attacker':
                    attacker = user
                else:
                    defender = user


            match = fleet_list_regex.match(line)

            if match:
                attack_defend = match.group(1)
                ships = match.group(2)
                if attack_defend == 'Attacker':
                    ship_list = attacker_ships
                else:
                    ship_list = defender_ships

                for group in ship_regex.finditer(ships):
                    ship = Ship(name=group[1], ship_type=group[2], current_health=group[3], max_health=group[4])

                    ship_list.add_ship(ship, Position(CombatColumn.WAITING, -1))


        return CombatStatus(attacker, defender, attacker_ships, defender_ships, combat_round=combat_round)

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
        return;

    defender = ctx.message.mentions[0]

    guild: discord.Guild = ctx.guild

    await ctx.send(
        'Starting combat, {} attacks {}...'.format(ctx.author.mention, target)
    );

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
        # Next, create the run-* role
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
    );

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

    decoded_fleet = base64.b64decode(fleet_list, validate=True)

    fleet_obj = json.loads(decoded_fleet)

    combat_status.add_fleet_for(user, fleet_obj)

    await message.edit(content=combat_status)

    await ctx.reply('Added your ships to the list')

    if combat_status.ready_for_combat():
        await start_combat_loop(message, combat_status)

async def start_combat_loop(message: discord.Message, combat_status: CombatStatus):
    channel = message.channel

    combat_status.combat_round = CombatRound.MISSILE_ONE

    await message.edit(content=combat_status)

    await channel.send('COMBAT HAS STARTED!')

    react_message: discord.Message = await channel.send('React to this message with :crossed_swords: to fight, or with :flag_white: to retreat')

    for emoji in ['⚔', '🏳']:
        await react_message.add_reaction(emoji)

    attack_react = await bot.wait_for(
        'reaction_add',
        check=lambda reaction,user: reaction.message == react_message and reaction.emoji in ['⚔', '🏳'] and user == combat_status.attacker
    )
    defend_react = await bot.wait_for(
        'reaction_add',
        check=lambda reaction,user: reaction.message == react_message and reaction.emoji in ['⚔', '🏳'] and user == combat_status.defender
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
            check=lambda reaction,user: reaction.message == attacker_ships_message and (reaction.emoji == '🚫' or reaction.emoji in ship_list) and user == combat_status.attacker
        ),
        await bot.wait_for(
            'reaction_add',
            check=lambda reaction,user: reaction.message == attacker_ships_message and (reaction.emoji == '🚫' or reaction.emoji in ship_list) and user == combat_status.attacker
        ),
        await bot.wait_for(
            'reaction_add',
            check=lambda reaction,user: reaction.message == attacker_ships_message and (reaction.emoji == '🚫' or reaction.emoji in ship_list) and user == combat_status.attacker
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
# jedi:environment-root: "bot-heard-round"
# End:
