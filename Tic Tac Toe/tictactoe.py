from enum import Enum
from abc import ABC, abstractmethod
from typing import Dict, List
import threading

class Symbol(Enum):
    X = 'X'
    O = 'O'
    EMPTY = '_'

    def get_char(self):
        return self.value
    
class Player:
    def __init__(self, name: str, symbol: Symbol):
        self.name = name
        self.symbol = symbol

    def get_name(self):
        return self.name
    
    def get_symbol(self):
        return self.symbol
    
class InvalidMoveException(Exception):
    def __init__(self, message):
        super().__init__(message)
    
class Cell:
    def __init__(self):
        self.symbol = Symbol.EMPTY

    def get_symbol(self):
        return self.symbol
    
    def set_symbol(self, symbol: Symbol):
        self.symbol = symbol

class Board:
    def __init__(self, size: int):
        self.size = size
        self.board: List[List[Cell]] = []
        self.moves_count = 0
        self.initialize_board()

    def initialize_board(self):
        for row in range(self.size):
            board_row = []
            for col in range(self.size):
                board_row.append(Cell())
            self.board.append(board_row)

    def place_symbol(self, row: int, col: int, symbol: Symbol):
        if row<0 or row >=self.size or col<0 or col>=self.size:
            raise InvalidMoveException("Invalid poistions. Out of bounds")
        if self.board[row][col].get_symbol() != Symbol.EMPTY:
            raise InvalidMoveException("Invlaid position cell is already oocupied")
        self.board[row][col].set_symbol(symbol)

    def get_cell(self, row: int, col: int):
        if row<0 or row >=self.size or col<0 or col>=self.size:
            return None
        return self.board[row][col]
    
    def is_full(self):
        return self.moves_count == self.size * self.size
    
    def get_size(self):
        return self.size
    
    def print_board(self):
        print("------------")
        for i in range(self.size):
            print("| ", end = "")
            for j in range(self.size):
                symbol = self.board[i][j].get_symbol()
                print(f"{symbol.get_char()} | ", end="")
            print()
        print("------------")

    def increment_moves_count(self):
        self.moves_count +=1

class WinningStrategy(ABC):
    @abstractmethod
    def check_winner(self, board: Board, player: Player):
        pass

class RowWinningStrategy(WinningStrategy):
    def check_winner(self, board: Board, player: Player):
        for row in range(board.get_size()):
            row_win = True
            for col in range(board.get_size()):
                if board.get_cell(row, col).get_symbol() != player.get_symbol():
                    row_win = False
                    break
            if row_win:
                return True
        return False
    
class ColumnWinningStrategy(WinningStrategy):
    def check_winner(self, board: Board, player: Player):
        for col in range(board.get_size()):
            col_win = True
            for row in range(board.get_size()):
                if board.get_cell(row, col).get_symbol() != player.get_symbol():
                    col_win = False
                    break
            if col_win:
                return True
        return False
    
class DiagonalWinningStrategy(WinningStrategy):
    def check_winner(self, board: Board, player: Player):
        main_diag_win = True
        for i in range(board.get_size()):
            if board.get_cell(i,i).get_symbol() != player.get_symbol():
                main_diag_win = False
                break
        if main_diag_win:
            return True

        anti_diag_win = True
        for i in range(board.get_size()):
            if board.get_cell(i,board.get_size() - i - 1).get_symbol() != player.get_symbol():
                anti_diag_win = False
                break
        if anti_diag_win:
            return True
        return False
        
class GameStatus(Enum):
    IN_PROGRESS = "IN_PROGRESS"
    WINNER_X = "WINNER_X"
    WINNER_O = "WINNER_O"
    DRAW = "DRAW"

class GameObserver(ABC):
    @abstractmethod
    def update(self, game):
        pass

class GameSubject(ABC):
    def __init__(self):
        self.observers: List[GameObserver] = []

    def add_observer(self, observer: GameObserver):
        self.observers.append(observer)

    def remove_observer(self, observer: GameObserver):
        self.observers.remove(observer)

    def notify_observer(self):
        for observer in self.observers:
            observer.update(self)

class GameState(ABC):
    @abstractmethod
    def handle_move(self, game: 'Game', player: Player, row: int, col: int):
        pass

class InProgressState(GameState):
    def handle_move(self, game: 'Game', player: Player, row: int, col:int):
        #First define the game class now and then come back to this function
        if game.get_current_player() != player:
            raise InvalidMoveException("Not your turn")
        
        game.get_board().place_symbol(row, col, player.get_symbol())
        game.get_board().increment_moves_count()
        
        # Check for a winner or a draw
        if game.check_winner(player):
            game.set_winner(player)
            game.set_status(GameStatus.WINNER_X if player.get_symbol() == Symbol.X else GameStatus.WINNER_O)
            game.set_state(WinnerState())
        elif game.get_board().is_full():
            game.set_status(GameStatus.DRAW)
            game.set_state(DrawState())
        else:
            # If the game is still in progress, switch players
            game.switch_player()

class DrawState(GameState):
    def handle_move(self, game, player: Player, row: int, col: int):
        raise InvalidMoveException("Game is already over. It was a draw.")


class WinnerState(GameState):
    def handle_move(self, game, player: Player, row: int, col: int):
        raise InvalidMoveException(f"Game is already over. {game.get_winner().get_name()} has won.")
        
