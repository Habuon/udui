import numpy as np
import matplotlib.pyplot as plt
import random
import atexit
import os

def prepare_data(num_points=2000, num_classes=4):
    p = []
    label = []

    lines = np.linspace(0, 1, num=num_classes+1)
    count = 0
    while count < num_points:
        a = np.random.rand(2)
        for i in range(1, num_classes+1):
            if a[0] < lines[i]:
                p.append(a)
                label.append(one_hot(i-1, num_classes))
                count += 1
                break
    return np.asarray(p).T + np.random.randn(2, num_points) * 1/50, np.asarray(label).T


def one_hot(x, num_classes):
    b = np.zeros(num_classes)
    b[x] = 1
    return b


def plot_points(inputs, targets, model=None, title=None, block=False):
    cols = [0, 1, 2, 3, 4, 5, 6, 7, 8, 9]
    c = []
    for i in range(targets.shape[1]):
        c.append(cols[np.argmax(targets[:, i])])
    plt.scatter(inputs[0, :], inputs[1, :], c=c, cmap="tab10", s=1.5)


def plot_errors(training_hisotry, block=False):
    # Plot history of errors
    (errs, accs, t_accs) = training_hisotry
    fig, ax = plt.subplots(3, 1, num='Training history', sharex=True)
    fig.canvas.mpl_connect('key_press_event', keypress)
    plt.subplot(3, 1, 1)
    plt.title('Regression error per epoch')
    plt.plot(errs, '-r')
    plt.grid(True)
    plt.xlim(left=-1); plt.ylim(bottom=-1)
    plt.subplot(3, 1, 2)
    plt.title('Training accuracy per epoch [%]')
    plt.plot(np.array(accs)*100, '-b')
    plt.grid(True)

    plt.xlim(left=-1); plt.ylim(bottom=-1)
    plt.subplot(3, 1, 3)
    plt.title('Testing accuracy per epoch [%]')
    plt.plot(np.array(accs)*100, '-b')
    plt.grid(True)

    plt.xlim(left=-1); plt.ylim(-3, 103)
    plt.tight_layout()
    plt.show(block=block)


def keypress(e):
    if e.key in {'q', 'escape'}:
        os._exit(0) # unclean exit, but exit() or sys.exit() won't work
    if e.key in {' ', 'enter'}:
        plt.close() # skip blocking figures


def finish():
    if plt.get_fignums(): plt.show(block=True) # Woraround to prevent plots from closing

atexit.register(finish)
