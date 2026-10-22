import numpy as np
from PIL import Image
import matplotlib.pyplot as plt
from matplotlib.colors import LinearSegmentedColormap
import argparse

cmap = LinearSegmentedColormap.from_list(
    'transparent_red',
    [(1, 0, 0, 0), (1, 0, 0, 0.3)]
)

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
    parser.add_argument('frame', type=int, help="Which frame of the animation to compute")
    parser.add_argument('out_png', help="The name of the output file")
    parser.add_argument('--vmin-vmax', nargs=2, type=float, help="The vmin and vmax to use for the wave panel")
    parser.add_argument('--invert-mask', action='store_true', help="Will use the inverse mask on the Fourier plane to generate the output image")

    args = parser.parse_args()
    vmin, vmax = args.vmin_vmax if args.vmin_vmax is not None else [None, None]

    # Load image and force conversion to greyscale ('L' mode)
    img = np.array(Image.open(args.jpg).convert('L'))

    img_ffted = np.fft.fft2(img)
    img_ffted_shifted = np.fft.fftshift(img_ffted)

    fx = np.fft.fftshift(np.fft.fftfreq(img_ffted_shifted.shape[1], 1/img.shape[1]))
    fy = np.fft.fftshift(np.fft.fftfreq(img_ffted_shifted.shape[0], 1/img.shape[0]))

    # Create an equivalent zero array and use that as the basis for an inverse Fourier transform
    accum_ffted = np.zeros_like(img_ffted, dtype=img_ffted.dtype)
    single_component_ffted = np.zeros_like(img_ffted, dtype=img_ffted.dtype)
    mask = np.full_like(accum_ffted, False, dtype=bool)

    N = np.floor(np.sqrt(args.frame)*5) # This sets the rate at which fourier components get added

    for value, x, y in ulam_double_spiral(N):
        mask[x, y] = True
        mask[-x, -y] = True

        single_component_ffted[:,:] = 0
        single_component_ffted[x, y] = img_ffted[x, y]
        single_component_ffted[-x, -y] = img_ffted[-x, -y]

    if args.invert_mask:
        mask = ~mask

    accum_ffted[mask] = img_ffted[mask]
    accum = np.real(np.fft.ifft2(accum_ffted))
    single_component = np.real(np.fft.ifft2(single_component_ffted))

    fig, axs = plt.subplots(nrows=2, ncols=2, figsize=(8,9.5))
    fig.subplots_adjust(hspace=0.0, wspace=0.0)

    for ax in axs.flat:
        ax.tick_params(which='both', length=0)
        ax.set_xticks([])
        ax.set_yticks([])

    axs[0,0].imshow(img, cmap='grey')
    axs[0,1].pcolormesh(fx, fy, np.log(np.abs(img_ffted_shifted)), cmap='grey')
    axs[0,1].pcolormesh(fx, fy, np.fft.fftshift(mask.astype(int)), cmap=cmap)
    axs[1,0].imshow(single_component, cmap='grey', vmin=vmin, vmax=vmax)
    axs[1,1].imshow(accum, cmap='grey')

    # Zoom out as we go along
    xrad = np.sqrt(N) + 2
    yrad = xrad * img.shape[1] / img.shape[0]

    axs[0,1].set_xlim([-xrad, xrad])
    axs[0,1].set_ylim([-yrad, yrad])

    fig.tight_layout()
    fig.savefig(args.out_png)



if __name__ == '__main__':
    main()
