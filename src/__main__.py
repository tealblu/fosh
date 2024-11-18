from argparse import ArgumentParser
from os import remove
from src import PALETTE, DEFAULT_NUM_NEIGHBORS, DEFAULT_VIEW_DIST
from src import Universe, Canvas, Boid


if __name__ == "__main__":
    # setup args
    parser = ArgumentParser()

    # basic
    parser.add_argument("-n",
                        dest="n",
                        type=int,
                        default=60,
                        help="the number of boids in the simulation")
    parser.add_argument("--fps",
                        type=float,
                        default=30.0,
                        help="the (maximum) framerate")
    parser.add_argument("--res",
                        type=str,
                        default="1920x1080",
                        help="the resolution")
    parser.add_argument("--highlight",
                        action="store_true",
                        help="highlight a single boid")
    parser.add_argument("--preview-only",
                        dest="preview_only",
                        action="store_true",
                        help="dont save the video, just show the preview")

    # weights
    parser.add_argument("-c", "--cohesion",
                        dest="cohes",
                        type=float,
                        default=1.0,
                        help="the weight of the cohesion rule")
    parser.add_argument("-a", "--alignment",
                        dest="align",
                        type=float,
                        default=1.0,
                        help="the weight of the alignment rule")
    parser.add_argument("-s", "--seperation",
                        dest="sep",
                        type=float,
                        default=1.0,
                        help="the weight of the seperation rule")

    # behaviour near edges
    parser.add_argument("-e", "--edge-behaviour",
                        dest="edge_behaviour",
                        type=str,
                        choices={"avoid", "wrap"},
                        default="avoid",
                        help="the behaviour of the boids near edges, either avoid them or just wrap around to the other side")

    # what method to use to decide which boids are close ('nearby')
    group = parser.add_mutually_exclusive_group()
    group.add_argument("--dist",
                       nargs="?",
                       type=float,
                       const=DEFAULT_VIEW_DIST,
                       help=f"all boids which are at most DIST units away from the current boid can be seen (defaults to {DEFAULT_VIEW_DIST})")
    group.add_argument("--count",
                       dest="num_neighbors",
                       nargs="?",
                       type=int,
                       const=DEFAULT_NUM_NEIGHBORS,
                       help=f"the COUNT closest boids are seen by the current boid (defaults to {DEFAULT_NUM_NEIGHBORS})")
    
    args = parser.parse_args()

    # run simulation
    with Canvas(args.res.split("x"), args.fps) as canvas:
        u = Universe(canvas,
                     edge_behaviour=args.edge_behaviour,
                     nearby_method="dist" if args.num_neighbors is None else "count",
                     view_dist=args.dist or DEFAULT_VIEW_DIST,
                     num_neighbors=args.num_neighbors or DEFAULT_NUM_NEIGHBORS,
                     sep=args.sep,
                     align=args.align,
                     cohes=args.cohes)

        if args.highlight:
            u.add_boid(color=PALETTE["highlight"], pos=(0, 0))
            args.n -= 1

        u.populate(args.n)
        u.loop()
        
    # delete file if wanted
    if args.preview_only or input("Save video? (Y/n) ").lower() == "n":
        remove(canvas.filename)
