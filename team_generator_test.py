"""Tests for team_generator.py
"""
import unittest

from team_generator import Rank, Player, TeamGenerator


class TestTeamGenerator(unittest.TestCase):

  def test_add_player(self):
    generator = TeamGenerator()
    players = [
      Player('Ben', Rank.PLATINUM),
      Player('David', Rank.PLATINUM),
      Player('Harinder', Rank.PLATINUM),
      Player('Josh', Rank.PLATINUM),
      Player('Christian', Rank.GOLD),
      Player('Harrison', Rank.GOLD),
      Player('Austin', Rank.SILVER),
      Player('Jesse', Rank.SILVER),
      Player('Justin', Rank.SILVER),
      Player('Seth', Rank.SILVER),
    ]
    for p in players[:-1]:
      generator.add_player(p.name, p.rank)

    with self.assertRaises(ValueError):
      generator.add_player('Josh', Rank.SILVER)

    generator.add_player(players[-1].name, players[-1].rank)
    with self.assertRaises(ValueError):
      generator.add_player('Bob', Rank.BRONZE)

    self.assertCountEqual(generator.list_players(), players)

  def test_remove_player(self):
    generator = TeamGenerator()
    players = [
      Player('Ben', Rank.PLATINUM),
      Player('David', Rank.PLATINUM),
      Player('Harinder', Rank.PLATINUM),
      Player('Josh', Rank.PLATINUM),
      Player('Christian', Rank.GOLD),
      Player('Harrison', Rank.GOLD),
      Player('Austin', Rank.SILVER),
      Player('Jesse', Rank.SILVER),
      Player('Justin', Rank.SILVER),
      Player('Seth', Rank.SILVER),
    ]
    for p in players:
      generator.add_player(p.name, p.rank)

    generator.remove_player('ben')
    self.assertCountEqual(generator.list_players(), players[1:])

  def test_generate(self):
    generator = TeamGenerator(random_seed=20)
    players = [
      Player('Ben', Rank.PLATINUM),
      Player('David', Rank.PLATINUM),
      Player('Harinder', Rank.PLATINUM),
      Player('Josh', Rank.PLATINUM),
      Player('Christian', Rank.GOLD),
      Player('Harrison', Rank.GOLD),
      Player('Austin', Rank.SILVER),
      Player('Jesse', Rank.SILVER),
      Player('Justin', Rank.SILVER),
      Player('Seth', Rank.SILVER),
    ]
    for p in players:
      generator.add_player(p.name, p.rank)

    team_a = [players[2], players[0], players[4], players[9], players[7]]
    team_a_score = 12.0
    team_b = [players[3], players[1], players[5], players[8], players[6]]
    team_b_score = 12.0

    expected = f'\nTeam A: {team_a}, Team Score: {team_a_score}\nTeam B: {team_b}, Team Score: {team_b_score}\n'
    got = generator.generate()
    self.assertEqual(expected, got)


if __name__ == '__main__':
  unittest.main()