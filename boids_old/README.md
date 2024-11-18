# foshs

Groups of bird-like agents, behaving like a flock. See https://youtu.be/bqtqltqcQhw and https://team.inria.fr/imagine/files/2014/10/flocks-hers-and-schools.pdf.

![a video of foshs moving](./out/examples/square.webm)

## Setup

Just clone this repo, create a venv, install the packages and run it.

> _Note: You need python>=3.8, as this project uses the [walrus operator](https://docs.python.org/3/whatsnew/3.8.html#assignment-expressions)._

On linux:

    git clone https://gitlab.com/chrismit3s/foshs
    cd foshs
    python3.8 -m venv venv
    source ./venv/bin/activate
    python -m pip install -r requirements.txt

On windows (with [py launcher](https://docs.python.org/3/using/windows.html) installed):

    git clone https://gitlab.com/chrismit3s/foshs
    cd foshs
    py -3.8 -m venv venv
    .\venv\scripts\activate.bat
    python -m pip install -r requirements.txt

## Usage

Just run the `src` module:

    python -m src [-h] [-n N] [--fps FPS] [--res RES] [--highlight] [--preview-only] [-c COHES] [-a ALIGN] [-s SEP] [-e {wrap,avoid}] [--dist [DIST] | --count [NUM_NEIGHBORS]]

| Argument             | Shorthand | Explanation |
|:---------------------|:----------|:------------|
| --help               | -h        | show help message and exit |
|                      | -n        | the number of foshs in the simulation |
| --fps                |           | the (maximum) framerate |
| --res                |           | the resolution |
| --highlight          |           | highlight a single fosh |
| --preview-only       |           | dont save the video, just show the preview |
| --cohesion           | -c        | the weight of the cohesion rule |
| --alignment          | -a        | the weight of the alignment rule |
| --seperation         | -s        | the weight of the seperation rule |
| --edge-behaviour     | -e        | the behaviour of the foshs near edges, either avoid them or just wrap around to the other side (one of {avoid, wrap}) |
| --dist               |           | all foshs which are at most DIST units away from the current fosh can be seen (defaults to 80.0) |
| --count              |           | the COUNT closest foshs are seen by the current fosh (defaults to 5, modelled after [this](https://www.pnas.org/content/105/4/1232)) |

## License

This project is licensed under the MIT License - see the LICENSE.md file for details
