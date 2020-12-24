import sys
import time
from maps import *

class MapCSP():
    def __init__(self, states, neighbours):
        # List of available colors
        self.color_options = ['red', 'green', 'blue', 'yellow']
        self.states = states
        self.neighbours = neighbours
        self.colors = {s: None for s in self.states}

    def print_map(self):
        # Prints all states and their colors
        for s in sorted(self.states):
            print('{} has color: {}'.format(s, self.get_color(s)))
        print()


    def set_color(self, state, color):
        # Assign color to a state
        self.colors[state] = color

    def del_color(self, state):
        # Remove color from state - reset to None
        self.colors[state] = None

    def get_color(self, state):
        # Get color assigned to a state
        return self.colors[state]

    def has_color(self, state):
        # Returns True if state has already a color
        return self.colors[state] != None

    def same_colors(self, state1, state2):
        # Returns True if state1 and state2 are colored with the same color.
        return self.has_color(state1)  and  self.get_color(state1) == self.get_color(state2)

    def all_colored(self):
        # Returns True if all states of the map are already colored.
        return all([self.has_color(s) for s in self.states])

    def is_correct_coloring(self):
        # Returns True if coloring is all correct, False if not. Prints the result with found error (if any).
        print('Coloring is ', end='')
        for s1 in self.states:
            if self.get_color(s1) not in self.color_options:
                print('INCORRECT - {} has invalid color: {}\n'.format(s1, self.get_color(s1)))
                return False
            for s2 in self.neighbours[s1]:
                if self.same_colors(s1,s2):
                    print('INCORRECT - {} and {} have conflicting color {}\n'.format(s1, s2, mapa.get_color(s1)))
                    return False
        print('OK\n')
        return True


    def can_set_color(self, state, color):
        # Returns True if we can set color to a state without violating constrains - all neighbouring
        # states must have None or different color.
        for n in self.neighbours[state]:
            if self.colors[n] == color:
                return False
            if self.colors[n] is not None:
                continue            
            colors = set(self.color_options)  # all possible colors
            colors.remove(color)  # remove my future color
            for nn in self.neighbours[n]:  # iter trough all neighbours of that neighbour
                if self.colors[nn] is None:  # if neighbour's neighbour has no color we skip him
                    continue
                if self.colors[nn] not in colors:
                    continue
                colors.remove(self.colors[nn])  # remove color of neighbour's neighbour from all possible colors
            if len(colors) == 0:  # if there is neighbour that could have no colors left we know that we can not choose this color
                return False
        return True


    def select_next_state(self):
        # Selects next state that will be colored, or returns False if no such exists (all stated are
        # colored). You can use heuristics or simply choose a state without color for start.
        queue = dict()  # make dictionary that will be used as priority queue
        for state in self.colors:  # go trough all states
            if self.colors[state] is not None:  # if the state has color we skip it
                continue
            queue[state] = len([x for x in self.color_options if x not in [self.colors[y] for y in self.neighbours[state]]])  # weight of state is set to number of remaining colors for that state
        return False if len(queue.keys()) == 0 else min(queue, key=queue.get)  # return false if there is no state without color else return state with least possibilities of colors
        
    
    def color_rek(self, state):
        if self.all_colored():  # if all countries are colored no need to continue
            return
        for color in self.color_options:  # try all possible colors
            if not self.can_set_color(state, color):  # if can not use this specific color continue
                continue
            self.set_color(state, color)  # set the color to this state
            next_state = self.select_next_state()  # find the next state
            self.color_rek(next_state)  # call recurent function
            if self.all_colored():  # if the recurent function was successfull quit
                return  
            self.del_color(state) # clear my color 
        self.del_color(state)  # clear my color 

    def color_map(self):                    
        # Assign colors to all states on the map. (! Beware: 'map' is python`s reserved word - function)
        state = self.select_next_state()  # select starting state
        self.color_rek(state)  # try filling colors using reccurent function 
        return self.all_colored()




if __name__ == "__main__":
    maps = [('Australia', AustraliaMap()),
            ('USSR', USSRMap()),
            ('USA', USAMap()),
            ('World', WorldMap()),

            ('Impossible Australia', ImpossibleMap(AustraliaMap())),
            ('Impossible USSR', ImpossibleMap(USSRMap())),
            ('Impossible USA', ImpossibleMap(USAMap())),
            ('Impossible World', ImpossibleMap(WorldMap()))
            ]

    for name, mapa in maps:
        print('==== {} ===='.format(name))
        t = time.time()
        has_result = mapa.color_map()    # Compute the colors for an empty map
        print('Time: {:.3f} ms'.format( (time.time() - t)*1000 ))
        if has_result:
            mapa.is_correct_coloring()  # Print whether coloring is correct
        else:
            print('Coloring does not exist\n')
        # mapa.print_map()    # Print whole coloring
