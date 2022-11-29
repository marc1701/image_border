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
    bottom_weighted=False, verbose=False, bg_luminance=0.965):
    
    cheight, cwidth = canvas_size
    imheight, imwidth, nchannels = image.shape

    # a bit of a fudge
    if bg_luminance == 1:
        bgcolor = 255
    elif bg_luminance == 0:
        bgcolor = 0
    else:
        bgcolor = move_luminance(rgbimage_mean_colour(image), bg_luminance)

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
    # NEEDS COMPENSATING FOR GAMMA
    return np.sum(colour * np.array([0.2126, 0.7152, 0.0722]))


def c_lin(c_srgb):
    '''Converts gamma-adjusted sRGB values to linear'''
    if type(c_srgb) == np.ndarray:
        c_arr = np.zeros_like(c_srgb)
        for i, c in enumerate(c_srgb):
            c_arr[i] = c_lin(c)
        return c_arr
        
    if c_srgb <= 0.04045:
        return c_srgb/12.92
    elif c_srgb > 0.04045:
        return ((c_srgb + 0.055) / 1.055)**2.4


def c_srgb(c_lin):
    '''Converts linear values to sRGB gamma'''
    if type(c_lin) == np.ndarray:
        c_arr = np.zeros_like(c_lin)
        for i, c in enumerate(c_lin):
            c_arr[i] = c_srgb(c)
        return c_arr

    if c_lin <= 0.0031308:
        return 12.92*c_lin
    elif c_lin > 0.003108:
        return (1.055*c_lin**(1/2.4)) - 0.055


def move_luminance(colour, luminance):
    
    luminance = int(luminance*255)
    luma = perceptual_luminance(colour)
    colour = np.copy(colour)

    if luma < luminance:
        while luma < luminance:
            
            # increment brightness
            colour += 1

            # calculate perceptual luminance
            luma = int(perceptual_luminance(colour))

            # clip values
            colour[colour > 255] = 255
    
    elif luma > luminance:
        while luma > luminance:
            
            # increment brightness
            colour -= 1

            # calculate perceptual luminance
            luma = int(perceptual_luminance(colour))

            # clip values
            colour[colour < 0] = 0

    return colour


def parse_args():
    parser = argparse.ArgumentParser(description='Add borders to images.')
    
    parser.add_argument('input_filepath', 
        help='Path of image to process.')
    parser.add_argument('border', type=int, 
        help='Border thickness in pixels.')
    parser.add_argument('cheight', type=int,
        help='Height of background canvas in pixels.')
    parser.add_argument('cwidth', type=int,
        help='Width of background canvas in pixels.')

    parser.add_argument('--bgluminance', default=0.965, type=float,
        help='Set luminance of background canvas.')
    parser.add_argument('--verbose', action='store_true',
        help='Set verbosity (printing of output messages).')
    parser.add_argument('--output_filename', 
        help='Name for output file.')
    parser.add_argument('--btmwght', action='store_true', 
        help='Enable bottom weighting.')
    parser.add_argument('--output_dir', default='.', 
        help='Directory for output files.')
    parser.add_argument('--jpegquality', default=95, type=int, 
        help='Quality of output jpeg file.')
    

    return parser.parse_args()

if __name__ == "__main__":
    args = parse_args()

    main(args.input_filepath,
         args.output_filename,
         args.output_dir,
         args.jpegquality,
         canvas_size=(args.cheight, args.cwidth),
         border=args.border,
         bottom_weighted=args.btmwght,
         verbose=args.verbose,
         bg_luminance=args.bgluminance)

# e.g.
# python3 white_border.py fox_mural.jpg 80 2160 2160 --output_filename fox10.jpg --bgluminance 0.25