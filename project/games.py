import random
import copy
from time import time

TIME_LIMIT = 5  # seconds



############################### GAME DEFINITION ###############################

class Game:
    def __init__(self):
        pass

    def initial_state(self):
        pass

    def players(self):
        pass

    def actions(self, state):
        pass

    def is_terminal(self, state):
        pass

    def utility(self, state, player):
        pass

    def state_after_move(self, state, move):
        pass

    def player_at_turn(self, state):
        pass

    def other_player(self, player):
        pass

    def display_state(self, state):
        pass

    def play(self, players, can_break_limit=[False, False], show_moves=True):
        # Executes one match of the game. Returns index of winning player, or -1 if draw.
        # can_break_limit determines whether player 1 or player 2 can break the time limit
        assert len(players) == 2, 'Game must be played by exactly two players!'
        assert len(can_break_limit) == 2, 'Must provide two values for can_break_limit!'
        state = self.initial_state()
        if show_moves:
            self.display_state(state)
        while True:
            for i, player in enumerate(players):
                p_char = self.player_at_turn(state)
                # Choose move
                t = time()
                move = player.choose_move(self, state)
                t = time() - t
                if t > TIME_LIMIT and not can_break_limit[i]:
                    print('Player "{}" exceeded time limit ({:.3f}s) - his turn took {:.3f}s'
                          .format(p_char, TIME_LIMIT, t))
                    return 1 - i
                # Make move
                state = self.state_after_move(state, move)
                if state is None:
                    print('Player "{}" made invalid move and lost'.format(p_char))
                    return 1 - i
                if show_moves:
                    self.display_state(state)
                # Check (normal) game termination
                if self.is_terminal(state):
                    p0 = self.players()[0]
                    p0_score = self.utility(state, p0)
                    if p0_score > 0:
                        print('Player "{}" won'.format(p0))
                        return 0
                    if p0_score < 0:
                        print('Player "{}" won'.format(self.other_player(p0)))
                        return 1
                    print("Draw")
                    return -1

    def play_n_games(self, players, n, can_break_limit=[False, False], show_moves=False):
        # Execute N games of two players. In each game order of the players is switched (i.e.
        # different player starts the game).
        results = [[0]*3, [0]*3]
        score1 = 0
        plrs, plr_chrs, cbr = players, self.players(), can_break_limit
        for i in range(n):
            print('Game {}: player 1 is "{}", player 2 is "{}": '.format(i+1, *plr_chrs), end='')
            w = self.play(plrs, cbr, show_moves)
            winner = w if w < 0 or i%2==0 else 1-w  # switching-aware winner choice
            score1 += winner + 1 if winner < 1 else -1
            if winner == -1:
                results[0][1] += 1
                results[1][1] += 1
            else:
                results[winner][0] += 1
                results[1 - winner][2] += 1
            # Switch the order of two players
            plrs, plr_chrs, cbr = [list(reversed(x)) for x in (plrs, plr_chrs, cbr)]
        print('Results:')
        print('\tplayer 1: {} win, {} draw, {} lost, total score: {}'.format(*results[0], score1 / n))
        print('\tplayer 2: {} win, {} draw, {} lost, total score: {}'.format(*results[1], -score1 / n))



