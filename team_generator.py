import enum
from dataclasses import dataclass
from typing import List, Optional

import numpy as np



_TEAM_DISPLAY_TEMPLATE = """
Team A: {team_a}, Team Score: {team_a_score}
Team B: {team_b}, Team Score: {team_b_score}
"""


class Rank(enum.Enum):
	IRON = 0.5
	BRONZE = 1.0
	SILVER = 1.5
	GOLD = 2.0
	PLATINUM = 3.5 
	DIAMOND = 5.0


@dataclass
class Player(object):
	'''Class for tracking Valorant players.'''
	name: str
	rank: Rank
	
	def __truediv__(self, other):
		if isinstance(other, self.__class__):
			return self.rank.value / other.rank.value
		elif isinstance(other, int) or isinstance(other, float):
			return self.rank.value / other
		raise TypeError(f'Unsupported type for division: {type(other)}')

	def __eq__(self, other):
		if isinstance(other, self.__class__):
			return self.name.lower() == other.name.lower()
		return False

	def __lt__(self, other):
		if self.rank.value == other.rank.value:
			return self.name < other.name
		return self.rank.value < other.rank.value	

	def __repr__(self):
		return self.name

class TeamGenerator(object):

	def __init__(self, random_seed: Optional[int] = None):
		if random_seed: np.random.seed(random_seed)
		self.players = []

	def generate(self, check_length: bool = True) -> str:
		if check_length and len(self.players) != 10:
			raise ValueError(f'Can only match 10 players. Currently have {len(self.players)}.')
		if len(self.players) % 2 != 0:
			raise ValueError(f'Must have an even number of players. Currently have {len(self.players)}.')

		temp_players = self.players.copy()
		team_a, team_b = [], []
		while temp_players:
			team_a.append(self._poll(temp_players))
			team_b.append(self._poll(temp_players))
			team_a = sorted(team_a, reverse=True)
			team_b = sorted(team_b, reverse=True)
		team_a_score = self._evaluate_team(team_a)
		team_b_score = self._evaluate_team(team_b)
		return _TEAM_DISPLAY_TEMPLATE.format(
			team_a=team_a,
			team_a_score=team_a_score,
			team_b_score=team_b_score,
			team_b=team_b)

	def add_player(self, player_name: str, rank: Rank) -> bool:
		if len(self.players) == 10:
			raise ValueError(f'Players list is full.')
			return False
		player = Player(player_name, rank)
		if player in self.players:
			raise ValueError(f'{player_name.title()} is already added.')
			return False
		self.players.append(player)
		return True

	def remove_player(self, player_name: str) -> bool:
		for p in self.players:
			if p.name.lower() == player_name.lower():
				self.players.remove(p)
				return True
		return False

	def list_players(self) -> List[Player]:
		return sorted(self.players, reverse=True)

	def clear_players(self):
		self.players = []

	def _poll(self, players: List[Player]) -> Player:
		total = sum([p.rank.value for p in players])
		probs = list(np.array(players) / total)
		index = np.random.choice(range(len(players)), size=1, replace=False, p=probs)[0]
		return players.pop(index)

	def _evaluate_team(self, team: List[Player]) -> float:
		return np.round(sum([p.rank.value for p in team]), decimals=2)