import uuid
import pathlib
import argparse
import src.cluster


def get_arguments():
    filetype = argparse.FileType("r", encoding="utf-8")
    defaulthelp = argparse.ArgumentDefaultsHelpFormatter
    rawdescription = argparse.RawDescriptionHelpFormatter
    parser = argparse.ArgumentParser(description="SEO Operations.")
    subparsers = parser.add_subparsers(help="commands", dest="command")
    cluster = subparsers.add_parser(name="cluster", formatter_class=rawdescription, description=src.cluster.__doc__, help="cluster search terms")
    cluster.add_argument("kwfile", type=filetype, help="keywords file (.txt or .csv)")
    cluster.add_argument("-s", type=str, help="similarity algorithm", default="leven", metavar="[leven, demerau]")
    import numpy as np
    cluster.add_argument("-d", type=float, help="damping", default=0.9, metavar="[0.5 - 1.0]")
    return parser.parse_args()


def main():
    arguments = get_arguments()
    if arguments.command == "cluster":
        keywords = arguments.kwfile.read().splitlines()
        distance = arguments.s
        damping = arguments.d
        uid = str(uuid.uuid4())
        fpath = pathlib.Path(f"~/Desktop/urlmap_{uid}.csv").expanduser()
        src.cluster.cluster_keywords(keywords, distance, damping, fpath)
        print(f"complete ~ find your output @ {fpath}")
        

if __name__ == "__main__":
    main()
