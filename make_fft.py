import numpy as np
from PIL import Image
import matplotlib.pyplot as plt
import argparse
from matplotlib.animation import FuncAnimation, FFMpegWriter, PillowWriter

def ulam_double_spiral(n):
    x = y = 0
    yield 0, x, y

    step = 1
    value = 2

    while value < n:
        for dx, dy in [(1, 0), (0, 1), (-1, 0), (0, -1)]:
            for _ in range(step):
                if value >= n:
                    return
                x += dx
                y += dy
                yield value, x, y
                value += 1

            if dy != 0:
                step += 2

def main():
    parser = argparse.ArgumentParser(description="Makes an animation of an image of Joseph Fourier being constructed out of accumulated points in the Fourier plane.")
    parser.add_argument('jpg', help="The image to be Fourier transformed")
    parser.add_argument('--vmin-vmax', nargs=2, type=float, help="The vmin and vmax to use for the wave panel")

    args = parser.parse_args()
    vmin, vmax = args.vmin_vmax if args.vmin_vmax is not None else [None, None]

    # Load image and force conversion to greyscale ('L' mode)
    img = np.array(Image.open(args.jpg).convert('L'))

    img_ffted = np.fft.fft2(img)
    img_ffted_shifted = np.fft.fftshift(img_ffted)

    # Create an equivalent zero array and use that as the basis for an inverse Fourier transform
    accum_ffted = np.zeros_like(img_ffted, dtype=img_ffted.dtype)
    single_component_ffted = np.zeros_like(img_ffted, dtype=img_ffted.dtype)

    for value, x, y in ulam_double_spiral(100):
        accum_ffted[x, y] = img_ffted[x, y]
        accum_ffted[-x, -y] = img_ffted[-x, -y]

        single_component_ffted[:,:] = 0
        single_component_ffted[x, y] = img_ffted[x, y]
        single_component_ffted[-x, -y] = img_ffted[-x, -y]

    accum = np.real(np.fft.ifft2(accum_ffted))
    single_component = np.real(np.fft.ifft2(single_component_ffted))

    fig, axs = plt.subplots(nrows=2, ncols=2, figsize=(8,10))
    fig.subplots_adjust(hspace=0.0, wspace=0.0)

    for ax in axs.flat:
        ax.tick_params(which='both', length=0)
        ax.set_xticks([])
        ax.set_yticks([])

    axs[0,0].imshow(img, cmap='grey')
    axs[0,1].imshow(np.log(np.abs(img_ffted_shifted)), cmap='grey')
    axs[1,0].imshow(single_component, cmap='grey', vmin=vmin, vmax=vmax)
    axs[1,1].imshow(accum, cmap='grey')
    plt.show()

    #ani = FuncAnimation(fig, update, frames=100, interval=50, blit=True)


if __name__ == '__main__':
    main()
