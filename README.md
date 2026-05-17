<p align="center">
  <h1 align="center">Crypto</h1>
  <p align="center">A reference cryptography laboratory covering classical ciphers, symmetric and asymmetric primitives, hash functions, digital signatures, and secure communication applications — with both a CLI and a PySide6 desktop GUI.</p>
</p>

<p align="center">
  <img src="https://img.shields.io/badge/python-3.9+-3776AB.svg?logo=python&logoColor=white" alt="Python">
  <img src="https://img.shields.io/badge/tests-126-brightgreen.svg" alt="Tests">
  <img src="https://img.shields.io/badge/algorithms-22-orange.svg" alt="Algorithms">
  <img src="https://img.shields.io/badge/coverage-NIST%20✓%20RFC%20✓-success.svg" alt="Coverage">
</p>


## Installation

```sh
git clone <repo-url> crypto
cd crypto

python3 -m venv .venv
source .venv/bin/activate

pip install -r requirements.txt
```


## Quick Start

```sh
python main.py           # interactive CLI menu
python gui.py            # PySide6 desktop GUI
```


## Architecture

Each cryptographic algorithm lives in its own Python module with a public API
(`chiffrer`, `dechiffrer`, `signer`, `verifier`, …) and a non-interactive
`demo()` function. Two independent interfaces consume these modules without
duplicating any cryptographic code.

```
             ┌────────────────────────────────────────────┐
             │         user-facing layer                  │
             │   ┌──────────┐         ┌──────────┐       │
             │   │   CLI    │         │   GUI    │       │
             │   │ main.py  │         │  gui.py  │       │
             │   └────┬─────┘         └────┬─────┘       │
             └────────┴────────────────────┴─────────────┘
                       │  locker.catalog + importlib
             ┌─────────┴─────────────────────────────────┐
             │        cryptographic modules              │
             │                                           │
             │  classical/   symmetric/   asymmetric/    │
             │  hashing/     signatures/  applications/  │
             └─────────────┬─────────────────────────────┘
                           │
             ┌─────────────┴─────────────────────────────┐
             │  libraries (audited primitives)           │
             │  pycryptodome · cryptography · hashlib    │
             │  twofish · sympy · matplotlib             │
             └───────────────────────────────────────────┘
```

The `locker/` package acts as the orchestration layer:

| Component | Role |
|-----------|------|
| `locker.catalog` | Central registry of module paths, theme labels, and course aliases |
| `locker.cli` | Renders the catalogue, resolves targets, and launches demos or custom-value forms |
| `gui.py` | Imports the same catalogue so both interfaces stay in sync |


## Algorithms

### Classical Ciphers — `classical/`

| Module | Description | Implementation |
|--------|-------------|----------------|
| `caesar` | Caesar cipher with brute-force and frequency analysis attacks | From scratch |
| `vigenere` | Vigenère cipher with Kasiski/frequency cryptanalysis | From scratch |
| `hill` | Hill cipher (matrix-based polygraphic) | From scratch |
| `otp` | One-Time Pad | From scratch |

### Symmetric Cryptography — `symmetric/`

| Module | Description | Implementation |
|--------|-------------|----------------|
| `stream/rc4` | RC4 stream cipher | From scratch, validated against published vectors |
| `block/des` | DES and Triple-DES (CBC mode) | Library (`pycryptodome`) |
| `block/aes` | AES-128/192/256 in CBC and CTR modes, with PGM image encryption demo | Library (`pycryptodome`) |
| `block/aes_finalists` | AES competition finalists: Serpent, Twofish, RC6 | From scratch (Serpent, RC6) + library (Twofish) |
| `block/_serpent` | Serpent block cipher internals | From scratch |

### Asymmetric Cryptography — `asymmetric/`

| Module | Description | Implementation |
|--------|-------------|----------------|
| `diffie_hellman` | Diffie-Hellman key exchange | From scratch (pure Python) |
| `rsa` | RSA-OAEP encryption/decryption | Library (`cryptography`) |
| `elgamal` | ElGamal encryption | From scratch (pure Python) |
| `ecc` | Elliptic curve arithmetic and ECDH key exchange | From scratch (pure Python) |

### Hash Functions — `hashing/`

