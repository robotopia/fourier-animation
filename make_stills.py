import numpy as np
from PIL import Image
import matplotlib.pyplot as plt
from matplotlib.colors import LinearSegmentedColormap
import argparse

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
    parser = argparse.ArgumentParser(description="Makes Fourier transform amps and phases plots of a given input image")
    parser.add_argument('img', help="The image to be Fourier transformed")
    parser.add_argument('--amp-cmap', default='gray', help="The color map to use for the amplitudes (default: gray)")
    parser.add_argument('--phase-cmap', default='hsv_r', help="The color map to use for the phases (default: hsv_r)")
    parser.add_argument('--out-type', default='png', help="The image type for the output files (default: png)")

    args = parser.parse_args()

    # Load image and force conversion to greyscale ('L' mode)
    img = np.array(Image.open(args.img).convert('L'))
    img_stem = args.img[:args.img.rfind('.')]
    out_amp = f'{img_stem}_amp.{args.out_type}'
    out_phase = f'{img_stem}_phase.{args.out_type}'

    img_ffted = np.fft.fft2(img)
    img_ffted_shifted = np.fft.fftshift(img_ffted)

    fx = np.fft.fftshift(np.fft.fftfreq(img_ffted_shifted.shape[1], 1/img.shape[1]))
    fy = np.fft.fftshift(np.fft.fftfreq(img_ffted_shifted.shape[0], 1/img.shape[0]))

    fig = plt.figure(figsize=(8,8))

    # Amplitudes
    plt.pcolormesh(fx, fy, np.log10(np.abs(img_ffted_shifted)), cmap=args.amp_cmap)
    plt.xlabel("Spatial frequency (pixel$^{-1}$)")
    plt.ylabel("Spatial frequency (pixel$^{-1}$)")
    plt.colorbar(label="log$_{10}$(Amplitude)")

    plt.tight_layout()
    plt.savefig(out_amp)

    plt.clf()

    # Phases
    plt.pcolormesh(fx, fy, np.angle(img_ffted_shifted, deg=True), cmap=args.phase_cmap, vmin=-180, vmax=180)
    plt.xlabel("Spatial frequency (pixel$^{-1}$)")
    plt.ylabel("Spatial frequency (pixel$^{-1}$)")
    plt.colorbar(label="Phase (degrees)")

    plt.tight_layout()
    plt.savefig(out_phase)



if __name__ == '__main__':
    main()
