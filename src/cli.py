import uuid
import pathlib
import argparse
from src.cluster import cluster_keywords
from src.cluster import __doc__ as cluster_doc
from src.competition import enumerate_competition
from src.competition import __doc__ as competition_doc
from src.kwlist import get_kwlist
from src.kwlist import __doc__ as kwlist_doc
from src.urlmap import map_domain
from src.urlmap import __doc__ as urlmap_doc
from src.onpage import pfetch
from src.onpage import __doc__ as onpage_doc


def get_arguments():
    filetype = argparse.FileType("r", encoding="utf-8")
    defaulthelp = argparse.ArgumentDefaultsHelpFormatter
    rawdescription = argparse.RawDescriptionHelpFormatter
    parser = argparse.ArgumentParser(description="SEO Operations.")
    subparsers = parser.add_subparsers(help="commands", dest="command")
    cluster = subparsers.add_parser(
        name="cluster",
        formatter_class=rawdescription,
        description=cluster_doc,
        help="cluster search terms",
    )
    cluster.add_argument("kwfile", type=filetype, help="keywords file (.txt or .csv)")
    cluster.add_argument(
        "-s",
        type=str,
        help="similarity algorithm",
        default="leven",
        metavar="[leven, demerau]",
    )
    cluster.add_argument(
        "-d", type=float, help="damping factor", default=0.9, metavar="[0.5 - 1.0]"
    )
    competition = subparsers.add_parser(
        name="competition",
        formatter_class=rawdescription,
        description=competition_doc,
        help="find competing domains",
    )
    competition.add_argument("kwfile", type=filetype, help="keyword file (.txt or .csv)")
    competition.add_argument("-l", type=str, help="location", default="Sweden")
    kwlist = subparsers.add_parser(
        name="kwlist",
        formatter_class=rawdescription,
        description=kwlist_doc,
        help="create a keyword list",
    )
    kwlist.add_argument("kwfile", type=filetype, help="keywords file (.txt or .csv)")
    kwlist.add_argument("-l", type=str, help="location", default="Sweden")
    kwlist.add_argument("-c", type=int, help="cutoff point", default=50)
    urlmap = subparsers.add_parser(
        name="urlmap",
        formatter_class=rawdescription,
        description=urlmap_doc,
        help="map queries to pages",
    )
    urlmap.add_argument("domain", type=str, help="domain to map")
    urlmap.add_argument("-d", type=str, help="semrush database", default="SE")
    urlmap.add_argument("-l", type=int, help="output rows", default=30)
    urlmap.add_argument("-f", type=filetype, help="keywords (.txt or .csv)")

    onpage = subparsers.add_parser(
        name="onpage",
        formatter_class=rawdescription,
        description=onpage_doc,
        help="on page optimization",
    )

    onpage.add_argument("url", type=str, help="url to optimize")
    onpage.add_argument("term", type=str, help="main search term to optimize")
    onpage.add_argument("-s", type=str, nargs="*", help="secondary search terms")
    onpage.add_argument("-l", type=str, help="database location", default="Sweden")

    return parser.parse_args()


def main():
    arguments = get_arguments()
    uid = str(uuid.uuid4())
    if arguments.command == "cluster":
        keywords = arguments.kwfile.read().splitlines()
        distance = arguments.s
        damping = arguments.d
        fpath = pathlib.Path(f"~/Desktop/cluster_{uid}.csv").expanduser()
        cluster_keywords(keywords, distance, damping, fpath)
    if arguments.command == "competition":
        keywords = arguments.kwfile.read().splitlines()
        location = arguments.l.title()
        fpath = pathlib.Path(f"~/Desktop/competition_{uid}.txt").expanduser()
        enumerate_competition(keywords, location, fpath)
    if arguments.command == "kwlist":
        keywords = arguments.kwfile.read().splitlines()
        location = arguments.l
        cutoff = arguments.c
        fpath = pathlib.Path(f"~/Desktop/kwlist_{uid}.csv").expanduser()
        get_kwlist(keywords, location, cutoff, fpath)
    if arguments.command == "urlmap":
        domain = arguments.domain
        database = arguments.d
        limit = arguments.l
        upload = arguments.f.read().splitlines()
        fpath = pathlib.Path(f"~/Desktop/urlmap_{uid}.csv").expanduser()
        map_domain(domain, database, limit, upload, fpath)

    if arguments.command == "onpage":
        url = arguments.url
        term = arguments.term
        secondary = arguments.s
        location = arguments.l
        fpath = pathlib.Path(f"~/Desktop/onpage_{uid}.txt").expanduser()
        pfetch(url, term, secondary, location, fpath)

    print(f"complete ~ find your output @ {fpath}")


if __name__ == "__main__":
    main()
