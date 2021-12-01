import os
from sys import argv

import numpy as np
from PIL import Image
from ISR.models import RDN, RRDN

path = argv[1]
if not os.path.isdir(path):
    raise RuntimeError("Given path does not exist")

# Import the image
for f in os.listdir(path):
    img = Image.open(f"{path}/{f}")
    model = RRDN(weights="gans")  # Load the GAN model that will perform a 4x resize
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
    big_img.save(f"{path}/{filename_no_ext}-post.jpg")
