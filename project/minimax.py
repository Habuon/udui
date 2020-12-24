import sys
import random
from games import Reversi

infinity = 0
try:
    infinity = sys.maxint
except:
    infinity = sys.maxsize



################################### PLAYERS ###################################

class Player:
    def choose_move(self, game, state):
        raise NotImplementedError



class AskingPlayer(Player):
    def choose_move(self, game, state):
        # Asks user (human) which move to take. Useful for debug.
        actions = game.actions(state)
        print("Choose one of the following positions: {}".format(actions))
        game.display_state(state, True)
        return int(input('> '))



class RandomPlayer(Player):
    def choose_move(self, game, state):
        # Picks random move from list of possible ones.
        return random.choice(game.actions(state))


class MyPlayer(Player):
    def __init__(self):
        self.depth = 3
        self.game = None
        self.my_player = ""

    def choose_move(self, game, state):
        # set up self game  and self my player
        self.game = game
        self.my_player = game.player_at_turn(state)

        # starting as max finding best move
        alpha = best_value = -infinity
        best_turn = None
        for action in game.actions(state):
            state_after = game.state_after_move(state, action)
            value = self.min(state_after, alpha, infinity, self.depth)
            alpha = max(alpha, value)
            if value > best_value:
                best_value = value
                best_turn = action
        return best_turn

    # heuristic to estimate result for specific player
    def heuristic(self, state, player, coefficient=3):
        board = state['board']
        good = 0  # good tiles are those that are those in the corner or on the edge
        total = 0
        for r in range(len(board)):
            for c in range(len(board[r])):
                if board[r][c] == player:
                    if r in [0, len(board) - 1] and c in [0, len(board[0]) - 1]:  # corner
                        good += 2
                        continue
                    if r in [0, len(board) - 1]:  # only one edge
                        good += 1
                        continue
                    if c in [0, len(board[0]) - 1]:  # only one edge
                        good += 1
                        continue
                    total += 1

        result = total + good * coefficient
        return result if player == self.my_player else -result

    # max part of mini-max algorithm
    def max(self, state, alpha, beta, depth):
        if depth == 0:  # when we reach specific depth we will predict result
            return self.heuristic(state, self.my_player)
        best_val = -infinity
        actions = self.game.actions(state)
        if len(actions) == 0:  # when there is no more moves we return actual result
            return self.heuristic(state, self.my_player)
        for action in actions:
            state_after = self.game.state_after_move(state, action)
            value = self.min(state_after, alpha, beta, depth - 1)
            best_val = max(best_val, value)
            alpha = max(alpha, best_val)
            if beta <= alpha:
                break
        return best_val

    # min part of mini-max algorithm
    def min(self, state, alpha, beta, depth):
        if depth == 0:  # when we reach specific depth we will predict result
            return self.heuristic(state, self.game.other_player(self.my_player))
        best_val = infinity
        actions = self.game.actions(state)
        if len(actions) == 0:  # when there is no more moves we return actual result
            return self.heuristic(state, self.game.other_player(self.my_player))
        for action in actions:
            state_after = self.game.state_after_move(state, action)
            value = self.max(state_after, alpha, beta, depth - 1)
            best_val = min(best_val, value)
            beta = min(beta, best_val)
            if beta <= alpha:
                break
        return best_val


################################ MAIN PROGRAM #################################

if __name__ == '__main__':
    # Print all moves of the game? Useful for debugging, annoying if it`s already working.
    show_moves = True

    # Play single game
    # Reversi().play([RandomPlayer(), MyPlayer()], can_break_limit=[False, False], show_moves=show_moves)
    
    # Play N games
    Reversi().play_n_games([MyPlayer(), MyPlayer()], n=10, can_break_limit=[False, True])

