import scipy.ndimage
import numpy as np
import matplotlib.pyplot as plt
from spectrum import *

def evaluate_color_func(x, func, normalize_each=False):
    img = np.zeros((1,len(x),3))
    for i in range(len(x)):
        col = np.ravel(func(x[i]))
        if normalize_each and np.max(col) > 0.0: col = col / np.max(col)
        col = np.maximum(col, 0.0)
        img[0,i,:] = col
    img *= 1.0 / np.max(np.abs(np.ravel(img)))
    return img

def spectrum_plot(x, *args, **kwargs):
    return_image = kwargs.pop('return_image', False)
    img = evaluate_color_func(x, *args, **kwargs)
    plt.imshow(img, extent=[np.min(x),np.max(x),0,1])
    plt.gca().set_aspect((np.max(x)-np.min(x))*0.1)
    plt.show()
    if return_image: return img

s = Spectrum()

black_body_color = lambda T: s.get_color(s.black_body(T, normalized=True))
temperatures = range(100,20000,100)
bb_hue = spectrum_plot(temperatures, black_body_color, normalize_each=True, return_image=True)[0,:,:]
bb_col = spectrum_plot(temperatures, black_body_color, return_image=True)[0,:,:]

plt.plot(temperatures, bb_hue)
plt.show()
plt.plot(temperatures, bb_col)
plt.show()
plt.plot(temperatures, (bb_col[:,2]+bb_col[:,1])/bb_col[:,0])
plt.show()

single_wavelength_color = lambda nm: s.get_color(s.single_wavelength(nm))
spectrum_plot(range(400,700), single_wavelength_color, normalize_each=True)
spectrum_plot(range(400,700), single_wavelength_color, normalize_each=False)

def shifted_black_body(T):
    return lambda d: s.get_color(s.black_body(T, normalized=True, doppler_factor=d))

for t in [3000,5000,10000]:
    spectrum_plot(np.linspace(0.1,5.0,num=200), shifted_black_body(T=t))

for d in [0.1, 0.5, 1.0, 1.5, 100.0]:
    plt.plot(s.wavelengths, s.black_body(T=5000.0/d, doppler_factor=d, normalized=False)*(d**5))
plt.show()

temperatures = range(64,32*2048,32)
bb_color = spectrum_plot(temperatures, black_body_color, return_image=True)
temperatures = [0,32] + temperatures
bb_color = np.hstack([np.zeros((1,2,3)), bb_color])

sw_color = spectrum_plot(range(0,bb_color.shape[1]), single_wavelength_color, return_image=True)

ratios = np.zeros((bb_color.shape[1],))
ratios[2:] = (bb_color[0,2:,1] + bb_color[0,2:,2]) / bb_color[0,2:,0]

plt.plot(temperatures, ratios)
plt.show()

max_ratio = ratios[-1]
inverse_range = np.linspace(0,max_ratio,num=ratios.size)
inverses = np.interp(inverse_range, ratios, temperatures,
                     left=0, right=temperatures[-1])

inv_tex = np.dstack([inverses[np.newaxis,:,np.newaxis]]*3) / inverses[-1]

plt.plot(inverse_range, inverses)

spectrum_texture = np.vstack((bb_color, sw_color, sw_color, inv_tex))


def apply_in_blocks(function):
    BLOCK_SIZE = 1000

    def blocked_function(self, arr):
        assert (len(arr.shape) == 2)
        n = arr.shape[0]
        blocks = []
        for i0 in range(0, n, BLOCK_SIZE):
            i1 = min(i0 + BLOCK_SIZE, n)
            block = arr[i0:i1, :]
            blocks.append(function(self, block))

        return np.vstack(blocks)

    return blocked_function


class BlackBodyDecomposition:
    def __init__(self):
        self.temperatures = np.ravel(range(100, 100 * 256, 100))
        self.colors = evaluate_color_func(self.temperatures, black_body_color)
        self.hues = evaluate_color_func(self.temperatures, black_body_color, normalize_each=True)
        self.gr_ratios = (self.colors[0, :, 2] + self.colors[0, :, 1]) / self.colors[0, :, 0]

    @apply_in_blocks
    def decompose_array(self, arr):
        assert (len(arr.shape) == 2 and arr.shape[1] == 3)

        magns = np.max(arr, axis=1)
        gr_ratios = (arr[arr[:, 0] > 0, 2] + arr[arr[:, 0] > 0, 1]) / arr[arr[:, 0] > 0, 0]

        temperatures = np.zeros((arr.shape[0],))
        temperatures[arr[:, 0] > 0] = np.interp(gr_ratios, self.gr_ratios, self.temperatures,
                                                left=0, right=self.temperatures[-1])

        return np.hstack((magns[:, np.newaxis], temperatures[:, np.newaxis]))

    def temperature_indices(self, arr):
        n = len(self.temperatures)
        return np.round(np.interp(arr[..., 1], self.temperatures, range(n), left=0, right=n - 1)).astype(int)

    @apply_in_blocks
    def compose_array(self, arr):
        assert (len(arr.shape) == 2 and arr.shape[1] == 2)
        t_indices = self.temperature_indices(arr)
        return self.hues[0, t_indices, :] * arr[:, 0, np.newaxis]

    def decompose_image(self, img):
        assert (len(img.shape) == 3 and img.shape[2] == 3)
        shape0 = img.shape
        arr = np.reshape(img, (shape0[0] * shape0[1], 3))
        r = self.decompose_array(arr)
        return np.reshape(r, (shape0[0], shape0[1], 2))

    def compose_image(self, img):
        assert (len(img.shape) == 3 and img.shape[2] == 2)
        shape0 = img.shape
        arr = np.reshape(img, (shape0[0] * shape0[1], 2))
        r = self.compose_array(arr)
        return np.reshape(r, (shape0[0], shape0[1], 3))

    def save_decomposed(self, img, filename):
        assert (len(img.shape) == 3 and img.shape[2] == 2)
        bright = img[..., 0] / np.max(img[..., 0])
        red = (bright * 255).astype(int)
        green = (self.temperature_indices(img) * bright).astype(int)
        blue = green
        scipy.misc.imsave(filename, np.dstack((red, green, blue)))


src_img = bb_color[:, 10:300, :]
src_img = src_img * 0.9 + np.random.rand(*src_img.shape) * 0.1
src_img[:, :, 1] *= 0.5
dec = BlackBodyDecomposition()
result = dec.decompose_image(src_img)
inv = dec.compose_image(result)

plt.imshow(src_img)
plt.gca().set_aspect(40)
plt.show()
plt.imshow(inv)
plt.gca().set_aspect(40)
plt.show()

