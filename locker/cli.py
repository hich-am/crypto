"""Lanceur CLI indépendant pour Locker."""

from __future__ import annotations

import argparse
import importlib
import sys

from .catalog import (
    COURSE_ALIASES,
    MODULE_CATALOG,
    THEME_LABELS,
    THEME_SEQUENCE,
    iter_modules_for_theme,
    resolve_target,
)

_USE_COLOR = sys.stdout.isatty()


def _c(code: str, text: str) -> str:
    if not _USE_COLOR:
        return text
    return f"\033[{code}m{text}\033[0m"


def _brand(text: str) -> str:
    return _c("1;97;48;5;25", text)


def _label(text: str) -> str:
    return _c("1;38;5;25", text)


def _accent(text: str) -> str:
    return _c("38;5;75", text)


def _muted(text: str) -> str:
    return _c("38;5;244", text)


def _subtitle(text: str) -> str:
    return _c("38;5;245", text)


def _error(text: str) -> str:
    return _c("38;5;160", text)


def _term_width(default: int = 78) -> int:
    try:
        import shutil

        return max(40, min(shutil.get_terminal_size().columns, 100))
    except Exception:
        return default


def _divider() -> str:
    return _muted("-" * _term_width())


def render_catalog_menu() -> None:
    print()
    print(_brand(" Locker ".ljust(_term_width())))
    print(_subtitle("  Laboratoire de cryptographie indépendant - catalogue et valeurs personnalisées"))
    print(_divider())
    for theme in THEME_SEQUENCE:
        print()
        print(_label(f"  {THEME_LABELS[theme]}"))
        for slug, _module_path, module_label in iter_modules_for_theme(theme):
            ref = f"{theme}.{slug}"
            print(f"    {_accent(ref.ljust(28))} {module_label}")
    print()
    print(_divider())
    print(f"  {_accent('list')}   {_muted('afficher le catalogue')}")
    print(f"  {_accent('all')}    {_muted('lancer tous les scénarios')}")
    print(f"  {_accent('q')}      {_muted('quitter')}")
    print()


def run_demo(module_path: str) -> None:
    print()
    print(_label(f"=== {module_path} ==="))
    print(_subtitle("Scénario prédéfini"))
    print(_divider())
    try:
        module = importlib.import_module(module_path)
        if not hasattr(module, "demo"):
            print(_error(f"  {module_path} : pas de fonction demo()"))
            return
        module.demo()
    except ImportError as exc:
        print(_error(f"  Erreur d'import : {exc}"))
        print(_subtitle("  pip install -r requirements.txt"))
    except Exception as exc:
        print(_error(f"  Erreur : {type(exc).__name__}: {exc}"))


def run_all_demos() -> None:
    for _key, (module_path, _label) in MODULE_CATALOG.items():
        run_demo(module_path)


def run_custom_values(module_path: str, label: str) -> None:
    try:
        from gui_specs import BYTES_HEX, BYTES_UTF8, CHOICE, INT, MULTILINE, SPECS, TEXT
    except ImportError as exc:
        print(_error(f"  Error : gui_specs module unavailable ({exc})"))
        return

    spec = SPECS.get(module_path)
    if spec is None:
        print()
        print(_label(label))
        print(_subtitle("Aucun formulaire personnalisé pour ce module.\nChoisissez 's' pour lancer le scénario démo."))
        return

    print()
    print(_label(label))
    print(_subtitle("Fournissez les valeurs ci-dessous. Appuyez sur Entrée pour garder la valeur par défaut."))
    print(_divider())
    print(_label("PARAMÈTRES"))

    values: dict = {}
    for field in spec.champs:
        note = f" {_muted('- ' + field.note)}" if field.note else ""
        default_display = field.defaut
        if field.type == CHOICE and field.options:
            note = f" {_muted('[' + '/'.join(field.options) + ']')}" if not note else note
        prompt = f"  {_accent(field.label)}{note}\n    [{_muted(str(default_display))}] > "
        try:
            raw = input(prompt)
        except EOFError:
            print()
            return

        if raw == "" and field.defaut != "":
            raw = str(field.defaut)

        try:
            if field.type == TEXT:
                values[field.cle] = raw
            elif field.type == MULTILINE:
                values[field.cle] = raw
            elif field.type == BYTES_UTF8:
                values[field.cle] = raw.encode("utf-8")
            elif field.type == INT:
                values[field.cle] = int(raw or 0)
            elif field.type == BYTES_HEX:
                text = raw.strip().replace(" ", "")
                values[field.cle] = bytes.fromhex(text) if text else b""
            elif field.type == CHOICE:
                if field.options and raw not in field.options:
                    raw = field.options[0]
                values[field.cle] = raw
            else:
                values[field.cle] = raw
        except ValueError as exc:
            print(_error(f"  [ERREUR DE SAISIE] {field.label}: {exc}"))
            return

    print()
    print(_label("RÉSULTAT"))
    print(_divider())
    try:
        result = spec.runner(values)
    except Exception as exc:
        print(_error(f"  [ERREUR D'EXÉCUTION] {type(exc).__name__}: {exc}"))
        return
    print(result)


