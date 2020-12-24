import math
import random
import os
import atexit
from time import sleep
import numpy as np
import matplotlib

matplotlib.use('TkAgg')  # fixme if plotting doesn`t work (try 'Qt5Agg' or 'Qt4Agg')
import matplotlib.pyplot as plt


def finish():
    plt.show(block=True)  # Woraround to prevent plots from closing


atexit.register(finish)


class OptimizeMax:
    # Abstract class solving all maximization problems

    def __init__(self):
        pass

    def hillclimb(self, max_steps=100):
        # A function that finds the maximal value of the fitness function by
        # executing the hill climbing algorithm.
        # Returns a state (e.g. x) for which fitness(x) is maximal.
        x = self.random_state()
        for i in range(max_steps):
            self.plot(x, self.fitness(x), "Name")
            m = x
            for n in self.neighbors(x):
                if self.fitness(n) >= self.fitness(m):
                    m = n
            if m == x:
                return x
            x = m

        # In every iteration use:
        #   self.plot(x, x_fit, title='Hill climb')
        # to visualize the search.

        return m  # Dummy return

    # These abstract methods are implemented in subclasses
    def fitness(self, x):
        # Returns the value of fitness for a given state.
        raise NotImplementedError("This function needs to be implemented in subclass.")

    def neighbors(self, x):
        # Returns a list of neighbouring states for a given state.
        raise NotImplementedError("This function needs to be implemented in subclass.")

    def random_state(self):
        # Returns a random state for a given problem.
        raise NotImplementedError("This function needs to be implemented in subclass.")

    def plot(self, x, fx, title):
        # Plots point [x, fx] onto a plot. If the inhereted class does not
        # override, this function it will do essentially nothing.
        pass


class MysteryFunction(OptimizeMax):
    # An optimization problem in which we are trying to find value for x such
    # that function sin(x)/x is maximized.

    def __init__(self, span=30, delta=0.1):
        self.cfg = None
        self.hist_x = []
        self.hist_y = []
        self.span = span
        self.delta = delta

    def keypress(self, e):
        if e.key in {'q', 'escape'}: os._exit(0)  # unclean exit, but exit() or sys.exit() won't work
        if e.key in {' ', 'enter'}: plt.close()  # skip blocking figures

    def plot(self, x, y, title, temperature=None):
        # Initialization of figure
        if title != self.cfg:
            self.cfg = title
            self.hist_x = []
            self.hist_y = []
            plt.figure(num=title).canvas.mpl_connect('key_press_event', self.keypress)
            plt.axis([-self.span, self.span, -0.5, 2.5])
            plt.ion()
        # Plotting
        plt.clf()
        xx = np.linspace(-self.span, self.span, 1000)
        plt.plot(xx, np.sin(xx) / xx + np.cos(xx / 10) / 3, c='k', lw=0.5)
        self.hist_x += [x]
        self.hist_y += [y]
        colors = np.arange(len(self.hist_x))
        plt.scatter(x, y, s=30, c='r')
        if temperature:
            plt.title('T          = {:.5f}\np(-0.3) = {:.8f} %\n[Press ESC to quit]'
                      .format(temperature, math.exp(-0.3 / temperature) * 100), loc='left')
        else:
            plt.title('[Press ESC to quit]', loc='left')
        plt.gcf().canvas.flush_events()
        plt.waitforbuttonpress(timeout=0.001)

    def fitness(self, x):
        if x == 0:
            return 1
        return np.sin(x) / x + np.cos(x / 10) / 3

    def neighbors(self, x):
        res = []
        if x > -self.span + 3 * self.delta: res += [x - i * self.delta for i in range(1, 4)]
        if x < self.span - 3 * self.delta: res += [x + i * self.delta for i in range(1, 4)]
        return res

    def random_state(self):
        return random.random() * self.span * 2 - self.span


class EightQueens(OptimizeMax):
    # An optimization problem in which we are trying to find positions of 8
    # queens on an 8x8 chessboard so that no two queens threaten each other.

    def fitness(self, x):
        m = 28  # since hill climbing is searching for the largest fitness I had to make the best state which is 0
        # somehow the biggest one
        num = 0  # number of queens that could attack each other
        for c1, l1 in enumerate(x):
            for c2, l2 in enumerate(x):
                if c1 == c2:  # cannot happen only if it is the same queen
                    continue
                if l1 == l2:  # they are in the same line
                    num += 1
                if abs(c1 - c2) == abs(l1 - l2):  # they are on the diagonal
                    num += 1

        return m - num // 2  # resulting fitness function  showing how many pairs of queens could attack each other

    def neighbors(self, x):
        result = []
        for i in range(8):  # move all the queens to generate all possible next states
            for k in range(1, x[i]):  # from actual up to 1
                result.append(list(x))
                result[-1][i] -= k
            for k in range(1, 8 - x[i] + 1):  # from the actual down to the max
                result.append(list(x))
                result[-1][i] += k
        return result

    def random_state(self):
        result = []
        for i in range(8):
            result.append(random.randint(1, 8))  # each element represents how far the queen is from the bottom
            # the position of element in the array is the column on the playboard
        return result


if __name__ == '__main__':
    #  Task 1
    for _ in range(10):
        problem = MysteryFunction()
        max_x = problem.hillclimb()
        print("Found maximum of Mystery function with hill climbing at x={}, f={}\n"
              .format(max_x, problem.fitness(max_x)))
        sleep(2)

    #  Task 2
    f = []
    for i in range(10):
        problem = EightQueens()
        solution = problem.hillclimb()
        f.append(problem.fitness(solution))
        print(f"{i + 1}. Found a solution (with fitness of {format(problem.fitness(solution))} "
              f"with hill climbing to 8 queens problem:\n{solution}\n")
        if problem.fitness(solution) == 28:
            break
