<p align="center">
  <img src="assets/logo-dark.svg" alt="Logo de upd" width="450">
</p>

# UPD

Built for people who use varius package managers, this program unites all of them in one easy to use CLI tool.
By default calling it show you automatically every package manager you have and its outdates packages. Letting you update everything at your convenience


## Why upd?

Tools like topgrade or UniGetUI update things for you. 
UPD starts by showing you what's outdated by letting you choose in case you don't want to update something

## List of supported managers

- Winget
- Scoop
- Pip
- Chocolatey (Untested)
- Npm
- Cargo (Needs cargo-update to work)
- Apt (Untested)

## Requirements

- Python 3.10 or greater

## Instalation
```
pipx install git+https://github.com/AsIeR-17/UPD.git
```
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
- `-n` | npm
- `-r` | cargo
- `-t` | apt

## Known issues

- If a manager fails while listing updates, the error is printed but upd still exits with code 0.

## Future

- Working on adding much more managers 
- Preparing for adding Mac compatability
- Testing on Linux

## License

MIT