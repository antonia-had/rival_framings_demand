import argparse

if __name__ == '__main__':
    parser = argparse.ArgumentParser(description='Extract monthly and annual flows per realization.')
    parser.add_argument('p', type=str)
    parser.add_argument('i', type=int,
                        help='scenario number')
    parser.add_argument('j', type=int,
                        help='realization number')
    parser.add_argument('k', type=int,
                        help='realization number')
    args = parser.parse_args()
    print("core " + args.p + " would run " + str(args.i) + " " + str(args.j) + " " + str(args.k))