| Module | Description | Implementation |
|--------|-------------|----------------|
| `md5` | MD5 digest | Library (`hashlib`) |
| `sha256` | SHA-256 — manual implementation validated against NIST FIPS 180-4 | From scratch |
| `sha512` | SHA-512 with multi-algorithm comparison | Library (`hashlib`) |
| `hmac` | HMAC — manual implementation validated against RFC 4231 | From scratch + stdlib comparison |

### Digital Signatures — `signatures/`

| Module | Description | Implementation |
|--------|-------------|----------------|
| `rsa_signature` | RSA PKCS#1 v1.5 and PSS signatures | Library (`cryptography`) |
| `elgamal_sig` | ElGamal signature scheme | From scratch (pure Python) |
| `dsa_ecdsa` | DSA and ECDSA (P-256, P-384, P-521) | Library (`cryptography`) |

### Secure Communication — `applications/`

| Module | Description |
|--------|-------------|
| `secure_channel` | Core SecureChannel protocol: RSA-OAEP key exchange + AES-CTR + HMAC-SHA256 |
| `tcp_secure` | TCP echo server with SecureChannel |
| `udp_chat` | UDP secure chat |
| `bluetooth_secure` | Bluetooth RFCOMM secure channel |
| `ble_secure` | Bluetooth Low Energy (BLE) secure channel via GATT (bleak/bless) |
| `voting` | Homomorphic e-voting demonstration (Paillier) |

### Utilities — `common/`

| Module | Description |
|--------|-------------|
| `pgm` | PGM (P5 grayscale) image reader/writer for block cipher visual demos |


## Interfaces

### CLI — `python main.py`

```sh
python main.py                       # interactive menu
python main.py classical.caesar      # run a single demo by name
python main.py 2.3                   # by course alias
python main.py --all                 # run every demo sequentially
python main.py --list                # print the full catalogue
python main.py --theme symmetric     # print a single theme section
python main.py --no-color            # disable ANSI colours
```

In interactive mode, selecting a module opens a prompt:

| Key | Action |
|-----|--------|
| `s` | Run the pre-built `Scénario` (`demo()` output) |
| `i` | Open the `Tester avec mes valeurs` form (same fields as the GUI) |
| `q` | Return to menu |

ANSI colours are disabled automatically when stdout is not a TTY.

### GUI — `python gui.py`

PySide6 desktop application with:

- **Algorithm browser** sidebar with search/filter.
- **Two tabs per module**: `Tester avec mes valeurs` (interactive form or custom panel) and `Scénario` (pre-built demo output).
- Toolbar with `Lancer scénario` (`Ctrl+R`) and `Effacer` (`Ctrl+L`).
- Dedicated panels for symmetric/asymmetric encrypt–decrypt, hashing, signatures, TCP/UDP/Bluetooth chat, and voting.
- Worker threads for non-blocking demo execution.

### BLE Demo Scripts

```sh
python ble_serveur.py    # Linux peripheral (bless)
python ble_client.py     # macOS/Linux central (bleak)
```


## Project Structure

```
crypto/
├── main.py                          # CLI entry point (delegates to locker.cli)
├── gui.py                           # PySide6 desktop GUI
├── gui_panels.py                    # Custom GUI panels (symmetric, asymmetric, hash, etc.)
├── gui_apps.py                      # Application-specific panels (TCP, UDP, BLE, voting)
├── gui_specs.py                     # Form field descriptors and runners
├── gui_widgets.py                   # Shared GUI widget helpers
├── ble_client.py                    # BLE central demo script
├── ble_serveur.py                   # BLE peripheral demo script
├── locker/
│   ├── __init__.py                  # Package exports
│   ├── catalog.py                   # Module registry, themes, course aliases
│   └── cli.py                       # Independent CLI launcher
├── classical/
│   ├── caesar.py
│   ├── vigenere.py
│   ├── hill.py
│   └── otp.py
├── symmetric/
│   ├── stream/
│   │   └── rc4.py
│   └── block/
│       ├── aes.py
│       ├── aes_finalists.py         # Serpent, Twofish, RC6
│       ├── des.py
│       └── _serpent.py
├── asymmetric/
│   ├── diffie_hellman.py
│   ├── rsa.py
│   ├── elgamal.py
│   └── ecc.py
├── hashing/
│   ├── md5.py
│   ├── sha256.py
│   ├── sha512.py
│   └── hmac.py
├── signatures/
│   ├── rsa_signature.py
│   ├── elgamal_sig.py
│   └── dsa_ecdsa.py
├── applications/
│   ├── secure_channel.py
│   ├── tcp_secure.py
│   ├── udp_chat.py
│   ├── bluetooth_secure.py
│   ├── ble_secure.py
│   └── voting.py
├── common/
│   └── pgm.py                      # PGM image reader/writer
├── assets/                          # PGM sample images for block cipher demos
├── tests/
│   ├── test_classical.py
│   ├── test_symmetric.py
│   ├── test_asymmetric.py
│   ├── test_hashing.py
│   ├── test_signatures.py
│   ├── test_applications.py
│   ├── test_bluetooth_wrapper.py
│   ├── test_bluetooth_loopback.py
│   └── test_ble_wrapper.py
├── requirements.txt
├── pyproject.toml
└── .gitignore
```


