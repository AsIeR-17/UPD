# upd

A small Windows update checker for package managers. By default it only **lists** what is outdated and never updates anything unless you ask.

Supported managers: winget, scoop and pip.

## Why upd?

Tools like topgrade or UniGetUI update things for you. upd takes the opposite approach: it shows you what is outdated first, and you decide what to update.

## Requirements

- Windows
- Python 3
- At least one of: winget, scoop, pip

## Installation

1. Clone or download this repository.
2. Add the folder to your PATH, so the `upd` command works anywhere.

## Usage

```
upd                 List updates for all available managers
upd -w              Update all winget packages
upd -w Git.Git      Update one winget package
upd -a              Update all managers
```

Use `-s` for scoop and `-p` for pip. Pip has no "update all", so it needs package names.

## Known issues

- If a manager fails while listing updates, the error is printed but upd still exits with code 0.

## Future

- Working on adding much more managers 

## License

MIT