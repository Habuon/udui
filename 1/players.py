import random
from games import TicTacToe, Gomoku


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
    def choose_move(self, game, state):
        def terminal(game, state):
            for move in game.actions(state):
                next_state = game.state_after_move(state, move)
                if game.is_terminal(next_state):
                    return move
            return None

        def copy_dict(d):
            result = dict()
            for key in d:
                result[key] = d[key]
            return result

        def closest(game, state):
            my_icon = game.player_at_turn(state)
            board = game.board_in_state(state)
            closest = [game.w, None]
            for move in game.actions(state):
                r, c = game.idx_to_rc(move)
                for i in range(1, game.w - c):
                    for j in range(1, game.h - r):
                        if board[r + j][c + i] == my_icon:
                            d = int((i ** 2 + j ** 2) ** 0.5)  # distance
                            if d < closest[0]:
                                closest = [d, move]
            return closest[1]

        board = state["board"]
        my_icon = game.player_at_turn(state)
# if I can finish the game I ll do it
        t = terminal(game, state)
        if t is not None:
            return t
# If opponent can finish the game I ll block him/her/it
        opponent_state = copy_dict(state)
        opponent_state["player_on_turn"] = game.other_player(my_icon)

        t = terminal(game, opponent_state)
        if t is not None:
            return t

# try to get the middle one
        if board[game.h // 2][game.w // 2] == " ":
            return game.rc_to_idx(game.h // 2, game.w // 2)

# get the closest field
        c = closest(game, state)
        if c is not None:
            return c

        return game.actions(state)[0]


################################ MAIN PROGRAM #################################

if __name__ == '__main__':
    ## Print all moves of the game? Useful for debugging, annoying if it`s already working.
    show_moves = True

    ## Play computer against human:
    ## a) with random player
    # TicTacToe().play([RandomPlayer(), AskingPlayer()], show_moves=show_moves)
    ## b) simple TicTacToe with MyPlayer
    # TicTacToe().play([MyPlayer(), AskingPlayer()], show_moves=show_moves)
    ## c) difficult Gomoku with MyPlayer
    # Gomoku().play([MyPlayer(), AskingPlayer()], show_moves=show_moves)

    ## Test MyPlayer
    ## a) play single game of TicTacToe
    # TicTacToe().play([MyPlayer(), RandomPlayer()], show_moves=show_moves)
    ## b) play single game of Gomoku
    # Gomoku().play([MyPlayer(), RandomPlayer()], show_moves=show_moves)
    ## c) play N games
    TicTacToe().play_n_games([MyPlayer(), RandomPlayer()], n=10)
    # Gomoku().play_n_games([MyPlayer(), RandomPlayer()], n=10)
