"""

usage:
    imtx.py <input-filename> <text> <output-filename> [options]

options:
    --help, -h          show this help
    --progress-bar      show a progress bar
    --text-size=int     text size in output image           [default: 20]
    --text-font=font    text font in output image           [default: FreeSerif]
    --adjust=float      ratio applyied on output image      [default: 0.7]

"""

import shutil
import itertools
from itertools import zip_longest, cycle

import png
import gizeh
import docopt


DEFAULT_BACKGROUND = (255, 255, 255)
TERM_WIDTH = shutil.get_terminal_size().columns
NB_RGBA = 4


def grouper(iterable, n, fillvalue=None):
    "Collect data into fixed-length chunks or blocks"
    # grouper('ABCDEFG', 3, 'x') --> ABC DEF Gxx"
    args = [iter(iterable)] * n
    return zip_longest(*args, fillvalue=fillvalue)



def image_reader(input_image:str):
    reader = png.Reader(filename=input_image)
    return reader.asRGBA()


def color255_to_color_ratio(color:tuple) -> tuple:
    """Return normalized color, without the alpha channel if given"""
    return tuple(sub/255 for sub in color)[:3]


def write_merged_image(image:str, text:str, output:str,
                       text_size:int=20, term_width:int=None,
                       text_font:str='Impact',
                       x_just:float=0.8, y_just:float=0.8, adjust:float=None,
                       background_consume_text:bool=False,
                       background:tuple=None):
    """Perform the interlacing treatment on image found in given file and
    given text.

    image -- filename containing png data
    text -- text to integrate in output image
    output -- output filename
    text_size -- text size in output image
    term_width -- if given, allow a progress bar to appear during treatment
    text_font -- text font family in output image
    x_just -- ratio applied on distances between letters of same row
    y_just -- ratio applied on distances between letters of same column
    adjust -- if given, ratio overwritting x_just and y_just
    background_consume_text -- if True, text will not be cut by background color
    background -- background color, overwrite background color found in metadata

    """
    if adjust:
        x_just = y_just = adjust
    width, height, pixels, meta = image_reader(image)
    outwidth = int(width * text_size * x_just)
    outheight = int(height * text_size * y_just)
    text = cycle(text)

    surface = gizeh.Surface(width=outwidth, height=outheight)
    # write the background
    bg_color = color255_to_color_ratio(
        background or meta.get('background', DEFAULT_BACKGROUND)
    )
    gizeh.rectangle(
        xy=(outwidth//2, outheight//2),
        lx=outwidth,
        ly=outheight,
        fill=bg_color
    ).draw(surface)

    # write the letters themselves
    for nol, line in enumerate(pixels):
        if term_width:
            oks = ('>' * int(nol/height * term_width)).ljust(term_width)
            print('\r[' + oks + ']', end='', flush=True)
        for idx, color in enumerate(grouper(line, NB_RGBA)):
            color = color255_to_color_ratio(color)
            if color == bg_color and not background_consume_text:
                continue
            letter = next(text)
            todraw = gizeh.text(
                letter, stroke=color, fill=color,
                xy=(idx*text_size*x_just+text_size//2, nol*text_size*y_just+text_size//2),
                fontsize=text_size, fontfamily=text_font,
                v_align='top',
                fontweight='bold',
            )
            todraw.draw(surface)

    surface.write_to_png(output)


if __name__ == "__main__":
    args = docopt.docopt(__doc__)

    write_merged_image(
        args['<input-filename>'], args['<text>'],
        term_width=(TERM_WIDTH//4 if args['--progress-bar'] else None),
        output=args['<output-filename>'],
        text_size=int(args['--text-size']),
        text_font=args['--text-font'],
        adjust=float(args['--adjust']),
        # text_font='Source Code Pro',
        # text_font='FreeSerif',
        # text_font='FreeSans',
        # text_font='Oxygen-Sans',
    )
