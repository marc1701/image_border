# Image Border
Simple tool to add borders to image files. Default usage from python shell places images in 2160px square background with a minimum border of 80px on the longest edge, with a background of 85% luminance. Background colour hue automatically chosen from input image. The default output filename is the input name with `_border` appended.

The option `-btmwght` is included for 'bottom weighting', sometimes used in galleries to position the image at the 'visual centre' of a frame when mounting. This works better with larger borders. Note that in the event that the smallest border would be on the vertical, the image will be rescaled to the size required for absolute centring, resulting in a smaller border at top than specified. This enables the user to try out both positioning options on the same effective image enlargement, whereas if the border width was strictly maintained, this would result in a rescaling of the image.

####Positional Arguments:
  ```
  input_filepath        Path of image to process.
  border                Border thickness in pixels.
  cheight               Height of background canvas in pixels.
  cwidth                Width of background canvas in pixels.
  ```

####Optional Arguments:
  ```
  -h, --help            show this help message and exit
  --bgluminance         Set luminance of background canvas.
  --verbose             Set verbosity (printing of output messages).
  --output_filename     Name for output file.
  --btmwght             Enable bottom weighting.
  --output_dir          Directory for output files.
  --jpegquality         Quality of output jpeg file.
  ```

####Usage Example:
`python3 image_border.py input_image.jpg 80 2160 2160 --output_filename output_file.jpg --bgluminance 0.95`