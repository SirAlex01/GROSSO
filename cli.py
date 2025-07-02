import argparse

# === Argument Parsing ===
def parseArgs():
    parser = argparse.ArgumentParser(
        description="Recursively collect readable or executable files from a directory."
    )
    parser.add_argument(
        '-p', '--path',
        type=str,
        #default="./simu3/mudarabah",
        required=True,
        help="Path to the root directory (default: ./simu3/sesame)"
    )

    parser.add_argument(
        '-ms', '--maxsize',
        type=int,
        default=30,
        help="Maximum file size in kilobytes (default: 30 KB)"
    )

    parser.add_argument(
        '-t', '--timeout',
        type=int,
        default=300,
        help="Maximum timeout for first model's response (default: 300 seconds)"
    )

    return parser.parse_args()
