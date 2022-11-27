import warnings
import numpy as np
from skimage import io
from skimage.transform import rescale

def main(input_filepath, output_filepath=None, quality=95, **kwargs):

    image = io.imread(input_filepath)

    if len(image.shape) < 3:
        # add channel dimension to monochrome images
        image = np.expand_dims(image, 2)

    wb = add_white_border(image, **kwargs)

    if not output_filepath: 
        output_filepath = f'{input_filepath}_wb.jpg'

    io.imsave(wb, output_filepath, quality=quality)
    

def add_white_border(image, canvas_size=(2160, 2160), thinnest_border=80, verbose=False):
    
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
        if verbose: print(f'Rescaling image by factor {rescale_factor}')
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