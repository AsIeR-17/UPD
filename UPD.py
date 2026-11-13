import argparse
import subprocess
import shutil
import sys

hubo_error = False
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
        "executable": sys.executable,
        "list": ["python", "-m", "pip", "list", "--outdated"],
        "update_all": None,
        "update_one": ["python", "-m", "pip", "install", "-U", "{name}"],
        "check_installed": ["python", "-m", "pip", "show", "{name}"],
        "existencia": ["python", "-m", "pip", "--version"],
    },
}


def disponibilidad():
    disponibles = []
    for gestor in GESTORES:
        datos = GESTORES[gestor]
        if datos["existencia"] is None:
            if shutil.which(datos["executable"]) is not None:
                disponibles.append(gestor)
        else:
            comando = [datos["executable"]] + datos["existencia"][1:]
            comprobacion = subprocess.run(comando, capture_output=True)
            if comprobacion.returncode == 0:
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
        if resultado.returncode != 0:
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
                subprocess.run([ruta] + comando[1:])
    else:
        for nombre in nombres:
            if datos["check_installed"] is None:
                comando = sustituir(datos["update_one"], nombre)
                subprocess.run([ruta] + comando[1:])
            else:
                comando = sustituir(datos["check_installed"], nombre)
                comprobacion = subprocess.run([ruta] + comando[1:], capture_output=True)
                if comprobacion.returncode == 0:
                    comando = sustituir(datos["update_one"], nombre)
                    subprocess.run([ruta] + comando[1:])
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
parser.add_argument("-a", "--all", action="store_true", help="All managers")
args = parser.parse_args()

disponibles = disponibilidad()

if not disponibles:
    print("No package managers were found", file=sys.stderr)
    sys.exit(1)

if args.all:
    if "winget" in disponibles:
        print("===== WINGET =====")
        ejecutar("winget", [])
        print(" ")
    if "scoop" in disponibles:
        print("===== SCOOP =====")
        ejecutar("scoop", [])
        print(" ")
    if "pip" in disponibles:
        print("====== PIP ======")
        ejecutar("pip", [])
elif args.w is None and args.s is None and args.p is None:
    if "winget" in disponibles:
        print("===== WINGET =====")
        ejecutar("winget", None)
        print(" ")
    if "scoop" in disponibles:
        print("===== SCOOP =====")
        ejecutar("scoop", None)
        print(" ")
    if "pip" in disponibles:
        print("====== PIP ======")
        ejecutar("pip", None)
else:
    if args.w is not None:
        if "winget" in disponibles:
            ejecutar("winget", args.w)
        else:
            print("Winget not found in PATH", file=sys.stderr)
            hubo_error = True
    if args.s is not None:
        if "scoop" in disponibles:
            ejecutar("scoop", args.s)
        else:
            print("Scoop not found in PATH", file=sys.stderr)
            hubo_error = True
    if args.p is not None:
        if "pip" in disponibles:
            ejecutar("pip", args.p)
        else:
            print("Pip is not available for this Python", file=sys.stderr)
            hubo_error = True

if hubo_error == True:
    sys.exit(1)
