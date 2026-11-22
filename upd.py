import argparse
import subprocess
import shutil
import sys
import os

GESTORES = {
    "winget": {
        "executable": "winget",
        "list": ["winget", "update"],
        "update_all": [["winget", "upgrade", "--all"]],
        "update_one": ["winget", "upgrade", "--id", "{name}", "--exact"],
        "check_installed": None,
        "existencia": None,
    },
    "scoop": {
        "executable": "scoop",
        "list": ["scoop", "status"],
        "update_all": [["scoop", "update"], ["scoop", "update", "*"]],
        "update_one": ["scoop", "update", "{name}"],
        "check_installed": None,
        "existencia": None,
    },
    "pip": {
        "executable": shutil.which("python" if sys.platform == "win32" else "python3") or "python",
        "list": ["python", "-m", "pip", "list", "--outdated"],
        "update_all": None,
        "update_one": ["python", "-m", "pip", "install", "-U", "{name}"],
        "check_installed": ["python", "-m", "pip", "show", "{name}"],
        "existencia": ["python", "-m", "pip", "--version"],
    },
    "choco": {
        "executable": "choco",
        "list": ["choco", "outdated"],
        "update_all": [["choco", "upgrade", "all", "-y"]],
        "update_one": ["choco", "upgrade", "{name}", "-y", "--fail-on-not-installed"],
        "check_installed": None,
        "existencia": None,
    },
    "npm": {
        "executable": "npm",
        "list": ["npm", "outdated", "-g"],
        "update_all": [["npm", "update", "-g"]],
        "update_one": ["npm", "update", "-g", "{name}"],
        "check_installed": None,
        "existencia": None,
        "ok_codes": [0, 1],
    },
    "cargo": {
        "executable": "cargo",
        "list": ["cargo", "install-update", "-l"],
        "update_all": [["cargo", "install-update", "-a"]],
        "update_one": ["cargo", "install-update", "{name}"],
        "check_installed": None,
        "existencia": ["cargo", "install-update", "--version"],
        "hint": "cargo-update is required: cargo install cargo-update",
    },
}

def construir(datos, comando, ruta):
    comando = [ruta] + comando[1:]
    if not datos.get("sudo") or sys.platform == "win32":
        return comando
    if os.geteuid() != 0:
        comando = ["sudo"] + comando
    return comando

def disponibilidad():
    disponibles = []
    for gestor, datos in GESTORES.items():
        if shutil.which(datos["executable"]) is None:
            continue
        if datos["existencia"] is not None:
            comando = [datos["executable"]] + datos["existencia"][1:]
            if subprocess.run(comando, capture_output=True).returncode != 0:
                continue
        disponibles.append(gestor)
    return disponibles


def sustituir(comando, nombre):
    resultado = []
    for palabra in comando:
        if palabra == "{name}":
            resultado.append(nombre)
        else:
            resultado.append(palabra)
    return resultado


def ejecutar(gestor, nombres):
    datos = GESTORES[gestor]
    ruta = shutil.which(datos["executable"])
    if nombres is None:
        resultado = subprocess.run(
            [ruta] + datos["list"][1:], capture_output=True, text=True, encoding="utf-8"
        )
        if resultado.returncode not in datos.get("ok_codes", [0]):
            print(
                f"{gestor}: failed (exit code {resultado.returncode})", file=sys.stderr
            )
            print(resultado.stderr, file=sys.stderr)
        elif resultado.stdout.strip() == "":
            print(f"{gestor}: everything is up to date")
        else:
            print(resultado.stdout, end="")
    elif nombres == []:
        if datos["update_all"] is None:
            print(f"{gestor} has no update all")
        else:
            for comando in datos["update_all"]:
                subprocess.run(construir(datos, comando, ruta))
    else:
        for nombre in nombres:
            if datos["check_installed"] is None:
                comando = sustituir(datos["update_one"], nombre)
                subprocess.run(construir(datos, comando, ruta))
            else:
                comando = sustituir(datos["check_installed"], nombre)
                comprobacion = subprocess.run([ruta] + comando[1:], capture_output=True)
                if comprobacion.returncode == 0:
                    comando = sustituir(datos["update_one"], nombre)
                    subprocess.run(construir(datos, comando, ruta))
                else:
                    print(f"{nombre} is not installed")


parser = argparse.ArgumentParser(
    description="Manage package managers",
    formatter_class=lambda prog: argparse.RawDescriptionHelpFormatter(
        prog, max_help_position=30
    ),
    prog="upd",
    epilog="""\
    Examples:
    upd            Displays updates for all packages
    upd -w         Update all winget packages
    upd -w Git.Git Update a specific package

    ██╗   ██╗██████╗ ██████╗ 
    ██║   ██║██╔══██╗██╔══██╗
    ██║   ██║██████╔╝██║  ██║
    ██║   ██║██╔═══╝ ██║  ██║
    ╚██████╔╝██║     ██████╔╝
     ╚═════╝ ╚═╝     ╚═════╝ 
    """,
)
parser.add_argument(
    "-w",
    "--winget",
    dest="w",
    nargs="*",
    default=None,
    help="Winget packages",
    metavar="ID",
)
parser.add_argument(
    "-s",
    "--scoop",
    dest="s",
    nargs="*",
    default=None,
    help="Scoop packages",
    metavar="ID",
)
parser.add_argument(
    "-p", "--pip", dest="p", nargs="*", default=None, help="Pip packages", metavar="ID"
)
parser.add_argument(
    "-c",
    "--choco",
    dest="c",
    nargs="*",
    default=None,
    help="Chocolatey packages",
    metavar="ID",
)
parser.add_argument(
    "-n",
    "--npm",
    dest="n",
    nargs="*",
    default=None,
    help="npm global packages",
    metavar="ID",
)
parser.add_argument(
    "-r",
    "--cargo",
    dest="r",
    nargs="*",
    default=None,
    help="Cargo packages",
    metavar="ID",
)
parser.add_argument("-a", "--all", action="store_true", help="All managers")


def main():
    args = parser.parse_args()

    hubo_error = False

    disponibles = disponibilidad()

    RESET = "\033[0m"
    VERDE = "\033[32m"

    def color(texto, codigo):
        if not sys.stdout.isatty():
            return texto
        return f"{codigo}{texto}{RESET}"

    if not disponibles:
        print("No package managers were found", file=sys.stderr)
        sys.exit(1)

    banderas = {
        "winget": args.w,
        "scoop": args.s,
        "pip": args.p,
        "choco": args.c,
        "npm": args.n,
        "cargo": args.r,
    }

    if args.all:
        for gestor in disponibles:
            print(" ")
            print(color(f"===== {gestor.upper()} =====", VERDE))
            print(" ")
            ejecutar(gestor, [])
            print(" ")
    elif all(valor is None for valor in banderas.values()):
        for gestor in disponibles:
            print(" ")
            print(color(f"===== {gestor.upper()} =====", VERDE))
            print(" ")
            ejecutar(gestor, None)
            print(" ")
    else:
        for gestor, nombres in banderas.items():
            if nombres is not None:
                if gestor in disponibles:
                    ejecutar(gestor, nombres)
                else:
                    print(f"{gestor} not found", file=sys.stderr)
                    if "hint" in GESTORES[gestor]:
                        print(f"  hint: {GESTORES[gestor]['hint']}", file=sys.stderr)
                    hubo_error = True

    if hubo_error == True:
        sys.exit(1)


if __name__ == "__main__":
    main()
