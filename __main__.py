#! /usr/bin/env python
# -*- coding: utf-8 -*-
# pylint: disable=bad-continuation,line-too-long
"""Filter clumsy styling from testssl.sh v3 html output and make more accessible."""
import os
import sys

UPSTREAM_REL_URL = "UPSTREAM_REL_URL"
upstream_rel_url = os.getenv(UPSTREAM_REL_URL, "")
if not upstream_rel_url:
    raise RuntimeError(
        f"Set the navigation link relative upstream URL via environment variable {UPSTREAM_REL_URL}"
    )


def transformer(server, upstream, line_generator):
    """DRY."""
    from_to_complete = {
        "<title>testssl.sh</title>": (
            "<title>audit - tls - %s</title>"
            "<style>body {background-color: #333333; color: #dddddd;} a {color: cyan;}"
            ' .some-font {font-family: "ITC Franklin Gothic Std Bk Cd", Verdana, Arial, sans-serif;}</style>'
        )
        % (server,),
        "<pre>": (
            '<p class="some-font">... <a href="%s">back to index</a></p>\n' "<pre>"
        )
        % (upstream,),
    }

    from_to_partial = {
        'background-color:black;"': '"',
        "color:black;": '"',
        '"color:#cd0000;"': '"color:#cd0000;background-color:yellow;"',
        '"color:red;': '"color:red;background-color:white;',
    }

    for line in line_generator.readlines():
        incoming = line.rstrip()
        outgoing = from_to_complete.get(incoming, incoming)
        if incoming == outgoing:
            for token in from_to_partial:
                if token in incoming:
                    outgoing = incoming.replace(token, from_to_partial[token])
                    break
        yield outgoing


def main(argv=None):
    """Drive the filter."""
    argv = argv if argv else sys.argv[1:]
    if len(argv) != 1:
        print(
            "Provide a server name as single argument and the testssl.sh html report via stdin"
        )
        return 2

    server = argv[0].strip()

    for line in transformer(server, upstream_rel_url, sys.stdin):
        sys.stdout.write(f"{line}\n")

    return 0


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