class Reversi(Game):
    directions = [(r, c) for r in range(-1, 2) for c in range(-1, 2) if r|c != 0]

    def __init__(self, k=8):
        # Create game instance, k == size of the board.
        assert k % 2 == 0, 'k must be even'
        self.k = k
        self.win_unility = 1.0


    def initial_state(self):
        # Returns initial state of the game
        board = [[' ']*self.k for _ in range(self.k)]
        h = self.k // 2
        board[h][h] = 'B'
        board[h-1][h-1] = 'B'
        board[h-1][h] = 'w'
        board[h][h-1] = 'w'
        return {'player_at_turn': 'B',
                'board': board}


    def players(self):
        # List of players in game
        return ['B', 'w']


    def player_at_turn(self, state):
        # Which player is at turn in given state of game
        return state['player_at_turn']


    def other_player(self, player):
        # Returns the opposite player
        players = self.players()
        if player == players[0]:
            return players[1]
        return players[0]


    def action_rc_to_number(self, r, c):
        # Convert [row, column] to action code (number)
        return r * self.k + c


    def action_number_to_rc(self, n):
        # Convert action code to [row, column] format
        return divmod(n, self.k)


    def execute_move(self, state, r, c, check_only=False):
        ### May be CPU-heavy
        # Place disc of player at turn at r,c tile and flip appropriate opponent`s discs.
        # If check_only: only check if move to r,c tile is a valid move.
        # Return: tuple (is valid move:bool, state after move:dict)
        board = state['board']
        player = self.player_at_turn(state)
        other_player = self.other_player(player)

        if board[r][c] != ' ':
            return False, None  # not an empty tile
        
        if not check_only:
            board = copy.deepcopy(board)  # only care about new board if we`re really executing the move
        
        valid_move = False
        for dr, dc in self.directions:
            rr, cc = r, c
            num_opp_discs = 0
            do_dir = True
            while do_dir:
                rr += dr
                cc += dc
                if rr < 0 or cc < 0 or rr >= self.k or cc >= self.k:
                    do_dir = False  # ran out of board
                elif board[rr][cc] == ' ':
                    do_dir = False  # no player`s disc on the other end
                elif board[rr][cc] == other_player:
                    num_opp_discs += 1  # some opponent`s discs I`m going to grab
                elif board[rr][cc] == player:
                    if num_opp_discs == 0:
                        do_dir = False  # no opponent`s discs between new and my disc
                    else:
                        valid_move = True
                        do_dir = False  # successfully quit this direction
                        if check_only:
                            return True, None  # only checking => only one direction is enough
                        else:
                            # Turn opponents disc and place mine
                            while rr != r or cc != c:
                                rr -= dr
                                cc -= dc
                                board[rr][cc] = player
                            board[r][c] = player
                else:
                    raise ValueError('Invalid char "{}" at board[{}, {}]!'
                                     .format(board[rr][cc], rr, cc))
        if not valid_move:
            return False, None
        return True, \
               {'player_at_turn': other_player,
                'board': board}


    def actions(self, state):
        ### May be CPU-heavy
        # List of possible actions (action codes) for player at turn
        acts = []
        for r in range(self.k):
            for c in range(self.k):
                valid_move, _ = self.execute_move(state, r, c, check_only=True)
                if valid_move:
                    acts.append(self.action_rc_to_number(r, c))
        return acts


    def state_after_move(self, state, move):
        ### May be CPU-heavy
        # Executes given action, returning state, or None if action was invalid 
        valid_move, new_state = self.execute_move(state, *self.action_number_to_rc(move))
        if not valid_move:
            print('Action {} is not possible for player "{}" in this state:'.format(move, self.player_at_turn(state)))
            self.display_state(state, show_nums=True)
            return None
        return new_state


    def is_terminal(self, state):
        ### May be CPU-heavy
        # Is this final state of the game?
        return len(self.actions(state)) == 0


    def utility(self, state, player):
        ### May be CPU-heavy
        if not self.is_terminal(state):
            return 0
        board = state['board']
        other_player = self.other_player(player)
        num_my, num_opp = 0, 0
        for r in range(self.k):
            for c in range(self.k):
                if board[r][c] == player:
                    num_my += 1
                elif board[r][c] == other_player:
                    num_opp += 1
        if num_my > num_opp:
            return self.win_unility
        if num_my < num_opp:
            return -self.win_unility
        return 0


    def display_state(self, state, show_nums=False):
        # Print state of the game, optionally show numbers of tiles as well
        board = state['board']
        dig = len(str(self.k ** 2))
        for r in range(self.k):
            print('|', end='')
            for c in range(self.k):
                ch = board[r][c]
                ch = self.action_rc_to_number(r, c) if show_nums and ch == ' ' else ch
                print('{:^{dig}}'.format(ch, dig = dig), end='|')
            print()
        if not show_nums: print()
