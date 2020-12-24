from logic import *
from kb import *
import sys



################################ WORLD DEFINITION ################################

class WumpusWorld:
    def __init__(self, map_path):
        ch_to_type = {'#':'wall', 'W':'wumpus', 'p':'pit', 'g':'gold', 'H':'hero', '.':'empty'}
        self.mapa = []
        self.bump = False
        self.scream = False
        self.hero = (0, 0)
        self.arrow = 1
        self.players_gold = []
        self.players_wumpus = []
        self.gold_count = 0
        self.wumpus_count = 0
        with open(map_path, 'r') as f:
            for r, line in enumerate(f.read().splitlines()):
                row = []
                for c, ch in enumerate(line):
                    tile = {'type':ch_to_type[ch], 'visited':False, 'percept':set()}
                    if tile['type'] == 'hero':
                        tile['type'] = 'empty'
                        tile['visited'] = True
                        self.hero = (r, c)
                    row.append(tile)
                self.mapa.append(row)
        self.init_hero = self.hero
        # Percepts
        deltas = [(-1, 0), (0, 1), (1, 0), (0, -1)]
        for r, row in enumerate(self.mapa):
            for c, tile in enumerate(row):
                for dr, dc in deltas:
                    nr, nc = r+dr, c+dc
                    if tile['type'] == 'wumpus':
                        self.mapa[nr][nc]['percept'].add('stench')
                    elif tile['type'] == 'pit':
                        self.mapa[nr][nc]['percept'].add('breeze')
                if tile['type'] == 'gold':
                    self.gold_count += 1
                    tile['percept'].add('glitter')
                if tile['type'] == 'wumpus':
                    self.wumpus_count += 1

    def print_map(self, print_unvisited = False):
        # Prints visible part of map, or whole map if print_unvisited == True
        type_to_ch = {'wall':'#', 'wumpus':'W', 'pit':'p', 'gold':'g', 'empty':' '}
        hidden_tile = '-'
        print()
        for r, row in enumerate(self.mapa):
            for c, tile in enumerate(row):
                if (r, c) == self.hero: print('H', end='')
                else: print((type_to_ch[tile['type']] if tile['visited'] or print_unvisited else hidden_tile), end='')
            print()
        print()

    def directions_str_to_num(self, direction):
        # 0 = up, 1 = right, 2 = down, 3 = left
        return {'up':0,    'u':0,
                'right':1, 'r':1,
                'down':2,  'd':2,
                'left':3,  'l':3,
               }[direction.lower()]

    def move(self, direction):
        # Moves the hero in desired direction, returns True if he survives and game goes on
        # 0 = up, 1 = right, 2 = down, 3 = left
        direction = self.directions_str_to_num(direction)
        dr = ((direction+1) % 2) * (direction - 1)
        dc = (direction % 2) * (-direction + 2)
        r, c = self.hero
        nr, nc = r+dr, c+dc
        if self.mapa[nr][nc]['type'] == 'wall':
            self.bump = True
            self.mapa[nr][nc]['visited'] = True
            kb.tell(Fact(L("bump", nr, nc)))
            nr, nc = r, c
        elif self.mapa[nr][nc]['type'] in ['wumpus', 'pit']:
            print('--> You ran into ' + self.mapa[nr][nc]['type'])
            return False
        elif self.mapa[nr][nc]['type'] == 'gold':
            print('--> You have a gold!')
            self.mapa[nr][nc]['type'] = 'empty'
        self.hero = (nr, nc)
        self.mapa[nr][nc]['visited'] = True
        return True

    def shoot(self, direction):
        # Shoots an arrow in desired direction, returns True as game goes on
        # 0 = up, 1 = right, 2 = down, 3 = left
        direction = self.directions_str_to_num(direction)
        if self.arrow < 1:
            print('You have no more arrows')
            return True
        self.arrow -= 1
        dr = ((direction+1) % 2) * (direction - 1)
        dc = (direction % 2) * (-direction + 2)
        r, c = self.hero
        while self.mapa[r][c]['type'] != 'wall':
            r, c = r+dr, c+dc
            if self.mapa[r][c]['type'] == 'wumpus':
                self.scream = True
                self.mapa[r][c]['type'] = 'empty'
                print('--> You killed Wumpus!')
                self.players_wumpus.append((r, c))
                return True
        print('--> You missed')
        return True

    def climb(self, _):
        # Climb out of the cave, if you`re at your starting position. Returns True if game goes on, False is you climbed out.
        if self.hero == self.init_hero:
            print('--> You escaped from the cave!')
            print(f"[*] You killed {len(self.players_wumpus)} / {self.wumpus_count} {'wumpuses' if len(self.players_wumpus) > 1 else 'wumpus'}")
            print(f"[*] You took {len(self.players_gold)} / {self.gold_count} {'pieces of gold' if len(self.players_wumpus) > 1 else 'piece of gold'}")
            return False
        print('--> You cannot climb unless you are at your starting position.')
        return True

    def pick(self, _):
        r, c = self.hero
        if "glitter" in self.mapa[r][c]["percept"]:
            self.mapa[r][c]["percept"].remove("glitter")
            self.players_gold.append((r, c))
            print("--> You picked up gold")
            return True
        print('--> No gold found here')
        return True

    def percept(self):
        # Returns set of percepts in current time
        r, c = self.hero
        p = self.mapa[r][c]['percept'].copy()
        if self.bump:
            p.add('bump')
            self.bump = False
        if self.scream:
            p.add('scream')
            self.scream = False
        return p

    def play(self, choose_action, print_unvisited = False):
        # Main loop of the game
        while True:
            print('\n------------------------------------------------------------')
            self.print_map(print_unvisited)
            action, direction = choose_action(self, self.percept())
            if not action(direction):
                return

