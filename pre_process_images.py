#!/usr/bin/env python3
import os

import argparse
import imgaug as ia
from imgaug import augmenters as iaa
import numpy as np
from PIL import Image, UnidentifiedImageError


def parse_args():
    parser = argparse.ArgumentParser(description="Pre-process images for GAN training")
    parser.add_argument("indir", type=str, nargs="+", help="Absolute path to the source (raw-downloaded) images")
    parser.add_argument(
        "outdir", type=str, nargs="+", help="Absolute path where the pre-processed files should be stored"
    )
    parser.add_argument("project", type=str, nargs="+", help="Name of the project")
    args = parser.parse_args()

    if not os.path.isdir(args.indir):
        raise RuntimeError("source path does not exist")
    if not os.path.isdir(args.outdir):
        raise RuntimeError("outdir does not exist")


def delete_bad_images(bad_images: list):
    print("The following images had errors")
    for path in bad_images:
        print(path)
    while True:
        yes_no = str(input("Would you like to delete them? "))
        if not yes_no or yes_no.lower() not in ["yes", "no"]:
            print("com'on man, just give a yes or no answer!")
            continue
        elif yes_no == "yes":
            for path in bad_images:
                print(f"deleting {path}")
                os.remove(f"{path}")
        break


if __name__ == "__main__":
    args = parse_args()

    outdir = os.path.join(args.outdir, args.project, "preprocessed")
    if not os.path.isdir(outdir):
        os.mkdir(outdir)

    # Set up some parameters.
    size = 1024
    num_augmentations = 6

    # Set up the image augmenter. This will return a series of images that have been augmented in various ways, such
    # as flipped, perspective-shifted, color-shifted, etc.
    seq = iaa.Sequential(
        [
            iaa.Rot90((0, 3)),
            # iaa.Fliplr(0.5),
            iaa.PerspectiveTransform(scale=(0.0, 0.05), mode="replicate"),
            iaa.AddToHueAndSaturation((-20, 20)),
        ]
    )

    bad_images = []
    # loop through the images, resizing and augmenting.
    path, dirs, files = next(os.walk(args.indir))
    for file in sorted(files):
        if not file.endswith(tuple([".jpeg", ".jpg"])):
            continue

        infile = os.path.join(path, file)
        outfile = os.path.join(outdir, file)
        print(infile)

        try:
            image = Image.open(infile)
        except UnidentifiedImageError as e:
            bad_images.append(infile)
            continue
        if image.mode != "RGB":
            bad_images.append(infile)
            continue

        image_resized = image.resize((size, size), resample=Image.BILINEAR)
        augmented_images = seq(images=([np.array(image_resized)] * num_augmentations))

        for i, img in enumerate(augmented_images):
            Image.fromarray(np.uint8(img)).save(
                outdir + file[:-4] + "_" + str(i).zfill(2) + ".jpg",
                quality=95,
            )
    if bad_images:
        delete_bad_images(bad_images)
