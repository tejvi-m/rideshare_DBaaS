import csv
import hashlib


def find_area(code):
    with open('data/AreaNameEnum.csv') as csv_file:

        csv_reader = csv.reader(csv_file, delimiter = ',')
        for row in csv_reader:
            if row[0] == code:
                return True

def hash(plaintext):
    return hashlib.sha1(plaintext.encode()).hexdigest()

def is_sha1(hash):
    if len(hash) != 40:
        return False
    try:
        sha = int(hash, 16)
    except ValueError:
        return False
    return True

if __name__ == '__main__':
    # area = input()
    # print(find_area(area))
    print(is_sha1(hash("hello") + "1"))
    print(hash("hello"))
