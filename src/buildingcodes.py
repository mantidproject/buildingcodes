#!/usr/bin/env python
import argparse
from pathlib import Path
import sys
from typing import List, Optional, Sequence, Iterable

class Rule():
    def __init__(self):
      pass




def _check_file(filepath: Path):
    errors = []
    with open(filepath.resolve(strict=True), 'r') as handle:
        for linenum, line in enumerate(handle.readlines()):
            if 'Poco::Path' in line:
                errors.append((filepath, linenum, line.strip()))
            if 'Poco::File' in line:
                errors.append((filepath, linenum, line.strip()))
    return errors


def main(argv: Optional[Sequence[str]] = None) -> int:
    print('hi there')
    parser = argparse.ArgumentParser()
    parser.add_argument('filenames', nargs='*', help='Filenames to check')
    args = parser.parse_args(argv)

    errors = []
    for filename in args.filenames:
        filepath = Path(filename)
        error = _check_file(filepath)
        if error:
            errors.append(error)

    for error in errors:
        filename, linenum, error = error[0]  # TODO this is stupid
        print(f'{str(filename)}#{linenum}: {error}')
    return len(errors)



if __name__ == '__main__':
    sys.exit(main(sys.argv))
