import os
from sys import argv

from ISR.models import RDN, RRDN
from PIL import Image
import numpy as np


def parse_args():
    parser = argparse.ArgumentParser(description="Pre-process images for GAN training")
    parser.add_argument("indir", type=str, nargs="+", help="Absolute path to the source images")
    args = parser.parse_args()

    if not os.path.isdir(args.indir):
        raise RuntimeError("source path does not exist")


if __name__ == "__main__":
    args = parse_args()

    model = RRDN(weights="gans")  # Load the GAN model that will perform a 4x resize

    for f in os.listdir(args.indir):
        img = Image.open(f"{args.indir}/{f}")
        npimg = np.array(img)  # Convert to numpy image

        add_noise = False
        if add_noise:  # Add some noise
            row, col, ch = npimg.shape
            mean = 0
            var = 0.1
            sigma = var ** 0.5
            gauss = np.random.normal(mean, sigma, (row, col, ch)) * 24

            # Reshape and clip the pixel values
            gauss = gauss.reshape(row, col, ch)
            noisy = np.clip(npimg + gauss, 0, 255).astype("uint8")
            noisy_image = Image.fromarray(noisy)
            npimg = np.array(noisy_image)

        # Resize and save.
        big_img = Image.fromarray(model.predict(npimg))
        filename_no_ext = os.path.splitext(f)[0]
        big_img.save(f"{args.indir}/{filename_no_ext}-post.jpg")
