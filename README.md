# upd

A small Windows update checker for package managers. By default it only **lists** what is outdated and never updates anything unless you ask.


## Why upd?

Tools like topgrade or UniGetUI update things for you. upd takes the opposite approach: it shows you what is outdated first, and you decide what to update.

## List of supported managers

- Winget
- Scoop
- Pip
- Chocolatey (Experimental)

## Requirements

- Windows
- Python 3

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

- `-w` | winget
- `-s` | scoop 
- `-p` | pip
- `-c` | chocolatey

## Known issues

- If a manager fails while listing updates, the error is printed but upd still exits with code 0.

## Future

- Working on adding much more managers 

## License

MIT