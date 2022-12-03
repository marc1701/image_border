#!/opt/homebrew/bin/python3
import os
import argparse
import warnings
import numpy as np
from skimage import io
from pathlib import Path
from skimage.transform import rescale

def main(input_filepath, output_filename=None, 
    output_dir='.', quality=95, **kwargs):

    image = io.imread(input_filepath)

    if len(image.shape) < 3:
        # add channel dimension to monochrome images
        image = np.expand_dims(image, 2)

    wb = add_border(image, **kwargs)

    if not output_filename:
        output_filename = f'{Path(input_filepath).stem}_border.jpg'
        
    outpath = f'{output_dir}/{output_filename}'
    io.imsave(outpath, wb.astype(np.uint8), quality=quality)
    if args.verbose: print(f'Saved as {outpath}')
    

def add_border(image, canvas_size=(2160, 2160), border=80, 
    bottom_weighted=False, verbose=False, bg_luminance=1):
    
    cheight, cwidth = canvas_size
    imheight, imwidth, nchannels = image.shape

    # a bit of a fudge
    if bg_luminance == 1: bgcolor = 255
    elif bg_luminance == 0: bgcolor = 0
    else: bgcolor = move_luminance(rgbimage_mean_colour(image), bg_luminance)

    # make a white background array
    canvas = np.ones((*canvas_size, nchannels), dtype=np.uint8) * bgcolor

    # calculate scale factors in either dimension, retain the smallest
    vscale = (cheight - border*2) / imheight
    hscale = (cwidth - border*2) / imwidth
    rescale_factor = min(vscale, hscale)
    
    if rescale_factor > 1:
        warnings.warn('Image will be scaled up')
    
    if rescale_factor != 1:
        image = rescale(image, rescale_factor, 
            preserve_range=True, channel_axis=2)
        if verbose: print(f'Image rescaled by factor {rescale_factor}')
    else: 
        if verbose: print('Image not rescaled')

    imheight, imwidth, _ = image.shape
    vspace = (cheight - imheight) // 2
    hspace = (cwidth - imwidth) // 2

    if bottom_weighted:
        offset = round((vspace/cwidth)*hspace)
        vspace = vspace - offset

    # add image to canvas
    canvas[vspace:vspace+imheight, hspace:hspace+imwidth] = image

    return canvas


def rgbimage_mean_colour(image):
    return np.mean(np.mean(image, axis=0), axis=0).astype(int)


def perceptual_luminance(colour):
    return np.sum(colour * np.array([0.2126, 0.7152, 0.0722]))


def move_luminance(colour, luminance):
    
    luminance = int(luminance*255)
    luma = perceptual_luminance(colour)
    colour = np.copy(colour)

    if luma != luminance:
        
        inc = 1 if luma < luminance else -1
        
        while luma != luminance:
            
            # increment brightness
            colour += inc

            # calculate perceptual luminance
            luma = int(perceptual_luminance(colour))

            # clip values
            colour = np.clip(colour, 0, 255)

    return colour


def parse_args():
    parser = argparse.ArgumentParser(description='Add borders to images.')
    
    parser.add_argument('infiles', nargs='+',
        help='Path(s) of image(s) to process.')
    parser.add_argument('border', type=int, 
        help='Border thickness in pixels.')
    parser.add_argument('cheight', type=int,
        help='Height of background canvas in pixels.')
    parser.add_argument('cwidth', type=int,
        help='Width of background canvas in pixels.')

    parser.add_argument('-l', '--bgluminance', default=1, type=float,
        help='Set luminance of background canvas.')
    parser.add_argument('-v', '--verbose', action='store_true',
        help='Set verbosity (printing of output messages).')
    parser.add_argument('-o', '--outfile', 
        help='Name for output file.')
    parser.add_argument('-b', '--btmwght', action='store_true', 
        help='Enable bottom weighting.')
    parser.add_argument('-d', '--outdir', default='.', 
        help='Directory for output files.')
    parser.add_argument('-j', '--jpegquality', default=95, type=int, 
        help='Quality of output jpeg file.')
    

    return parser.parse_args()

if __name__ == "__main__":
    args = parse_args()

    for file in args.infiles:
        main(file,
             args.outfile,
             args.outdir,
             args.jpegquality,
             canvas_size=(args.cheight, args.cwidth),
             border=args.border,
             bottom_weighted=args.btmwght,
             verbose=args.verbose,
             bg_luminance=args.bgluminance)