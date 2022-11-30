# Image Border
Simple tool to add borders to image files. Default usage from python shell places images in 2160px square background with a minimum border of 80px on the longest edge, with a background of 85% luminance. Background colour hue automatically chosen from input image. The default output filename is the input name with `_border` appended.

The option `-btmwght` is included for 'bottom weighting', sometimes used in galleries to position the image at the 'visual centre' of a frame when mounting. This works better with larger borders. Note that in the event that the smallest border would be on the vertical, the image will be rescaled to the size required for absolute centring, resulting in a smaller border at top than specified. This enables the user to try out both positioning options on the same effective image enlargement, whereas if the border width was strictly maintained, this would result in a rescaling of the image.

#### Positional Arguments:
  ```
  infile                Path of image to process.
  border                Border thickness in pixels.
  cheight               Height of background canvas in pixels.
  cwidth                Width of background canvas in pixels.
  ```

#### Optional Arguments:
  ```
  -l, --bgluminance     Set luminance of background canvas.
  -v, --verbose         Set verbosity (printing of output messages).
  -o, --outfile         Name for output file.
  -b, --btmwght         Enable bottom weighting.
  -d, --outdir          Directory for output files.
  -j, --jpegquality     Quality of output jpeg file.
  ```

#### Usage Example:
`python3 image_border.py in.jpg 80 2160 2160 --output_filename out.jpg --bgluminance 0.95`

 `python3 image_border.py in.jpg 80 2160 2160 -o out.jpg -l 0.95`
