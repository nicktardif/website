"""
Usage:
    convert.py (INPUT_DIR) [OUTPUT_DIR]
    convert.py (-h | --help)

Arguments:
    INPUT_DIR   Directory to retrieve input images
    OUTPUT_DIR  Directory to create the build in [default: build]

Options:
    -h --help  Show this screen
"""
from docopt import docopt
from src.generate import generate_website

def main():
    args = docopt(__doc__)
    input_root_dir = args['INPUT_DIR']
    output_root_dir = args['OUTPUT_DIR'] or 'build'
    generate_website(input_root_dir, output_root_dir)

if __name__ == "__main__":
    main()
