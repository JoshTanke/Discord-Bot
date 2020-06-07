from absl import app
from absl import flags
import traceback
from typing import List, Optional, Tuple
import sys
import asyncio
import time
import json

import discord
from discord.ext import commands
from team_generator import TeamGenerator, Rank

print(discord.__file__)

FLAGS = flags.FLAGS
flags.DEFINE_integer("seed", 10, "Seed to use when generating random teams.")


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
		author, channel, content = message.author, message.channel, message.content
		if content.startswith(_COMMAND_PREFIX):
			command = content.split(_COMMAND_PREFIX)[1]
			response = await self._process_command(command, author)
			if response:
				await channel.send(response)

	async def on_error(event, *args, **kwargs):
		error_message = sys.exc_info()[1]
		channel = args[1].channel
		await channel.send(error_message)

	async def _process_command(self, command: str, author: discord.member.Member) -> Optional[str]:
		stripped = command.strip()
		split = [s.lower() for s in command.split(' ') if s]
		command_type = split[0]
		args = tuple(arg for arg in split[1:] if not arg.startswith('--'))
		flags = tuple(f.strip('--') for f in split[1:] if f.startswith('--'))
		if command_type == 'build':
			return self._build_player_list_from_channel(author.voice.channel, args, flags)
		elif command_type == 'list':
			return self._list(args, flags)
		elif command_type == 'clear':
			return self._clear(args, flags)
		elif command_type == 'add':
			return self._add(args, flags)
		elif command_type == 'remove':
			return self._remove(args, flags)
		elif command_type == 'generate' or command_type == 'gen':
			return self._generate(args, flags)
		# elif command_type == 'listen':
		# 	return await self._listen(author.voice.channel, args, flags)
		raise ValueError(f'Unsupported command: {command_type}')

	def _build_player_list_from_channel(self, channel: discord.channel.VoiceChannel, args: Tuple[str], flags: Tuple[str]):
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

	def _list(self, args: Tuple[str], flags: Tuple[str]):
		players = self.team_generator.list_players()
		if players:
			if 'include_rank' in flags:
				return ' | '.join([f'{p.name}: {p.rank.name.title()}' for p in players])
			return ' | '.join([str(p) for p in players]) 
		return 'Players list is empty.'

	def _clear(self, args: Tuple[str], flags: Tuple[str]):
		self.team_generator.clear_players()
		return 'Players list cleared.'

	def _add(self, args: Tuple[str], flags: Tuple[str]):
		if len(args) != 2:
			return f'Expected 2 arguments, got: {args}'
		player_name, rank_name = args
		if rank_name not in _RANKS:
			return f'Unsupported rank: {rank_name}'
		rank = _RANKS[rank_name]
		result = self.team_generator.add_player(player_name, rank)
		if result:
			return f'Successfully added {player_name.title()}'
		return f'Failed to add {player_name.title()}'


	def _remove(self, args: Tuple[str], flags: Tuple[str]):
		if len(args) != 1:
			return f'Expected 1 argument, got: {args}'
		player_name = args[0]
		result = self.team_generator.remove_player(player_name)
		if result:
			return f'Successfully removed {player_name.title()}'
		return f'Failed to remove {player_name.title()}'

	def _generate(self, args: Tuple[str], flags: Tuple[str]):
		check_length = 'force' not in flags
		teams = self.team_generator.generate(check_length=check_length)
		return teams

	# async def _listen(self, channel: discord.channel.VoiceChannel, args: Tuple[str], flags: Tuple[str]):
	# 	voice_client = await channel.connect()
	# 	t_end = time.time() + 10
	# 	while time.time() < t_end:
	# 		msg = await voice_client.ws.recv()
	# 		print(msg)
	# 		time.sleep(1)
	# 	await voice_client.disconnect()


def main(argv):
	del argv  # Unused.
	with open('client_secret.json', 'r') as f:
		token = json.load(f).get('Token')
	client = ValorantTeamsClient(FLAGS.seed)
	client.run(token)


if __name__ == '__main__':
  app.run(main)
