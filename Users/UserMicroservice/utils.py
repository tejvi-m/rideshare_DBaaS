import hashlib


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
    print(is_sha1(hash("hello")))
    print(hash("hello"))