## Testing

```sh
pytest                   # run the full suite (126 tests)
pytest tests/ -v         # verbose output
pytest -k "hashing"      # filter by keyword
```

Tests cover:

| Layer | Mechanism |
|-------|-----------|
| Algorithm correctness | Official vectors (NIST FIPS 180-4, FIPS 197, SP 800-38A, RFC 1321/4231/6229) |
| Property tests | Round-trip, avalanche, malleability, non-determinism |
| Integration tests | TCP/UDP echo server, end-to-end homomorphic voting |
| Static checks | `pytest --strict-markers`, `py_compile` |


## Dependencies

| Dependency | Version | Purpose |
|------------|---------|---------|
| Python | 3.9+ | Runtime |
| `pycryptodome` | ≥ 3.20 | Block cipher and asymmetric helpers |
| `cryptography` | ≥ 42 | RSA, ECDH, signatures, authenticated channel primitives |
| `sympy` | ≥ 1.12 | Number theory and algebra helpers |
| `matplotlib` | ≥ 3.8 | Benchmark and comparison charts |
| `numpy` | ≥ 1.26 | Numeric support |
| `twofish` | ≥ 0.3 | Twofish reference implementation |
| `Pillow` | ≥ 10 | Image processing |
| `pytest` | ≥ 8 | Test suite |
| `textual` | ≥ 0.50 | Terminal UI (reserved) |
| `PySide6` | ≥ 6.5 | Desktop GUI |
| `bleak` | ≥ 0.21 | BLE central role (scanner/client) |
| `bless` | ≥ 0.2.6 | BLE peripheral role (GATT server) |


## Course Aliases

Modules are mapped to numbered course aliases for quick access:

| Alias | Module |
|-------|--------|
| 1.1 | `classical.caesar` |
| 1.2 | `classical.vigenere` |
| 1.3 | `classical.hill` |
| 1.4 | `classical.otp` |
| 2.1 | `symmetric.rc4` |
| 2.2 | `symmetric.des` |
| 2.3 | `symmetric.aes` |
| 2.4 | `symmetric.finalists` |
| 3.1 | `asymmetric.dh` |
| 3.2 | `asymmetric.rsa` |
| 3.3 | `asymmetric.elgamal` |
| 3.4 | `asymmetric.ecc` |
| 4.1 | `hashing.md5` |
| 4.2 | `hashing.sha256` |
| 4.3 | `hashing.sha512` |
| 4.4 | `hashing.hmac` |
| 5.1 | `signatures.rsa` |
| 5.2 | `signatures.elgamal` |
| 5.3 | `signatures.dsa_ecdsa` |
| 6.1 | `applications.tcp` |
| 6.2 | `applications.bluetooth` |
| 6.3 | `applications.udp` |
| 6.4 | `applications.voting` |


## Notes

- **Educational vs production**: From-scratch implementations (Diffie-Hellman, ElGamal, ECC, RC4, RC6, Serpent, SHA-256, HMAC) are pure Python with no constant-time guarantees — they are intended for learning, not production use.
- `main.py` delegates to `locker.cli` at runtime. The `locker/` package centralises the module registry so both CLI and GUI stay in sync.
- PGM sample images in `assets/` are used by the AES/DES block cipher demos to visualise ECB vs CBC vs CTR mode differences.
