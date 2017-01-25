from imtx import write_merged_image


if __name__ == "__main__":
    with open('examples/functools.py') as fd:
        TEXT = ''.join(line.strip() for line in fd)
    print('\n' + str(write_merged_image(
        'examples/import_functools.png', TEXT,
        output='examples/import_functools_functools.png',
        text_size=25,
        text_font='Source Code Pro',
        adjust=0.8,
        term_width=80,
    )))