class Game(GameSubject):
    def __init__(self, player1: Player, player2: Player):
        super().__init__()
        self.board = Board(3)
        self.player1 = player1
        self.player2 = player2
        self.current_player = self.player1
        self.winner = None
        self.status = GameStatus.IN_PROGRESS
        self.state = InProgressState()
        self.winning_strategy: List[WinningStrategy] = [
            RowWinningStrategy(),
            ColumnWinningStrategy(),
            DiagonalWinningStrategy()
        ]

    def make_move(self, player: Player, row: int, col: int):
        self.state.handle_move(self, player, row, col)

    def check_winner(self, player: Player):
        for strategy in self.winning_strategy:
            if strategy.check_winner(self.board, player):
                return True
        return False
    
    def switch_player(self):
        self.current_player = self.player2 if self.current_player == self.player1 else self.player1

    def get_board(self):
        return self.board
    
    def get_current_player(self):
        return self.current_player
    
    def get_winner(self):
        return self.winner

    def set_winner(self, winner: Player):
        self.winner = winner

    def get_status(self):
        return self.status
    
    def set_status(self, status: GameStatus):
        self.status = status
        if self.status != GameStatus.IN_PROGRESS:
            self.notify_observer()

    def set_state(self, state: GameState):
        self.state = state


class ScoreBoard(GameObserver):
    def __init__(self):
        self.scores = {}

    def update(self, game: Game):
        if game.get_status() == GameStatus.DRAW:
            print(f"[Scoreboard] Game ends in a Draw !!")
        if game.get_winner() is not None:
            winner_name = game.get_winner().get_name()
            self.scores[winner_name] = self.scores.get(winner_name, 0) + 1
            print(f"[Scoreboard] {winner_name} wins! Their new score is {self.scores[winner_name]}.")

    def print_scores(self):
        print("\n--- Overall Scoreboard ---")
        if not self.scores:
            print("No games with a winner have been played yet.")
            return
        
        for player_name, score in self.scores.items():
            print(f"Player: {player_name:<10} | Wins: {score}")
        print("--------------------------\n")

        
class TicTacToeSystem:
    _instance = None
    _lock = threading.Lock()

    def __new__(cls):
        if cls._instance is None:
            with cls._lock:
                if cls._instance is None:
                    cls._instance = super().__new__(cls)
        return cls._instance
    
    def __init__(self):
        if not hasattr(self, 'initialized'):
            self.game = None
            self.scoreboard = ScoreBoard()
            self.initialized = True

    @classmethod
    def get_instance(cls):
        return cls()
    
    def create_game(self, player1: Player, player2: Player):
        self.game = Game(player1, player2)
        self.game.add_observer(self.scoreboard)

        print(f"Game started between {player1.get_name()} (X) and {player2.get_name()} (O).")

    def print_board(self):
        self.game.get_board().print_board()
    
    def print_score_board(self):
        self.scoreboard.print_scores()

    def make_move(self, player: Player, row: int, col: int):
        if self.game is None:
            print("No game is in progress, Please create a game first")
            return
        try:
            print(f"{player.get_name()} playes at ({row}, {col})")
            self.game.make_move(player, row, col)
            self.print_board()
            print(f"Game status: {self.game.get_status().value}")
            if self.game.get_winner() is not None:
                print(f"Winner: {self.game.get_winner().get_name()}")
        except InvalidMoveException as e:
            print(f"Error: {e}")

class TicTacToeDemo:
    @staticmethod
    def main():
        system = TicTacToeSystem.get_instance()
        
        alice = Player("Alice", Symbol.X)
        bob = Player("Bob", Symbol.O)
        
        # --- GAME 1: Alice wins ---
        print("--- GAME 1: Alice (X) vs. Bob (O) ---")
        system.create_game(alice, bob)
        system.print_board()
        
        system.make_move(alice, 0, 0)
        system.make_move(bob, 1, 0)
        system.make_move(alice, 0, 1)
        system.make_move(bob, 1, 1)
        system.make_move(alice, 0, 2)  # Alice wins, scoreboard is notified
        print("----------------------------------------\n")
        
        # --- GAME 2: Bob wins ---
        print("--- GAME 2: Alice (X) vs. Bob (O) ---")
        system.create_game(alice, bob)  # A new game instance
        system.print_board()
        
        system.make_move(alice, 0, 0)
        system.make_move(bob, 1, 0)
        system.make_move(alice, 0, 1)
        system.make_move(bob, 1, 1)
        system.make_move(alice, 2, 2)
        system.make_move(bob, 1, 2)  # Bob wins, scoreboard is notified
        print("----------------------------------------\n")
        
        # --- GAME 3: A Draw ---
        print("--- GAME 3: Alice (X) vs. Bob (O) - Draw ---")
        system.create_game(alice, bob)
        system.print_board()
        
        system.make_move(alice, 0, 0)
        system.make_move(bob, 0, 1)
        system.make_move(alice, 0, 2)
        system.make_move(bob, 1, 1)
        system.make_move(alice, 1, 0)
        system.make_move(bob, 1, 2)
        system.make_move(alice, 2, 1)
        system.make_move(bob, 2, 0)
        system.make_move(alice, 2, 2)  # Draw, scoreboard is not notified of a winner
        print("----------------------------------------\n")
        
        # --- Final Scoreboard ---
        # We get the scoreboard from the system and print its final state
        system.print_score_board()


if __name__ == "__main__":
    TicTacToeDemo.main()