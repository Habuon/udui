import sys
import random
import time
from games import TicTacToe, Gomoku

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



class MinimaxPlayer(Player):
    def choose_move(self, game, state):
        ### Task 1 ###
        my_player = game.player_at_turn(state) # get 'X' or 'O'

        def max_value(state):
            if game.is_terminal(state):
                return game.utility(state, my_player)
            v = -infinity
            for action in game.actions(state):
                state_after = game.state_after_move(state, action)
                mn = min_value(state_after)
                v = max(v, mn)
            return v

        def min_value(state):
            if game.is_terminal(state):
                return game.utility(state, my_player)
            v = infinity
            for action in game.actions(state):
                state_after = game.state_after_move(state, action)
                mx = max_value(state_after)
                v = min(v, mx)
            return v
        mx = -infinity
        ma = None
        for action in game.actions(state):
            state_after = game.state_after_move(state, action)
            value = min_value(state_after)
            if value > mx:
                mx = value
                ma = action
        return ma



class AlphaBetaPlayer(Player):
    def choose_move(self, game, state):
        my_player = game.player_at_turn(state) # get 'X' or 'O'
        
        def max_value(state, a, b):
            if game.is_terminal(state):
                return game.utility(state, my_player)
            v = -1
            for action in game.actions(state):
                state_after = game.state_after_move(state, action)
                mn = min_value(state_after, a, b)
                v = max(v, mn)
                if v >= b:
                    return v
                a = max(a, v)
            return v

        def min_value(state, a, b):
            if game.is_terminal(state):
                return game.utility(state, my_player)
            v = 1
            for action in game.actions(state):
                state_after = game.state_after_move(state, action)
                mx = max_value(state_after, a, b)
                v = min(v, mx)
                if v <= a:
                    return v
                b = min(b, v)
            return v

        a = mx = -1
        ma = None
        for action in game.actions(state):
            state_after = game.state_after_move(state, action)
            value = min_value(state_after, a, 1)
            a = max(a, value)
            if value > mx:
                mx = value
                ma = action
        return ma



class AlphaBetaEvalPlayer(Player):
    ### Does not work ###
    def choose_move(self, game, state):
        my_player = game.player_at_turn(state) # get 'X' or 'O's
        rows = set()
        actions = dict((x, -1) for x in game.actions(state))
        d = 2   # depth
        def max_value(state, a, b, depth=d):
            if game.is_terminal(state):  # state is terminal return utility
                return game.utility(state, my_player)
            if depth == 0:  # too deep, return evaluation of this state
                return evaluate(state)
            v = -infinity  # v is least possible element
            for action in game.actions(state):
                state_after = game.state_after_move(state, action)  # get the following state
                mn = min_value(state_after, a, b, depth - 1)  # get the minimal possible value
                v = max(v, mn)  # choose maximum of minimal and actual
                actions[action] = v
                if v >= b:  
                    return v
                a = max(a, v)
            actions[action] = v
            return v

        def min_value(state, a, b, depth=d):
            if game.is_terminal(state):
                return game.utility(state, my_player)
            if depth == 0:
                return evaluate(state)
            v = infinity
            for action in game.actions(state):
                state_after = game.state_after_move(state, action)
                mx = max_value(state_after, a, b, depth - 1)
                v = min(v, mx)
                actions[action] = v
                if v <= a:
                    return v
                b = min(b, v)
            actions[action] = v
            return v
        
        def evaluate(state):
            def max_row(board, player):  # should find longest row of specific player
                mx = 0
                for row in range(len(board)):
                    a = 0
                    for col in range(len(board[row])):
                        if board[row][col] == player:
                            a += 1
                        else:
                            mx = max(a, mx)
                            a = 0
                    mx = max(a, mx)
                return mx
            
            def max_col(board, player):  # should find longest column of specific player
                mx = 0
                for col in range(len(board[0])):
                    a = 0
                    for row in range(len(board)):
                        if board[row][col] == player:
                            a += 1
                        else:
                            mx = max(a, mx)
                            a = 0
                    mx = max(a, mx)
                return mx
            board = state["board"]
        
            player = game.other_player(my_player)
            if max_row(board, player) >= 3:  # if oponent have more than 3 in a row we predict that we will lose
                return -max_row(board, player)
            
            if max_col(board, player) >= 3:  # if oponent have more than 3 in a column we predict that we will lose
                return -max_col(board, player)

            if max_row(board, my_player) >= 4:  # if we have more than 4 in a row we could win
                return max_row(board, my_player)
            
            if max_col(board, my_player) >= 4:  # if we have more than 4 in a column we could win
                return max_col(board, my_player)

            return 0

        value = max_value(state, -infinity, infinity)
        for action in actions:
            if actions[action] == value:
                return action



################################ MAIN PROGRAM #################################

if __name__ == '__main__':
    ## Print all moves of the game? Useful for debugging, annoying if it`s already working.
    show_moves = True


    ## Task 1
##    s = time.time()
##    print('MiniMax plays as O and goes second - O must win or draw:')
##    TicTacToe().play([RandomPlayer(), MinimaxPlayer()], show_moves)
##    print(f"{time.time() - s} s")
##
##    s = time.time()
##    print('\n\nMiniMax plays as X and goes first - X must win or draw:')  # might take some extra time (max. cca 20s)
##    TicTacToe().play([MinimaxPlayer(), RandomPlayer()], show_moves)
##    print(f"{time.time() - s} s")
##
##    s = time.time()
##    print('\n\nMiniMax vs. MiniMax - should be draw:')
##    TicTacToe().play([MinimaxPlayer(), MinimaxPlayer()], show_moves)  # might take some extra time (max. cca 20s)
##    print(f"{time.time() - s} s")
##
##    # ## Task 2
##    s = time.time()
##    print('\n\nAlpha-Beta plays as X and goes first - X must win or draw:')
##    TicTacToe().play([AlphaBetaPlayer(), RandomPlayer()], show_moves)
##
##    print(f"{time.time() - s} s")
##
##    s = time.time()
##
##    print('\n\nAlpha-Beta vs. MiniMax - should be draw:')
##    TicTacToe().play([AlphaBetaPlayer(), MinimaxPlayer()], show_moves)
##
##    print(f"{time.time() - s} s")


    # ## Task 3 - bonus
##    print('\n\nAlpha-Beta Eval vs. itself - should be a well-played game.')
##    Gomoku().play([AlphaBetaEvalPlayer(), AlphaBetaEvalPlayer()], show_moves=show_moves)


    # ## Play computer against human:
    # ## a) human cannot win, draw is possible (assuming algorithm is correct)
##    TicTacToe().play([AskingPlayer(), MinimaxPlayer()])   # Task 1
##    TicTacToe().play([MinimaxPlayer(), AskingPlayer()])   # Task 1
##    TicTacToe().play([AskingPlayer(), AlphaBetaPlayer()]) # Task 2
##    TicTacToe().play([AlphaBetaPlayer(), AskingPlayer()]) # Task 2
    # ## b) computer will win, human will loose, draw is not possible
##    TicTacToe(4,4,3).play([AlphaBetaPlayer(), AskingPlayer()]) # Task 2
    # ## c) human, have fun! (recommended depth limit=2~3)
    # Gomoku().play([AskingPlayer(), AlphaBetaEvalPlayer()]) # Task 3
