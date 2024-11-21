import sys
import argparse


def common_parser():
    parser = argparse.ArgumentParser(
        description="""
        Generate a triangulation file and the associated point cloud file
        out of the Blender (manually) defined model.
        """,
        formatter_class=argparse.ArgumentDefaultsHelpFormatter,
    )
    parser.add_argument(
        "-v", "--verbose", action="store_true", help="Toggle verbose printing"
    )
    parser.add_argument(
        "--subdivision",
        help="Number of Catmull subdivisions that should be applied:"
        " 1 for a bare triangulation, for 5 expect a 450M resulting file",
        default=1,
        type=int,
    )
    parser.add_argument(
        "--outputdir",
        help="Directory for resulting PLY files",
        default=".",
        type=str,
    )
    parser.add_argument(
        "--no-ply-export",
        help="Do not export to PLY files.",
        action="store_true",
    )
    parser.add_argument(
        "--no-obj-export",
        help="Do not export to OBJ files.",
        action="store_true",
    )
    parser.add_argument(
        "--fill_holes",
        help="Plug/fill surface boundaries/holes (topological change)",
        action="store_true",
    )
    return parser


def parse_arguments(parser):
    if "--" in sys.argv:
        # We probably are running this script in UI mode (that is with commands
        # like `blender --python this_script.py -- --subdivision 2`) and thanks
        # to this
        # https://blender.stackexchange.com/questions/6817/how-to-pass-command-line-arguments-to-a-blender-python-script
        # we know how to modify sys.argv in order to avoid interactions with
        # blender CLI arguments/options:
        argv = sys.argv[sys.argv.index("--") + 1 :]  # get all args after "--"
        args = parser.parse_args(argv)
        args.headless = False
    else:
        args = parser.parse_args()
        args.headless = True
    if args.verbose:
        parser.print_help()
        print("Parsed arguments: ")
        for arg in vars(args):
            print("   ", arg, ": ", getattr(args, arg))
    return args
