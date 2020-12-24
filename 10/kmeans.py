from PIL import Image
import matplotlib.pyplot as plt
from random import shuffle
import numpy as np
import os


def press_to_quit(e):
    if e.key in {'q', 'escape'}:
        os._exit(0) # unclean exit, but exit() or sys.exit() won't work
    if e.key in {' ', 'enter'}:
        plt.close() # skip blocking figures



class K_Means:
    def __init__(self, img_filename):
        print('Loading image "{}" '.format(img_filename), end='')
        self.img_path = img_filename
        with Image.open(img_filename, 'r') as img:
            img.load()
            pixels = np.array(img, dtype='float64')
            self.h, self.w, _ = pixels.shape
            self.pixels = pixels.reshape(-1, 3)
            print('({} x {} = {} pixels)'.format(self.h, self.w, self.h*self.w))
        self.centers = np.zeros((1, 3))


    def init_centers(self, num_centers, method='sample'):
        # Initialize centers.
        if method == 'random':
            # Random colors.
            self.centers = np.random.rand(num_centers, 3) * 256
        elif method == 'sample':
            # Each center is a initialized as color of a random pixel from image.
            count, _ = self.pixels.shape
            self.centers = np.array([self.pixels[np.random.randint(count), :]
                                     for _ in range(num_centers)])
        else:
            raise NotImplementedError('Wrong method for centers initialization')


    def distance(self, a, b):
        # Euclidian distance of two points (e.g. two colors).
        return np.linalg.norm(a - b)


    def show_img(self, pixels):
        # Plot the image.
        print('Plotting image\n')
        title = self.img_path.split('.')[0]
        plt.figure(title).canvas.mpl_connect('key_press_event', press_to_quit)
        plt.axis('off')
        pxs = np.clip(np.asarray(pixels).reshape(self.h, self.w, 3), a_min=0, a_max=255)
        plt.imshow(np.asarray(pxs, dtype='ubyte'))
        plt.show()
        # plt.savefig('result_'+title+'.png', bbox_inches='tight')  # save image to file:


    def posterize(self, show=True):
        # Image posterization - replaces color of pixels with colors of appropriate centers.
        print('Running posterization')
        pxs = self.pixels
        k = self.centers.shape[0]
        k_pxs = np.tile(pxs.reshape(-1, 3, 1), (1, 1, k))  # shape = (h*w, colors, k)
        D = np.linalg.norm(k_pxs - self.centers.T, axis=1)  # shape = (h*w, k)
        col_i = np.argmin(D, axis=1)  # shape = (h*w)
        final_pxs = self.centers[col_i]
        if show:
            self.show_img(final_pxs)
        return final_pxs


    def k_means_stochastic(self, num_centers=2, num_iterations=1, alpha=0.1):
        # Might be useful:
        # -> pixel_color = self.pixels[pixel_index]
        # -> center_color = self.centers[center_index]
        ### YOUR CODE GOES HERE ###
        print('Running K-means...')
        self.init_centers(num_centers)
        num_pixels = self.pixels.shape[0]
        
        for it in range(num_iterations):
            print('\titeration {}/{}'.format(it+1, num_iterations))
            for px_i in np.random.permutation(num_pixels):
                pixel_color = self.pixels[px_i]
                c = self.find_best_center(pixel_color)
                self.centers[c] += alpha * (pixel_color - self.centers[c])


    def k_means_batch(self, num_centers=2, num_iterations=1, alpha=0.1):
        # Might be useful:
        # -> pixel_color = self.pixels[pixel_index]
        # -> center_color = self.centers[center_index]
        ### YOUR CODE GOES HERE ###
        print('Running K-means...')
        self.init_centers(num_centers)
        num_pixels = self.pixels.shape[0]
        k = 10

        for it in range(num_iterations):
            clusters = self.split_pixels_to_clusters(num_centers)
            changed = False
            for i in range(len(clusters)):
                mean = self.mean(clusters[i])
                if mean is not self.centers[i]:
                    changed = True
                self.centers[i] = mean
            if not changed:
                break



    def mean(self, sample):
        return sum(sample) / len(sample)

            


    def find_best_center(self, pixel_color):
        # Find center that is closest to a given pixel_color.
        # Return index of the center, not its color.
        ### YOUR CODE GOES HERE - OPTIONAL ###
        mn = 0
        for i in range(len(self.centers)):
            if self.distance(self.centers[i], pixel_color) < self.distance(self.centers[mn], pixel_color):
                mn = i
            
        return mn

    def split_pixels_to_clusters(self, num_clusters):
        # Split pixels into num_clusters clusters
        ### YOUR CODE GOES HERE - OPTIONAL ###
        clusters = [[] for _ in range(num_clusters)]
        for pixel_color in self.pixels:
            cluster = self.find_best_center(pixel_color)
            clusters[cluster].append(pixel_color)
        return clusters



if __name__ == '__main__':
    files = [  # comment out images you don`t want
             'gradient.png',
             'win_xp.jpg',
             'lenna.jpg',
             'mona_lisa.jpg'
             ]
    for f in files:
        k = K_Means(f)
        k.k_means_batch(num_centers=5, num_iterations=3)
        k.posterize()