################################ TOOLS ################################


def print_safe_moves(world):
    print('Safe moves: ')
    r, c = world.hero
    moves = [('up', -1, 0), ('right', 0, 1), ('down', 1, 0), ('left', 0, -1)]
    for direction, dr, dc in moves:
        nr, nc = r+dr, c+dc
        if kb.ask(L('safe', nr, nc)):
            print('\t{} to ({}, {})'.format(direction, nr, nc))
    print()


def get_safe_moves(world):
    res = []
    r, c = world.hero
    moves = [('up', -1, 0), ('right', 0, 1), ('down', 1, 0), ('left', 0, -1)]
    for direction, dr, dc in moves:
        nr, nc = r+dr, c+dc
        if kb.ask(L('safe', nr, nc)) and kb.ask(NOT('bump', nr, nc)):
            res.append((direction, nr, nc))
    return res


def get_action_from_user(world):
    try:
        s = input('Choose action ([move|shoot|climb|pick|quit], direction): ')
        if s in ['exit', 'quit', 'q']:
            print('Good bye...')
            sys.exit(0)
        a = s.split(' ')
        action = {'move':world.move, 'shoot':world.shoot, 'climb':world.climb, 'pick':world.pick}[a[0]]
        return action, (a[1] if len(a)>1 else None)
    except KeyError:
        print('Invalid action, try again...')
        return get_action_from_user(world)


################################ KB MANAGMENT ################################


def choose_action_interactive(world, percept):
    # Simple interactive player - asks user for each action.
    # User inputs: "[move|shoot|climb], direction". E.g "move up".
    print('You are at position {} and you percept: {}'.format(world.hero, (percept if percept else '{}')))
    kb_add_step(world, percept)
    print_safe_moves(world)
    return get_action_from_user(world)


