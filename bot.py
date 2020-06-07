"""Simple Discord bot for handling Valorant Teams commands.
"""
import json
import sys
import time
import traceback
from typing import List, Optional, Tuple

from absl import app
from absl import flags
# import asyncio
import discord
from discord.ext import commands
from team_generator import TeamGenerator, Rank

FLAGS = flags.FLAGS
flags.DEFINE_integer('seed', 10, 'Seed to use when generating random teams.')
flags.DEFINE_string('token', None, 'The Client token to use for authorizing the bot.')
flags.mark_flag_as_required('token')


_COMMAND_PREFIX = './'

_RANKS = {
  'b': Rank.BRONZE,
  'bronze': Rank.BRONZE,
  'i': Rank.IRON,
  'iron': Rank.IRON,
  's': Rank.SILVER,
  'silver': Rank.SILVER,
  'g': Rank.GOLD,
  'gold': Rank.GOLD,
  'p': Rank.PLATINUM,
  'platinum': Rank.PLATINUM,
  'plat': Rank.PLATINUM,
  'd': Rank.DIAMOND,
  'diamond': Rank.DIAMOND,
}


class ValorantTeamsClient(discord.Client):

  def __init__(self, seed: Optional[int]):
    super().__init__()
    self.team_generator = TeamGenerator(random_seed=seed)
    self.channels = {}

  async def on_ready(self):
    print(f'Logged on as {self.user}!')

  async def on_message(self, message):
    if message.content.startswith(_COMMAND_PREFIX):
      command = message.content.split(_COMMAND_PREFIX)[1]
      response = await self._process_command(command, message.author)
      await message.channel.send(response)

  async def on_error(event, *args, **kwargs):
    error_message = sys.exc_info()[1]
    channel = args[1].channel
    await channel.send(error_message)

  async def _process_command(self, command: str, author: discord.member.Member) -> str:
    stripped = command.strip()
    split = [s for s in command.split(' ') if s]
    command_type = split[0]
    args = tuple(arg for arg in split[1:] if not arg.startswith('--'))
    flags = tuple(f.strip('--').lower() for f in split[1:] if f.startswith('--'))
    # TODO(Josh): Create Command abc class for handling command requests. 
    if command_type == 'add':
      return self._add(args, flags)
    elif command_type == 'build':
      return self._build_player_list_from_channel(author.voice.channel, args, flags)
    elif command_type == 'clear':
      return self._clear(args, flags)
    elif command_type == 'generate' or command_type == 'gen':
      return self._generate(args, flags)
    elif command_type == 'list':
      return self._list(args, flags)
    # TODO(Josh): Add support for voice commands.   
    # elif command_type == 'listen':
    #   return await self._listen(author.voice.channel, args, flags)
    elif command_type == 'remove':
      return self._remove(args, flags)
    raise ValueError(f'Unsupported command: {command_type}')

  def _add(self, args: Tuple[str], flags: Tuple[str]) -> str:
    if len(args) != 2:
      return f'Expected 2 arguments, got: {args}'
    player_name, rank_name = args
    if rank_name.lower() not in _RANKS:
      return f'Unsupported rank: {rank_name}'
    rank = _RANKS[rank_name.lower()]
    self.team_generator.add_player(player_name, rank)
    return f'Successfully added {player_name.title()}'

  def _clear(self, args: Tuple[str], flags: Tuple[str]) -> str:
    self.team_generator.clear_players()
    return 'Players list cleared.'

  def _build_player_list_from_channel(self, channel: discord.channel.VoiceChannel, args: Tuple[str], flags: Tuple[str]) -> str:
    succeeded, failed = [], []
    for member in channel.members:
      added = False
      for role in member.roles:
        if role.name.lower() in _RANKS:
          self.team_generator.add_player(member.name, _RANKS[role.name.lower()])
          added = True
      if added:
        succeeded.append(member.name)
      else:
        failed.append(member.name)
    return_string = ''
    if succeeded:
      return_string += f'Successfully added: {succeeded}'
    if failed:
      return_string += f'\nFailed to add: {failed}'
    return return_string 

  def _generate(self, args: Tuple[str], flags: Tuple[str]) -> str:
    ignore_length = 'force' in flags
    teams = self.team_generator.generate(ignore_length=ignore_length)
    return teams    

  def _list(self, args: Tuple[str], flags: Tuple[str]) -> str:
    players = self.team_generator.list_players()
    if players:
      if 'include_rank' in flags:
        return ' | '.join([f'{str(p)}: {p.rank.name.title()}' for p in players])
      return ' | '.join([str(p) for p in players]) 
    return 'Players list is empty.'

  # async def _listen(self, channel: discord.channel.VoiceChannel, args: Tuple[str], flags: Tuple[str]):
  #   voice_client = await channel.connect()
  #   t_end = time.time() + 10
  #   while time.time() < t_end:
  #     msg = await voice_client.ws.recv()
  #     print(msg)
  #     time.sleep(1)
  #   await voice_client.disconnect()

  def _remove(self, args: Tuple[str], flags: Tuple[str]) -> str:
    if len(args) != 1:
      return f'Expected 1 argument, got: {args}'
    player_name = args[0]
    self.team_generator.remove_player(player_name)
    return f'Successfully removed {player_name}'


def main(argv):
  del argv  # Unused.
  client = ValorantTeamsClient(FLAGS.seed)
  client.run(FLAGS.token)


if __name__ == '__main__':
  app.run(main)