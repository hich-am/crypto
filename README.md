<p align="center">
  <h1 align="center">Crypto</h1>
  <p align="center">Un laboratoire de cryptographie de référence couvrant les chiffres classiques, les primitives asymétriques/symétriques, les fonctions de hachage, les signatures numériques et les applications de communication sécurisée — avec CLI et interface graphique de bureau.</p>
</p>

<p align="center">
  <a href="LICENSE"><img src="https://img.shields.io/badge/license-MIT-blue.svg" alt="License"></a>
  <img src="https://img.shields.io/badge/python-3.9+-3776AB.svg?logo=python&logoColor=white" alt="Python">
  <img src="https://img.shields.io/badge/tests-118%20passing-brightgreen.svg" alt="Tests">
  <img src="https://img.shields.io/badge/coverage-NIST%20%E2%9C%93%20RFC%20%E2%9C%93-success.svg" alt="Coverage">
  <img src="https://img.shields.io/badge/algorithms-25+-orange.svg" alt="Algorithms">
</p>


## Installation

```sh
# Cloner
cd crypto

# Virtualenv (recommandé)
python3 -m venv .venv
source .venv/bin/activate

# Dépendances
pip install -r requirements.txt

# Lancer n'importe laquelle des trois interfaces
python main.py        # Menu CLI
python gui.py         # Interface graphique de bureau (Qt / PySide6)
```


## Architecture

Chaque algorithme cryptographique est exposé sous la forme d'un module Python pur avec une API publique
(`chiffrer`, `dechiffrer`, `signer`, `verifier`, `chiffrer_bloc`, …) et une
fonction non-interactive `demo()`. Trois interfaces indépendantes consomment ces
modules sans dupliquer aucun code cryptographique.

```
              ┌────────────────────────────────────────────┐
              │        couche orientée utilisateur       │
              │  ┌────────┐   ┌────────┐   ┌──────────┐   │
              │  │  CLI   │   │   GUI    │   │
              │  │main.py │   │ gui.py   │   │
              │  └────┬───┘   └────┬───┘   └─────┬────┘   │
              └───────┴────────────┴─────────────┴────────┘
                        │ importlib + demo()
              ┌─────────┴───────────────────────────────────┐
              │         modules cryptographiques           │
              │                                           │
              │  classical/   symmetric/   asymmetric/    │
              │  hashing/     signatures/  applications/  │
              └─────────────┬───────────────────────────────┘
                           │
              ┌─────────────┴───────────────────────────────┐
              │  bibliotheques (primitives auditees)      │
              │  pycryptodome · cryptography · hashlib    │
              │  twofish · sympy · matplotlib             │
              └─────────────────────────────────────────────┘
```

### Couches de validation

| Couche | Mécanisme | Objectif |
|--------|-----------|----------|
| Correction de l'algorithme | Vecteurs officiels (NIST FIPS 180-4, 197, SP 800-38A, RFC 1321/4231/6229) | Les implémentations de zéro sont validées octet par octet |
| Tests de propriétés | Aller-retour, avalanche, malleéabilité, non-déterminisme | Les comportements crypto attendus vérifiés |
| Tests d'intégration | Serveur d'echo TCP/UDP, vote homomorphe de bout en bout | Composition complète des primitives |
| Vérifications statiques | `pytest --strict-markers`, `py_compile` | Les erreurs de typage et les imports détectés à froid |

### Primitives pédagogiques vs production

| Module | Style | Notes |
|--------|-------|-------|
| AES, DES/3DES, RSA-OAEP, RSA-PSS, ECDSA, DSA, ECDH, MD5/SHA-256/SHA-512 (hashlib) | Basé sur bibliothèque | `pycryptodome` / `cryptography` / stdlib — niveau production |
| Caesar, Vigenere, Hill, OTP | De zéro | Chiffres jouets, pédagogique |
| RC4, RC6, Serpent | De zéro | Validés par rapport aux vecteurs publiés |
| SHA-256, HMAC | De zéro | Validés par rapport à NIST FIPS 180-4 / RFC 4231 |
| Diffie-Hellman, ElGamal (chiffre + signature), arithmétique ECC | De zéro | Python pur — **pas de temporisation constante**, pédagogique uniquement |


