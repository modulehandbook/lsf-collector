from argparser import parser
from collect import run
def json2csv():
    # Use a breakpoint in the code line below to debug your script.
    args = parser.parse_args()
    run(args)



# Press the green button in the gutter to run the script.
if __name__ == '__main__':
    json2csv()

# See PyCharm help at https://www.jetbrains.com/help/pycharm/
