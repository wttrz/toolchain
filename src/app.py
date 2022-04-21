import uuid
import pathlib
import argparse
from src.cluster import cluster_keywords
from src.cluster import __doc__ as cluster_doc
from src.competition import enumerate_competition
from src.competition import __doc__ as competition_doc


def get_arguments():
    filetype = argparse.FileType("r", encoding="utf-8")
    defaulthelp = argparse.ArgumentDefaultsHelpFormatter
    rawdescription = argparse.RawDescriptionHelpFormatter
    parser = argparse.ArgumentParser(description="SEO Operations.")
    subparsers = parser.add_subparsers(help="commands", dest="command")
    cluster = subparsers.add_parser(name="cluster", formatter_class=rawdescription, description=cluster_doc, help="cluster search terms")
    cluster.add_argument("kwfile", type=filetype, help="keywords file (.txt or .csv)")
    cluster.add_argument("-s", type=str, help="similarity algorithm", default="leven", metavar="[leven, demerau]")
    cluster.add_argument("-d", type=float, help="damping factor", default=0.9, metavar="[0.5 - 1.0]")
    competition = subparsers.add_parser(name="competition", formatter_class=rawdescription, description=competition_doc, help="find competing domains")
    competition.add_argument("kwfile", type=filetype, help="keyword file (.txt or .csv)")
    competition.add_argument("-l", type=str, help="location", default="Sweden")
    return parser.parse_args()


def main():
    arguments = get_arguments()
    uid = str(uuid.uuid4())
    if arguments.command == "cluster":
        keywords = arguments.kwfile.read().splitlines()
        distance = arguments.s
        damping = arguments.d
        fpath = pathlib.Path(f"~/Desktop/urlmap_{uid}.csv").expanduser()
        cluster_keywords(keywords, distance, damping, fpath)
    if arguments.command == "competition":
        keywords = arguments.kwfile.read().splitlines()
        location = arguments.l.title()
        fpath = pathlib.Path(f"~/Desktop/competition_{uid}.txt").expanduser()
        enumerate_competition(keywords, location, fpath)
    print(f"complete ~ find your output @ {fpath}")
        

if __name__ == "__main__":
    main()
