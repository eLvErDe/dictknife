# -*- coding:utf-8 -*-
import logging
import sys
try:
    import click
except ImportError as e:
    print(e, file=sys.stderr)
    print("please install via `pip install dictknife[command]`", file=sys.stderr)
    sys.exit(1)
from dictknife import loading
logger = logging.getLogger(__name__)
loglevels = list(logging._nameToLevel.keys())


@click.group(context_settings={'help_option_names': ['-h', '--help']})
@click.option("--log", help="logging level", default="INFO", type=click.Choice(loglevels))
@click.pass_context
def main(ctx, log):
    logging.basicConfig(level=getattr(logging, log))
    loading.setup()


@main.command(help="tojsonschema")
@click.argument("src", default=None, type=click.Path(exists=True))
@click.option("--dst", default=None, type=click.Path())
@click.option("--name", default="top")
def tojsonschema(src, dst, name):
    d = loading.loadfile(src)
    root = d["definitions"].pop(name)
    root["required"] = True
    root.update(d)
    loading.dumpfile(root, filename=dst)


@main.command(help="json2swagger")
@click.argument("src", default=None, type=click.Path(exists=True))
@click.option("--dst", default=None, type=click.Path())
@click.option("--name", default="top")
@click.option("--annotations", default=None, type=click.Path(exists=True))
@click.option("--emit", default="schema", type=click.Choice(["schema", "info"]))
@click.option("--with-minimap", is_flag=True)
def json2swagger(src, dst, name, annotations, emit, with_minimap):
    from prestring import Module
    from dictknife.swaggerknife.json2swagger import Detector, Emitter

    if annotations is not None:
        annotations = loading.loadfile(annotations)
    else:
        annotations = {}

    detector = Detector()
    emitter = Emitter(annotations)

    data = loading.loadfile(src)
    info = detector.detect(data, name)

    if emit == "info":
        loading.dumpfile(info, filename=dst)
    else:
        m = Module(indent="  ")
        m.stmt(name)
        emitter.emit(info, m)
        if with_minimap:
            print("# minimap ###")
            print("# *", end="")
            print("\n# ".join(str(m).split("\n")))
        loading.dumpfile(emitter.doc, filename=dst)


@main.command(help="flatten jsonschema sub definitions")
@click.argument("src", default=None, type=click.Path(exists=True))
@click.option("--dst", default=None, type=click.Path())
def flatten(src, dst):
    from dictknife.swaggerknife.flatten import flatten
    data = loading.loadfile(src)
    d = flatten(data)
    loading.dumpfile(d, dst)