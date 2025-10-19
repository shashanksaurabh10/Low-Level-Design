#Requirenments

# 1. The game should be a played on a board with numbered cells, typically with 100 cells
# 2. The board should have predefined set of snakes and ladders connecting certain cells
# 3. The game should support multiple players, each represented by a unique game piece.
# 4. Player should take turns rolling a dice to determine the number of cells to move forward.
# 5. If a player lands on a cell with the head of a snake, they should slide down to the cell with the tail of the snake.
# 6. If a player lands on a cell with a base of a ladder, they should climb up to the cell at the top of the ladder.
# 7. The game should continue until one of the players reaches the final cell of the board.
# 8. The game should handle multiple game sessions concurrently, allowing different groups to play independently.

from typing import List
from abc import ABC
import random
from enum import Enum
from collections import deque

class Player:
    def __init__(self, name: str):
        self.name = name
        self.position = 0

    def get_name(self):
        return self.name
    
    def get_position(self):
        return self.position
    
    def set_position(self, position: int):
        self.position = position

class Dice:
    def __init__(self, min_value: int, max_value: int):
        self.min_value = min_value
        self.max_value = max_value

    def roll(self):
        return int(random.random() * (self.max_value - self.min_value + 1) + self.min_value)

class BoardEntity(ABC):
    def __init__(self, start: int, end: int):
        self.start = start
        self.end = end

    def get_start(self):
        return self.start
    
    def get_end(self):
        return self.end
    
class Ladder(BoardEntity):
    def __init__(self, start: int, end: int):
        super().__init__(start, end)
        if start >= end:
            raise ValueError("Ladder bottom must be at a lower position than its top.")
        
class Snake(BoardEntity):
    def __init__(self, start: int, end: int):
        super().__init__(start, end)
        if start <= end:
            raise ValueError("Snake head must be at a higher position than its tail.")
        
class GameStatus(Enum):
    NOT_STARTED = "NOT_STARTED"
    RUNNING = "RUNNING"
    FINISHED = "FINISHED"

class Board:
    def __init__(self, size: int, entities: List[BoardEntity]):
        self.size = size
        self.snakes_and_ladders = {}

        for entity in entities:
            self.snakes_and_ladders[entity.get_start()] = entity.get_end()

    def get_size(self):
        return self.size
    
    def get_final_position(self, position: int):
        return self.snakes_and_ladders.get(position, position)
    
class Game:
    class Builder:
        def __init__(self):
            self.board = None
            self.players = None
            self.dice = None

        def set_board(self, board_size: int, board_entities: List[BoardEntity]):
            self.board = Board(board_size, board_entities)
            return self
        
        def set_players(self, player_names: List[str]):
            self.players = deque()
            for player_name in player_names:
                self.players.append(Player(player_name))
            return self
        
        def set_dice(self, dice: Dice):
            self.dice = dice
            return self
        
        def build(self):
            if self.board is None or self.players is None or self.dice is None:
                raise ValueError("Board, players and dice must be set")
            return Game(self)
        
    def __init__(self, builder: 'Game.Builder'):
        self.board = builder.board
        self.players = deque(builder.players)
        self.dice = builder.dice
        self.status = GameStatus.NOT_STARTED
        self.winner = None

    def play(self):
        if len(self.players) < 2:
            print("Cannot start game. At least 2 players are required.")
            return
        
        self.status = GameStatus.RUNNING
        print("Game started")

        while self.status == GameStatus.RUNNING:
            current_player = self.players.popleft()
            self.take_turn(current_player)

            if self.status == GameStatus.RUNNING:
                self.players.append(current_player)

        print("Game Finished")
        if self.winner is not None:
            print(f"The winner is {self.winner.get_name()}!")

    def take_turn(self, player: Player):
        roll = self.dice.roll()
        print(f"\n{player.get_name()}'s turn. Rolled a {roll}.")

        current_position = player.get_position()
        next_position = current_position + roll

        if next_position > self.board.get_size():
            print(f"Oops, {player.get_name()} needs to land exactly on {self.board.get_size()}. Turn skipped.")
            return

        if next_position == self.board.get_size():
            player.set_position(next_position)
            self.winner = player
            self.status = GameStatus.FINISHED
            print(f"Hooray! {player.get_name()} reached the final square {self.board.get_size()} and won!")
            return
        
        final_position = self.board.get_final_position(next_position)

        if final_position > next_position:  # Ladder
            print(f"Wow! {player.get_name()} found a ladder 🪜 at {next_position} and climbed to {final_position}.")
        elif final_position < next_position:  # Snake
            print(f"Oh no! {player.get_name()} was bitten by a snake 🐍 at {next_position} and slid down to {final_position}.")
        else:
            print(f"{player.get_name()} moved from {current_position} to {final_position}.")

        player.set_position(final_position)
        
        if roll == 6:
            print(f"{player.get_name()} rolled a 6 and gets another turn!")
            self.take_turn(player)

class SnakeAndLadderDemo:
    @staticmethod
    def main():
        board_entities = [
            Snake(17, 7), Snake(54, 34),
            Snake(62, 19), Snake(98, 79),
            Ladder(3, 38), Ladder(24, 33),
            Ladder(42, 93), Ladder(72, 84)
        ]
        
        players = ["Alice", "Bob", "Charlie"]
        
        game = Game.Builder() \
            .set_board(100, board_entities) \
            .set_players(players) \
            .set_dice(Dice(1, 6)) \
            .build()
        
        game.play()


if __name__ == "__main__":
    SnakeAndLadderDemo.main()