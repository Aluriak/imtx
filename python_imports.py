

import os
import itertools
import functools, collections, importlib, pytest, inspect, re

import gizeh
import rdflib

from imtx import write_merged_image


MODULES = (
    # functools,
    rdflib,
    # re,
    # collections,
    # importlib,
    # pytest,
    # inspect,
)

TEXTFILE_TEMPLATE = 'examples/{}.py'
INIMAGE_TEMPLATE = 'examples/import_{}.png'
OUTIMAGE_TEMPLATE = 'examples/import_{name}_{name}.png'


def get_source_code(module, *, line_sep:str='', file_sep:str='') -> str or None:
    """Return the string containing all code of given python module.

    line_sep -- string joining the lines
    file_sep -- string joining the files

    If given module is found to be a package (like importlib) because
    the spec origin is an __init__.py, other files in the package
    will be concatenated and used.

    If module have no python sources (itertools for example), return value
    would be None.

    """
    source = ''
    for file in files_of_package(module):
        with open(file) as fd:
            source += file_sep + line_sep.join(line.strip() for line in fd)
    return source[len(file_sep):]  # return without the leading file separator


def files_of_package(module) -> frozenset:
    """Return frozenset of files composing the given module.

    If given module have no python sources, returned container is empty.

    """
    module_path = module.__spec__.origin
    if not os.path.exists(module_path): return frozenset()  # non valid module
    path, filename = os.path.split(module_path)
    module_files = {module_path}
    # get eventual other files if module is a package
    if filename == '__init__.py':  # there is other source files
        for entry in os.scandir(path):
            if entry.is_file() and entry.name.endswith('.py'):
                module_files.add(os.path.join(path, entry.name))
    return frozenset(module_files)


# NON WORKING ; gizeh works poorly with text
def write_png_text(outfile:str, text:str, colors:iter,
                   fontsize:int, fontfamily:str, bg_color=(255, 255, 255)):
    """Write in outfile given text using given font settings and given colors."""
    width, height = fontsize*len(text), fontsize*2
    words = text.split()
    if len(colors) != len(text):
        assert len(colors) == len(words), "colors should be given for each letter, or for each word"
        colors = tuple(itertools.chain.from_iterable(
            [color] * len(word) for color, word in zip(colors, words)
        ))

    # init surface
    surface = gizeh.Surface(width=width, height=height)
    gizeh.rectangle(
        xy=(width//2, height//2),
        lx=width,
        ly=height,
        fill=bg_color
    ).draw(surface)
    # colors = (0, 0, 0)
    # gizeh.text(
        # text, stroke=colors, fill=colors,
        # xy=(width//2, 0+height//2),
        # fontsize=fontsize, fontfamily=fontfamily,
        # v_align='top',
        # fontweight='bold',
    # ).draw(surface)
    for idx, letter, color in zip(itertools.count(), text, colors):
        gizeh.text(
            letter, stroke=color, fill=color,
            xy=(idx*fontsize*0.7+width//2, 0+height//2),
            fontsize=fontsize, fontfamily=fontfamily,
            v_align='top',
            fontweight='bold',
        ).draw(surface)
    surface.write_to_png(outfile)


if __name__ == "__main__":
    for module in MODULES:
        module_name = module.__spec__.name
        TEXT = get_source_code(module)
        print(module_name + ':')
        print('\n' + str(write_merged_image(
            INIMAGE_TEMPLATE.format(module_name), TEXT,
            output=OUTIMAGE_TEMPLATE.format(name=module_name),
            text_size=25,
            text_font='Source Code Pro',
            adjust=0.85,
            term_width=80,
        )))
