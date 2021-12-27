#!/usr/bin/env python
import argparse
import git
import yaml
from pathlib import Path
import sys
from typing import List, Optional, Sequence


class IgnoreItem:
    def __init__(self, file: str, line: str = ""):
        self.filename = Path(file)
        # convert the line numbers to a list
        if not str(line):  # empty string
            self.linenum = []
        else:
            self.linenum = [int(item) for item in str(line).split(",")]
        self._wholeFile = bool(len(self.linenum) == 0)

    def ignoreWholeFile(self, filename: Path) -> bool:
        return self._wholeFile and self.filename == filename

    def ignoreLine(self, filename: Path, linenum: int) -> bool:
        return self.filename == filename and linenum in self.linenum


class Rule:
    def __init__(self, pattern, message, ignore=[]):
        self.pattern = pattern
        self.message = message
        self._ignore = [IgnoreItem(**kwargs) for kwargs in ignore]

    def ignoreLine(self, filename: Path, linenum: int) -> bool:
        for item in self._ignore:
            if item.ignoreLine(filename, linenum):
                return True
        return False

    def ignoreWholeFile(self, filename: Path) -> bool:
        for item in self._ignore:
            if item.ignoreWholeFile(filename):
                return True
        return False

    def match(self, line: str):
        return self.pattern in line


def _get_config_file() -> Path:
    """Returns the path to the configuration file in the target repository.
    This will throw an exception if the configuration is 0 bytes or missing"""
    repo_root = git.Repo("", search_parent_directories=True)
    root_dir = Path(repo_root.working_tree_dir)
    config_file = root_dir / ".buildingcodes.yaml"
    if not config_file.exists():
        raise RuntimeError(f'Failed to find configuration file "{config_file}"')
    if config_file.stat().st_size <= 0:
        raise RuntimeError(f'Configuration file "{config_file}" 0 bytes in size')

    return config_file


def _create_rules() -> List[Rule]:
    # get the configuration file
    config_file = _get_config_file()

    # convert configuration into a dict
    with open(config_file, "r") as file:
        configuration = yaml.safe_load(file)
    if not configuration:
        raise RuntimeError(f'Empty configuration file "{config_file}"')

    # convert configuration into rules
    rules = [Rule(**rule) for rule in configuration]
    return rules


def _check_file(filepath: Path, rules: List[Rule]) -> int:
    # which rules should be used
    rule_indices = []
    for index, rule in enumerate(rules):
        if not rule.ignoreWholeFile(filepath):
            rule_indices.append(index)

    errors = 0
    with open(filepath.resolve(strict=True), "r") as handle:
        for linenum, line in enumerate(handle.readlines()):
            for rule_index in rule_indices:
                rule = rules[rule_index]
                matches = rule.match(line)
                if rule.ignoreLine(filepath, linenum):
                    # make sure that there is a match to suppress
                    if not matches:
                        print(f"Unmatched suppression: {rule.pattern} in {filepath} line {linenum}")
                        errors += 1
                elif matches:
                    print(f"{filepath}:{linenum}: {rule.message}")
                    print(f"{linenum:4} | {line[:-1]}")  # trim off end-of-line
                    errors += 1
    return errors


def main(argv: Optional[Sequence[str]] = None) -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("filenames", nargs="*", help="Filenames to check")
    args = parser.parse_args(argv)

    rules = _create_rules()

    errors: int = 0  # number of errors
    for filename in args.filenames:
        errors += _check_file(Path(filename), rules)

    if errors > 0:
        print(f"Found {errors} errors")
    return errors


if __name__ == "__main__":
    # skip the name of the script
    sys.exit(main(sys.argv[1:]) > 0)
