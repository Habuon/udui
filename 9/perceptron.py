import sys
import numpy as np
import random

from utils import *


class SingleLayerPerceptron:

    def __init__(self, input_dim, output_dim):
        # Initialize perceptron and data.
        # List self.data = [(input1, target1), (input2, target2), ...]
        self.input_dim = input_dim
        self.output_dim = output_dim
        self.initialize_weights()

    def compute_accuracy(self, inputs, targets):
        # Computes *classification* accuracy - percentage of correctly categorized inputs
        return np.mean([d.argmax() == self.compute_output(self.add_bias(x)).argmax() for (x, d) in zip(inputs.T, targets.T)])

    def add_bias(self, x):
        # Add bias to input vector x.
        return np.concatenate((x, [1]))

    def initialize_weights(self):
        # Sets all weights to (Gaussian) random values
        self.W = np.random.randn(self.output_dim, self.input_dim + 1)

    def sigmoid(self, x):
        # Activation function - logistical sigmoid
        return 1 / (1 + np.exp(-x))

    def compute_output(self, x):
        # Computes output (vector y) of the neural network for given input vector x (including bias).
        return self.sigmoid(self.W @ x)

    def compute_error(self, d, y):
        # Computes square error of output y against desired output d.
        return np.sum((d - y)**2)


    def train(self, inputs, targets, num_epochs, test_inp=None, test_targ=None, alpha_start=0.5, alpha_end=0.01):
        # Trains the neural network, iterating num_epochs times.
        # After each epoch, per-epoch regression error (E) and classification
        # accuracy are appended into history, that is return for further plotting.
        count = inputs.shape[1] # number of input-target pairs
        err_history = []
        accuracy_history = []
        test_acc = []

        if test_inp is None or test_targ is  None:
            test_inp = inputs
            test_targ = targets

        for ep in range(num_epochs):
            alpha = alpha_start * (alpha_end / alpha_start) ** (ep / num_epochs)

            E = 0
            for i in np.random.permutation(count):
                x = self.add_bias(inputs[:, i])
                d = targets[:, i]
                y = self.compute_output(x)
                E += self.compute_error(d, y)
                self.W += alpha * np.outer( ((d-y) * y * (1-y)), x )

            err_history.append(E)
            acc = self.compute_accuracy(inputs, targets)
            accuracy_history.append(acc)
            t_acc = self.compute_accuracy(test_inp, test_targ)
            test_acc.append(t_acc)
            if (ep+1) % 10 == 0: print('Epoch {:3d}, E = {:6.3f}, accuracy = {:4.1%}, test_accuracy = {:4.1%}'.format(ep+1, E, acc, t_acc))

        return (err_history, accuracy_history, test_acc)


if __name__ == "__main__":
    ## Load data and initialize

    inputs, targets = prepare_data()

    ### YOUR CODE GOES HERE ###

    tr_inp, tr_targets = [], []
    test_inp, test_targets = [], []

    z = list(zip(inputs.T, targets.T))
    length = len(z)

    while len(z) != 2 / 10 * length:
        idx = random.randint(0, len(z) - 1)
        tr_inp.append(z[idx][0])
        tr_targets.append(z[idx][1])
        z.pop(idx)

    tr_inp = np.asarray(tr_inp).T
    tr_targets = np.asarray(tr_targets).T

    while len(z) != 0:
        idx = random.randint(0, len(z) - 1)
        test_inp.append(z[idx][0])
        test_targets.append(z[idx][1])
        z.pop(idx)

    test_inp = np.asarray(test_inp).T
    test_targets = np.asarray(test_targets).T

    input_dim = inputs.shape[0]
    output_dim = targets.shape[0]

    model = SingleLayerPerceptron(input_dim, output_dim)

    ## Train the neural network
    history = model.train(tr_inp, tr_targets, test_inp=test_inp,
                                   test_targ=test_targets, num_epochs=200)
    plot_errors(history)