def open_module_entry(module_path: str, label: str) -> None:
    print()
    print(_label(label))
    print(_subtitle("Comment voulez-vous ouvrir ce module ?"))
    print(f"  {_accent('s')}   Scénario prédéfini")
    print(f"  {_accent('i')}   Tester avec mes valeurs")
    print(f"  {_accent('q')}   Retour au menu")
    try:
        choice = input("\n  > ").strip().lower()
    except EOFError:
        print()
        return
    if choice in ("", "s", "scenario"):
        run_demo(module_path)
    elif choice in ("i", "input", "values"):
        run_custom_values(module_path, label)
    elif choice in ("q", "quit", "back"):
        return
    else:
        print(_error(f"  Inconnu : {choice}"))


def launch_target(token):
    target = resolve_target(token)
    if target is None:
        print(_error(f"  Inconnu : {token}"))
        return
    module_path, label = target
    if not sys.stdin.isatty():
        run_demo(module_path)
        return
    open_module_entry(module_path, label)


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(prog="Locker", description="Lanceur de laboratoire de cryptographie indépendant")
    parser.add_argument("target", nargs="?", help="alias de module comme 2.3 ou thème.slug comme symmetric.aes")
    parser.add_argument("--all", action="store_true", help="lancer tous les démonstrations")
    parser.add_argument("--list", action="store_true", help="afficher le catalogue des modules")
    parser.add_argument("--theme", choices=THEME_SEQUENCE, help="afficher le catalogue d'un seul thème")
    parser.add_argument("--no-color", action="store_true", help="désactiver les couleurs ANSI")
    return parser


def run_cli(argv: list[str] | None = None) -> None:
    global _USE_COLOR
    parser = build_parser()
    args = parser.parse_args(argv)
    if args.no_color:
        _USE_COLOR = False

    if args.list:
        render_catalog_menu()
        return

    if args.theme:
        print()
        print(_brand(" Locker ".ljust(_term_width())))
        print(_subtitle(f"  {THEME_LABELS[args.theme]}"))
        print(_divider())
        for slug, _module_path, module_label in iter_modules_for_theme(args.theme):
            print(f"  {_accent(f'{args.theme}.{slug}'.ljust(28))} {module_label}")
        return

    if args.all:
        run_all_demos()
        return

    if args.target:
        target = args.target.strip().lower()
        if target in ("-h", "--help", "help"):
            parser.print_help()
            return
        target_info = resolve_target(target)
        if target_info is None:
            print(_error(f"  Inconnu : {target}"))
            return
        run_demo(target_info[0])
        return

    if not sys.stdin.isatty():
        render_catalog_menu()
        return

    while True:
        render_catalog_menu()
        try:
            choice = input(f"  {_accent('>')} ").strip().lower()
        except EOFError:
            print()
            break
        if choice in ("q", "quit", "exit"):
            print(_subtitle("  Goodbye."))
            break
        if choice == "all":
            run_all_demos()
        elif choice:
            launch_target(choice)


def main() -> None:
    run_cli()


if __name__ == "__main__":
    main()
