"""
Command line interface.

Command line interface for the application for use on the terminal.
"""

import argparse
import pathlib
import sys
import uuid

from src.cluster import __doc__ as cluster_doc
from src.cluster import cluster_keywords
from src.competition import __doc__ as comp_doc
from src.competition import enumerate_competition
from src.formatting import fprint
from src.kwlist import __doc__ as kwlist_doc
from src.kwlist import get_kwlist
from src.onpage import __doc__ as onpage_doc
from src.onpage import compile_onpage, get_page_metadata
from src.urlmap import __doc__ as urlmap_doc
from src.urlmap import map_domain

semver = "v0.0.4"


def get_arguments() -> argparse.Namespace:

    rfile = argparse.FileType("r", encoding="utf-8")
    # defaulthelp = argparse.ArgumentDefaultsHelpFormatter
    rawdesc = argparse.RawDescriptionHelpFormatter

    parser = argparse.ArgumentParser(description="SEO Operations.")
    parser.add_argument("--version", action="version", version=semver)
    subparsers = parser.add_subparsers(help="commands", dest="command")

    pagemeta_doc = "Fetch page metadata for a URL."
    pagemeta = subparsers.add_parser("pagemeta", formatter_class=rawdesc, description=pagemeta_doc, help="fetch page metadata")
    pagemeta.add_argument("url", type=str, help="url to inspect")

    cluster = subparsers.add_parser(name="cluster", formatter_class=rawdesc, description=cluster_doc, help="cluster search terms")
    cluster.add_argument("file", type=rfile, help="keywords file (.txt or .csv) - should not contain header row")
    cluster.add_argument("--damping", type=float, metavar="N", default=0.9, help="damping factor (default = 0.9)")

    competition = subparsers.add_parser(name="competition", formatter_class=rawdesc, description=comp_doc, help="find competing domains")
    competition.add_argument("file", type=rfile, help="keyword file (.txt or .csv) - should not contain header row")
    competition.add_argument("--location", type=str, metavar="COUNTRY", default="sweden", help="location (default = sweden)")

    kwlist = subparsers.add_parser(name="kwlist", formatter_class=rawdesc, description=kwlist_doc, help="create a keyword list")
    kwlist.add_argument("file", type=rfile, metavar="PATH", help="keywords file (.txt or .csv) - should not contain header row")
    kwlist.add_argument("--location", type=str, metavar="COUNTRY", default="sweden", help="location (default = sweden)")
    kwlist.add_argument("--cutoff", type=int, metavar="N", default=50, help="cutoff point (default = 50)")
    kwlist.add_argument("--remove", type=str, metavar="TERM", nargs="*", help="discard patterns")

    urlmap = subparsers.add_parser(name="urlmap", formatter_class=rawdesc, description=urlmap_doc, help="map queries to pages")
    urlmap.add_argument("domain", type=str, help="domain to map")
    urlmap.add_argument("--remove", type=str, metavar="TERM", nargs="*", help="discard patterns ('/subfolder/' or 'term')")
    urlmap.add_argument("--location", type=str, metavar="CODE", default="se", help="semrush database country code (default = se)")
    urlmap.add_argument("--rows", type=int, metavar="N", default=30, help="output rows (default = 30)")
    urlmap.add_argument("--file", type=rfile, metavar="FILEPATH", help="keyword file (.txt or .csv) - should not contain header row")
    urlmap.add_argument("--no-semrush", action="store_false", help="remove semrush data from output (default = false)")

    onpage = subparsers.add_parser(name="onpage", formatter_class=rawdesc, description=onpage_doc, help="on page optimization")
    onpage.add_argument("url", type=str, help="url to optimize")
    onpage.add_argument("term", type=str, help="main search term to optimize")
    onpage.add_argument("--terms", type=str, metavar="TERM", nargs="*", help="secondary search terms")
    onpage.add_argument("--location", type=str, metavar="COUNTY", default="sweden", help="location (default = sweden)")

    return parser.parse_args()


def main() -> None:
    arguments = get_arguments()
    uid = str(uuid.uuid4())
    if arguments.command == "cluster":
        keywords = arguments.file.read().splitlines()
        damping = arguments.damping
        fpath = pathlib.Path(f"~/Desktop/cluster_{uid}.csv").expanduser()
        cluster_keywords(keywords, damping, fpath)
    if arguments.command == "competition":
        keywords = arguments.file.read().splitlines()
        location = arguments.location.title()
        fpath = pathlib.Path(f"~/Desktop/competition_{uid}.csv").expanduser()
        enumerate_competition(keywords, location, fpath)
    if arguments.command == "kwlist":
        keywords = arguments.file.read().splitlines()
        location = arguments.location
        cutoff = arguments.cutoff
        exclusions = arguments.remove
        fpath = pathlib.Path(f"~/Desktop/kwlist_{uid}.csv").expanduser()
        get_kwlist(keywords, location, cutoff, fpath, exclusions)
    if arguments.command == "urlmap":
        domain = arguments.domain
        database = arguments.location
        rows = arguments.rows
        keep_semrush = arguments.no_semrush
        exclusions = arguments.remove
        upload = arguments.file.read().splitlines() if arguments.file else None
        fpath = pathlib.Path(f"~/Desktop/urlmap_{uid}.csv").expanduser()
        if keep_semrush is False and not upload:
            fprint("error", "the --no-semrush option requires a --file FILEPATH")
            sys.exit()
        map_domain(domain, database, rows, upload, fpath, keep_semrush, exclusions)
    if arguments.command == "onpage":
        url = arguments.url
        term = arguments.term
        terms = arguments.terms
        location = arguments.location
        # print("This operation is still a work in progress ...")
        # TODO: onpage check how to read the upload arguments to update the file
        # upload = arguments.file.read()
        # upload = pathlib.Path(arguments.file) if arguments.file else None
        # fpath = pathlib.Path(f"~/Desktop/onpage_{uid}.txt").expanduser()
        fpath = pathlib.Path(f"~/Desktop/onpage_{uid}.docx").expanduser()
        compile_onpage(url, term, terms, location, fpath)
        # compile_onpage(url, term, terms, location, fpath)
        # create_brief(url, location, fpath)
    if arguments.command == "pagemeta":
        url = arguments.url
        page_data = get_page_metadata(url)
        print("\n")
        for k, v in page_data.items():
            print(f"\u001b[7m\033[4m\033[1m{k}\033[0m\n")
            if isinstance(v, int):
                print(f"{v}")
            else:
                for i in v:
                    print(f"{i}")
            print("\n")


if __name__ == "__main__":
    main()