## Exigences

| Dépendance | Version |
|-----------|---------|
| Python | 3.9+ |
| pycryptodome | 3.20+ |
| cryptography | 42+ |
| sympy | 1.12+ |
| matplotlib | 3.8+ |
| Pillow | 10+ |
| twofish | 0.3+ |
| pytest | 8+ |
| textual (TUI) | 0.50+ |
| PySide6 (GUI) | 6.5+ |


## Fonctionnalités

### Terminées


## Cibles de construction

| Module | Point d'entrée | Description |
|--------|-------------|-------------|
| `main` | `python main.py` | Menu CLI de marque — `Scénario` ou `Tester avec mes valeurs` interactif |
| `gui` | `python gui.py` | Bureau PySide6 — barre d'outils de marque, panneaux par module personnalisés, workers threads |
| `applications.tcp_secure` | `python -m applications.tcp_secure` | Serveur d'echo TCP sécurisé autonome |
| `applications.udp_chat` | `python -m applications.udp_chat` | Chat UDP sécurisé autonome |
| `applications.voting` | `python -m applications.voting` | Démonstration de vote homomorphe autonome |


## Utilisation

### CLI

```sh
python main.py                       # menu interactif (en-tête de marque, sections thématiques)
python main.py classical.caesar      # une démonstration par nom (non-interactif)
python main.py 2.3                   # par alias d'exercice de cours
python main.py all                   # exécuter chaque démo séquentiellement
python main.py --help                # aide
python -m classical.caesar           # contourner entièrement le menu
```

Le mode interactif affiche un en-tête de marque bleu français et répertorie chaque module par
thème. Après en avoir choisi un, vous pouvez choisir :

| Touche | Action |
|--------|--------|
| `s` | exécuter le `Scénario` précuit (sortie `demo()`) |
| `i` | ouvrir le formulaire (`Tester avec mes valeurs`) — mêmes champs que GUI |
| `q` | retour au menu |

Les couleurs ANSI se désactivent automatiquement quand stdout n'est pas un TTY, donc les redirections/canalisations restent propres.

### TUI

```sh
python tui.py
```

Le disposition reflète l'interface graphique : barre supérieure de marque, arborescence latérale des modules, deux
onglets côté droit (`Tester avec mes valeurs` par défaut + `Scénario`), barre d'état en bas.

| Shortcut | Action |
|----------|--------|
| `Ctrl+R` | Lancer scenario |
| `Ctrl+L` | Effacer la sortie |
| `i` / `s` | switch to `Mes valeurs` / `Scenario` tab |
| `q` | Quitter |
| `Enter` on a tree node | run that module |

### GUI

```sh
python gui.py
```

