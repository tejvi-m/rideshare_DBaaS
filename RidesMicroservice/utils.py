import csv

def find_area(code):
    with open('./data/AreaNameEnum.csv') as csv_file:

        csv_reader = csv.reader(csv_file, delimiter = ',')
        for row in csv_reader:
            if row[0] == code:
                return True