def implication(r, c, indicator, danger, ic, dc):
    if c - 1 >= 0:
        if r + 1 < len(world.mapa):
            kb.tell(Implication(ic(indicator, r,  c - 1), ic(indicator, r + 1,  c), dc(danger, r, c)))
        if c + 1 < len(world.mapa[0]):
            kb.tell(Implication(ic(indicator, r,  c - 1), ic(indicator, r,  c + 1), dc(danger, r, c)))
        if r - 1 > 0:
            kb.tell(Implication(ic(indicator, r,  c - 1), ic(indicator, r - 1,  c), dc(danger, r, c)))
    if c + 1 < len(world.mapa[0]):
        if r + 1 < len(world.mapa):
            kb.tell(Implication(ic(indicator, r,  c + 1), ic(indicator, r + 1,  c), dc(danger, r, c)))
        if c - 1 > 0:
            kb.tell(Implication(ic(indicator, r,  c + 1), ic(indicator, r,  c - 1), dc(danger, r, c)))
        if r - 1 > 0:
            kb.tell(Implication(ic(indicator, r,  c + 1), ic(indicator, r - 1,  c), dc(danger, r, c)))
    if r - 1 >= 0:
        if c + 1 < len(world.mapa):
            kb.tell(Implication(ic(indicator, r,  c + 1), ic(indicator, r - 1,  c), dc(danger, r, c)))
        if r + 1 < len(world.mapa[0]):
            kb.tell(Implication(ic(indicator, r - 1,  c), ic(indicator, r + 1,  c), dc(danger, r, c)))
        if c - 1 > 0:
            kb.tell(Implication(ic(indicator, r,  c - 1), ic(indicator, r - 1,  c), dc(danger, r, c)))
    if r + 1 < len(world.mapa):
        if c + 1 < len(world.mapa):
            kb.tell(Implication(ic(indicator, r,  c + 1), ic(indicator, r + 1,  c), dc(danger, r, c)))
        if r - 1 > 0:
            kb.tell(Implication(ic(indicator, r + 1,  c), ic(indicator, r - 1,  c), dc(danger, r, c)))
        if c - 1 > 0:
            kb.tell(Implication(ic(indicator, r,  c - 1), ic(indicator, r + 1,  c), dc(danger, r, c)))


def implication_or(r, c, indicator, danger, ic, dc):
    kb.tell(Implication(ic(indicator, r, c), dc(danger, r, c)))
    if r - 1 >= 0:
        kb.tell(Implication(ic(indicator, r, c), dc(danger, r - 1, c)))
    if r + 1 < len(world.mapa):
        kb.tell(Implication(ic(indicator, r, c), dc(danger, r + 1, c)))
    if c - 1 >= 0:
        kb.tell(Implication(ic(indicator, r, c), dc(danger, r, c - 1)))
    if c + 1 < len(world.mapa[0]):
        kb.tell(Implication(ic(indicator, r, c), dc(danger, r, c + 1)))


def kb_initialize(kb, world):
    # At the beginning of the game: Fill KB with implication rules that will
    # help infer whether tiles are safe or not
    ### Task 3 (part 1/2)
    ### YOUR CODE GOES HERE ###
    r, c = world.hero
    kb.tell(Fact(L("safe", r, c)))
    kb.tell(Fact(NOT("Done")))
    for r in range(len(world.mapa)):
        for c in range(len(world.mapa[0])):
            # Tile is safe if there`s no pit or Wumpus
            kb.tell(Fact(NOT("visited", r, c)))
            kb.tell(Fact(NOT("bump", r, c)))
            # kb.tell(Fact(L("stench", r, c)))
            # kb.tell(Fact(L("breeze", r, c)))
            kb.tell(Implication(NOT('wumpus_at', r, c), NOT('pit', r, c),  L('safe', r,  c)))
            kb.tell(Implication(NOT('visited', r, c), NOT('bump', r, c), L('safe', r,  c),  L('interesting', r,  c)))
            implication(r, c, "breeze", "pit", L, L)
            implication(r, c, "stench", "wumpus_at", L, L)
            implication_or(r, c, "breeze", "pit", NOT, NOT)
            implication_or(r, c, "stench", "wumpus_at", NOT, NOT)
            implication_or(r, c, "scream", "wumpus_at", L, NOT)


def process_percept(percept, world):
    r, c = world.hero
    if "stench" in percept:
        kb.tell(Fact(L("stench", r, c)))
    else:
        kb.tell(Fact(NOT("stench", r, c)))
    if "breeze" in percept:
        kb.tell(Fact(L("breeze", r, c)))
    else:
        kb.tell(Fact(NOT("breeze", r, c)))
    if "scream" in percept:
        kb.tell(Fact(L("scream", r, c)))


