from api.db.exeption import *

def main():
    try:
        raise PeerAlreadyExist('bla bla')
    except PeerAlreadyExist as e:
        print(e)


if __name__ == '__main__':
    main()
