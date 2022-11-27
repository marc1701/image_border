import os
import argparse
import warnings
import numpy as np
from skimage import io
from pathlib import Path
from skimage.transform import rescale

def main(input_filepath, output_filename=None, output_dir='.', quality=95, **kwargs):

    image = io.imread(input_filepath)

    if len(image.shape) < 3:
        # add channel dimension to monochrome images
        image = np.expand_dims(image, 2)

    wb = add_border(image, **kwargs)

    if not output_filename:
        output_filename = f'{Path(input_filepath).stem}_wb.jpg'
        
    outpath = f'{output_dir}/{output_filename}'
    io.imsave(outpath, wb, quality=quality)
    if args.verbose: print(f'Saved as {outpath}')
    

def add_border(image, canvas_size=(2160, 2160), thinnest_border=80, verbose=False):
    
    cheight, cwidth = canvas_size
    imheight, imwidth, nchannels = image.shape

    # make a white background array
    canvas = np.ones((*canvas_size, nchannels), dtype=np.uint8) * 255

    # calculate scale factors in either dimension, retain the smallest
    vscale = (cheight - thinnest_border*2) / imheight
    hscale = (cwidth - thinnest_border*2) / imwidth
    rescale_factor = min(vscale, hscale)
    
    if rescale_factor > 1:
        warnings.warn('Image will be scaled up')
    
    if rescale_factor != 1:
        image = rescale(image, rescale_factor, preserve_range=True, channel_axis=2)
        if verbose: print(f'Image rescaled by factor {rescale_factor}')
    else: 
        if verbose: print('Image not rescaled')

    imheight, imwidth, _ = image.shape
    vspace = (cheight - imheight) // 2
    hspace = (cwidth - imwidth) // 2

    # add image to canvas
    canvas[vspace:vspace+imheight, hspace:hspace+imwidth] = image

    return canvas

#
# could add an additional option for 'gallery' centering 
# (e.g. slightly higher than centre)
#
# could have option for background colour / automatic colour selection

def parse_args():
    parser = argparse.ArgumentParser(description='Add white borders to images.')
    
    parser.add_argument('input_filepath', help='Path of image to process.')
    parser.add_argument('border', help='Thinnest border thickness in pixels.', type=int)
    parser.add_argument('cheight', help='Height of background canvas in pixels.', type=int)
    parser.add_argument('cwidth', help='Width of background canvas in pixels.', type=int)

    parser.add_argument('--output_dir', default='.', help='Directory for output files.')
    parser.add_argument('--jpegquality', default=95, type=int, help='Quality of output jpeg file.')
    parser.add_argument('--verbose', action='store_true')
    parser.add_argument('--output_filename', help='Name for output file.')

    return parser.parse_args()

if __name__ == "__main__":
    args = parse_args()

    main(args.input_filepath,
         args.output_filename,
         args.output_dir,
         args.jpegquality,
         canvas_size=(args.cheight, args.cwidth),
         thinnest_border=args.border,
         verbose=args.verbose)