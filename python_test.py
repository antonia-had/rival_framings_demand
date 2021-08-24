import argparse
import time

if __name__ == '__main__':
    parser = argparse.ArgumentParser(description='Extract monthly and annual flows per realization.')
    parser.add_argument('i', type=int,
                        help='scenario number')
    parser.add_argument('j', type=int,
                        help='realization number')
    parser.add_argument('k', type=int,
                        help='realization number')
    args = parser.parse_args()
    t = time.localtime()
    current_time = time.strftime("%H:%M:%S", t)
    print(current_time)
    print("this script would run " + str(args.i) + " " + str(args.j) + " " + str(args.k))
