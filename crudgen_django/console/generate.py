import argparse
from crudgen_django.services import SimpleRestService
import json

parser = argparse.ArgumentParser(description="command line interface for easy-rest")

parser.add_argument('-s', '--source', type=str, help='path to source model')
parser.add_argument('-d', '--destination', type=str, help='destination path to generate source code')

args = parser.parse_args()


def main():
    with open(args.source) as f:
        service_dict = json.load(f)
    service = SimpleRestService.from_dict(service_dict)
    service.transform(args.destination)