Branded toolbar in French Blue with `Lancer scenario` (Ctrl+R) and `Effacer`
(Ctrl+L). Default tab is `Tester avec mes valeurs` (interactive form or custom
panel — symmetric/asymmetric encrypt-decrypt, hash, signatures, network chats,
<p align="center">
  <h1 align="center">Locker</h1>
  <p align="center">A standalone cryptography laboratory for classical ciphers, symmetric and asymmetric primitives, hashing, signatures, and secure communication demos.</p>
</p>

<p align="center">
  <img src="https://img.shields.io/badge/python-3.9+-3776AB.svg?logo=python&logoColor=white" alt="Python">
  <img src="https://img.shields.io/badge/tests-pytest-green.svg" alt="Tests">
  <img src="https://img.shields.io/badge/ui-CLI%20%7C%20GUI-green.svg" alt="Interfaces">
</p>

Locker sépare la couche lanceur des moteurs cryptographiques. Les algorithmes vivent toujours dans les packages de domaine, tandis que le nouveau package `locker/` possède le catalogue, le routage et les points d'entrée orientés utilisateur.

## Installation

```sh
cd cryptography

python3 -m venv .venv
source .venv/bin/activate

pip install -r requirements.txt
```

If you prefer a different interpreter, use the matching `python3.x` binary for the virtual environment creation step.

## Run

```sh
python main.py --list
python main.py --theme symmetric
python main.py 2.3
python main.py --all
python tui.py
python gui.py
```

Le lanceur accepte également les noms de modules points tels que `classical.caesar` ou `applications.voting`. En mode interactif, chaque module peut être ouvert de deux façons :

1. `Scénario` exécute la sortie de démonstration cuite.
2. `Test with my values` opens the form-driven execution path.

Useful CLI options:

1. `--list` imprime le catalogue complet groupé par thème.
2. `--theme <name>` prints a single theme section.
3. `--all` runs every demo sequentially.
4. `--no-color` disables ANSI styling for redirected output.

## Architecture

Locker uses a thin orchestration layer above the crypto packages.

```text
user
  -> main.py / gui.py
  -> locker.cli / locker.catalog
  -> classical / symmetric / asymmetric / hashing / signatures / applications
```

The important separation is:

1. `locker.catalog` stores the registry of module paths, theme labels, and course aliases.
2. `locker.cli` rend le catalogue, résout les cibles et lance des démonstrations ou des exécutions de valeurs personnalisées.
3. `gui.py` importe le même catalogue pour que les deux interfaces restent alignées.
4. Les packages cryptographiques restent indépendants et peuvent toujours être importés directement pour les tests ou la réutilisation.

## Folder Structure

```text
cryptography/
  locker/
    __init__.py
    catalog.py
    cli.py
  classical/
  symmetric/
  asymmetric/
  hashing/
  signatures/
  applications/
  common/
  gui.py
  tui.py
  main.py
  tests/
```

## Interfaces

### CLI

`python main.py` ouvre le lanceur interactif. `python main.py 2.3` exécute la démonstration AES directement, et `python main.py --list` imprime le catalogue.

### TUI

`python tui.py` démarre l'interface Textual avec le catalogue partagé, une arborescence de modules, un formulaire de valeurs personnalisées et une vue de scénario.

### GUI

`python gui.py` ouvre l'application de bureau PySide6 avec le même modèle de sélection de module et la même division scénario/personnalisée.

## Algorithm Packages

Les moteurs cryptographiques restent séparés par domaine :

| Paquet | Contenu |
|--------|----------|
| `classical` | Caesar, Vigenere, Hill, OTP |
| `symmetric` | RC4, DES, AES, finalists |
| `asymmetric` | Diffie-Hellman, RSA, ElGamal, ECC |
| `hashing` | MD5, SHA-256, SHA-512, HMAC |
| `signatures` | Signatures RSA, signature ElGamal, DSA/ECDSA |
| `applications` | Démos de canal sécurisé, chat, vote, Bluetooth |

## Dependencies

| Dépendance | Objectif |
|-----------|----------|
| `pycryptodome` | Aide au chiffre de bloc et asymétrique |
| `cryptography` | RSA, ECDH, signatures, primitives de canal authentifié |
| `sympy` | Théorie des nombres et helpers d'algèbre |
| `matplotlib` | Graphiques de benchmark et de comparaison |
| `numpy` | Support numérique |
| `twofish` | Implémentation de référence Twofish |
| `Pillow` | Traitement d'images |
| `pytest` | Suite de tests |
| `textual` | Interface utilisateur terminal |
| `PySide6` | Interface graphique de bureau |

## Notes

`main.py` est maintenant un point d'entrée de compatibilité qui délègue à `locker.cli`. L'interface graphique utilise le même catalogue, de sorte que les étiquettes de navigation, les alias et l'ordre des modules restent cohérents.
│   └── pgm.py                    # PGM image reader/writer