def kb_add_step(world, percept):
    # Every time after player makes a step: Add percepts and/or other knowledge to KB
    ### Task 3 (part 2/2)
    ### YOUR CODE GOES HERE ###
    r, c = world.hero        # row-column position of hero
    process_percept(percept, world)
    kb.tell(Fact(L("safe", r, c)))
    kb.tell(Fact(L("visited", r, c)))
    kb.tell(Fact(NOT("interesting", r, c)))


def find_closest_interesting():
    actual = world.hero
    to_search = [actual]
    seen = []
    new = []
    while len(to_search) != 0:
        for n in to_search:
            if n in seen:
                continue
            for k in neighbours(n):
                if k in seen:
                    continue
                new.append(k)
        for n in new:
            r, c = n
            if kb.ask(L("interesting", r, c)):
                return n
        seen += to_search
        to_search = new
        new = []


def where_to_shoot():
    r, c = world.hero
    moves = [('up', -1, 0), ('right', 0, 1), ('down', 1, 0), ('left', 0, -1)]
    for direction, dr, dc in moves:
        nr, nc = r + dr, c + dc
        if kb.ask(L('wumpus_at', nr, nc)):
            return world.shoot, direction
    return None


def neighbours(node):
    res = []
    r, c = node
    if (kb.ask(L('safe', r - 1, c))) and kb.ask(NOT('bump', r - 1, c)):
        res.append((r - 1, c))
    if kb.ask(L('safe', r + 1, c)) and kb.ask(NOT('bump', r + 1, c)):
        res.append((r + 1, c))
    if kb.ask(L('safe', r, c - 1)) and kb.ask(NOT('bump', r, c - 1)):
        res.append((r, c - 1))
    if kb.ask(L('safe', r, c + 1)) and kb.ask(NOT('bump', r, c + 1)):
        res.append((r, c + 1))
    return res


def distance(actual, dest):
    if actual == dest:
        return 0
    to_search = [actual]
    seen = []
    new = []
    dist = 1
    while len(to_search) != 0:
        for n in to_search:
            if n in seen:
                continue
            for k in neighbours(n):
                if dest == k:
                    return dist
                if k in seen:
                    continue
                new.append(k)
        seen += to_search
        to_search = new
        new = []
        dist += 1
    return dist


def find_safe_path(dest):
    d = distance(world.hero, dest)
    for move in get_safe_moves(world):
        if distance((move[1], move[2]), dest) < d:
            return move[0]


def choose_action_automatic(world, percept):
    ### Task 4 - bonus - make action choosing automatic: explore unvisited, pick up gold, kill Wumpus and climb from the cave.
    ### YOUR CODE GOES HERE ###
    kb_add_step(world, percept)
    r, c = world.hero
    if r == 5 and c == 8:
        print("ahoj")
    if r == 10 and c == 2:
        print("ahoj")
    if "glitter" in percept:
        return world.pick, None
    safe_moves = get_safe_moves(world)
    shoot = where_to_shoot()
    if shoot is not None and world.arrow != 0:
        return shoot
    for move in safe_moves:
        if kb.ask(L("bump", move[1], move[2])):
            continue
        if kb.ask(L("visited", move[1], move[2])):
            continue
        return world.move, move[0]
    if not kb.ask(L("Done")):
        closest_interesting = find_closest_interesting()
        if closest_interesting is not None:
            for move in find_safe_path(closest_interesting):
                return world.move, move
        else:
            kb.tell(Fact(L("Done")))
    move = find_safe_path(world.init_hero)
    if move is not None:
        return world.move, move[0]

    return world.climb, None







################################ MAIN PROGRAM ################################

if __name__ == "__main__":
    print_unvisited = False # Only print the tiles I`ve been to. Make True for debugging

    kb = KB()
    world = WumpusWorld('mapa1.txt') # or 'mapa2.txt'
    kb_initialize(kb, world)
    # world.play(choose_action_interactive, print_unvisited)

    # Task 4 - bonus
    world.play(choose_action_automatic, print_unvisited)
