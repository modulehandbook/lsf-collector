import argparse

parser = argparse.ArgumentParser(
                    prog='json2csv',
                    description='Converts LSF Scraper output to various CSV formats.',
                    epilog='...')

parser.add_argument('filename')           # positional argument
parser.add_argument('-o', '--output')      # option that takes a value
parser.add_argument('-c', '--courselist',
                    action='store_true')
parser.add_argument('-v', '--verbose',
                    action='store_true')  # on/off flag
