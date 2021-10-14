#!/usr/bin/env python3
import os

import imgaug as ia
from imgaug import augmenters as iaa
import numpy as np
from PIL import Image, UnidentifiedImageError

from common import raw_path, resized_path


def delete_bad_images(bad_images: list):
    while True:
        yes_no = str(input("The following images had errors, would you like to delete them? "))
        if not yes_no or yes_no.lower() not in ["yes", "no"]:
            print("just give a yes or no answer!")
            continue
        elif yes_no == "yes":
            for i in bad_images:
                print(f"deleting {i}")
                os.remove(i)


if __name__ == "__main__":
    # set up some parameters
    size = 1024
    num_augmentations = 6

    # set up the image augmenter
    seq = iaa.Sequential(
        [
            iaa.Rot90((0, 3)),
            # iaa.Fliplr(0.5),
            iaa.PerspectiveTransform(scale=(0.0, 0.05), mode="replicate"),
            iaa.AddToHueAndSaturation((-20, 20)),
        ]
    )

    bad_images = []
    # loop through the images, resizing and augmenting
    path, dirs, files = next(os.walk(raw_path))
    for file in sorted(files):
        if not file.endswith(tuple([".jpeg", ".jpg"])):
            continue
        print(file)
        try:
            image = Image.open(path + "/" + file)
        except UnidentifiedImageError as e:
            bad_images.append(file)

        if image.mode == "RGB":
            image.save(resized_path + "/" + file)
            image_resized = image.resize((size, size), resample=Image.BILINEAR)
            image_np = np.array(image_resized)
            images = [image_np] * num_augmentations
            images_aug = seq(images=images)
            for i in range(0, num_augmentations):
                im = Image.fromarray(np.uint8(images_aug[i]))
                to_file = resized_path + "/" + file[:-4] + "_" + str(i).zfill(2) + ".jpg"
                im.save(to_file)  # , quality=95)
    if bad_images:
        delete_bad_images(bad_images)
