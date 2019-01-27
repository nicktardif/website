"""
Usage:
    main.py generate INPUT_DIR [OUTPUT_DIR]
    main.py deploy BUILD_DIR
    main.py (-h | --help)

Arguments:
    INPUT_DIR   Directory to retrieve input images
    OUTPUT_DIR  Directory to create the build in [default: build]

Options:
    -h --help  Show this screen
"""
from docopt import docopt
from src.generate import generate_website
from src.deploy import deploy_website

def main():
    args = docopt(__doc__)

    if args['generate']:
        print('Generating a website')
        input_root_dir = args['INPUT_DIR']
        output_root_dir = args['OUTPUT_DIR'] or 'build'
        generate_website(input_root_dir, output_root_dir)
    elif args['deploy']:
        print('Deploying the website')
        build_dir = args['BUILD_DIR']
        deploy_website(build_dir)

if __name__ == "__main__":
    main()
