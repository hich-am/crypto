
import importlib
import io
import sys
from contextlib import redirect_stdout

from PySide6.QtCore import QObject, QThread, Qt, Signal
"""Interface graphique pour les démonstrations Locker (PySide6).

Le volet gauche est un navigateur de modules où on peut chercher. Le volet droit garde les deux
vues habituelles par module : un scénario codé en dur et un formulaire personnalisé.
"""

import importlib
import io
import sys
from contextlib import redirect_stdout

from PySide6.QtCore import QObject, QThread, Qt, Signal
from PySide6.QtGui import QAction, QFont
from PySide6.QtWidgets import (
    QApplication,
    QComboBox,
    QFormLayout,
    QFrame,
    QHBoxLayout,
    QLabel,
    QLineEdit,
    QMainWindow,
    QPlainTextEdit,
    QProgressBar,
    QPushButton,
    QSpinBox,
    QSplitter,
    QStackedWidget,
    QStatusBar,
    QTabWidget,
    QToolBar,
    QTreeWidget,
    QTreeWidgetItem,
    QVBoxLayout,
    QWidget,
)

from locker.catalog import MODULE_CATALOG as MODULES, THEME_LABELS as THEMES, THEME_SEQUENCE as THEME_ORDER
from gui_apps import BluetoothChatPanel, TcpChatPanel, UdpChatPanel, VotingPanel
from gui_panels import (
    AsymmetricEncryptPanel,
    ClassicalPanel,
    HMACPanel,
    HashPanel,
    KeyExchangePanel,
    SignaturePanel,
    SymmetricCipherPanel,
)
from gui_specs import BYTES_HEX, BYTES_UTF8, CHOICE, INT, MULTILINE, SPECS, TEXT, Champ, Spec


PANELS_PERSO = {
    "applications.tcp_secure": TcpChatPanel,
    "applications.udp_chat": UdpChatPanel,
    "applications.bluetooth_secure": BluetoothChatPanel,
    "applications.voting": VotingPanel,
    "classical.caesar": lambda: ClassicalPanel("Caesar"),
    "classical.vigenere": lambda: ClassicalPanel("Vigenere"),
    "classical.otp": lambda: ClassicalPanel("OTP"),
    "classical.hill": lambda: ClassicalPanel("Hill"),
    "symmetric.stream.rc4": lambda: SymmetricCipherPanel("RC4"),
    "symmetric.block.des": lambda: SymmetricCipherPanel("DES"),
    "symmetric.block.aes": lambda: SymmetricCipherPanel("AES"),
    "asymmetric.rsa": lambda: AsymmetricEncryptPanel("RSA"),
    "asymmetric.elgamal": lambda: AsymmetricEncryptPanel("ElGamal"),
    "asymmetric.diffie_hellman": lambda: KeyExchangePanel("DH"),
    "asymmetric.ecc": lambda: KeyExchangePanel("ECDH"),
    "hashing.md5": lambda: HashPanel("MD5"),
    "hashing.sha256": lambda: HashPanel("SHA-256"),
    "hashing.sha512": lambda: HashPanel("SHA-512"),
    "hashing.hmac": lambda: HMACPanel(),
    "signatures.rsa_signature": lambda: SignaturePanel("RSA-PSS"),
    "signatures.elgamal_sig": lambda: SignaturePanel("ElGamal"),
    "signatures.dsa_ecdsa": lambda: SignaturePanel("ECDSA-P256"),
}


def _navigation_matches(theme: str, slug: str, module_path: str, label: str, query: str) -> bool:
    query = query.strip().lower()
    if not query:
        return True
    haystack = " ".join((theme, slug, module_path, label)).lower()
    return query in haystack


STYLESHEET = """
* {
    font-family: "Helvetica Neue", "Inter", "Segoe UI", Arial, sans-serif;
    font-size: 13px;
}

QMainWindow, QWidget {
    background-color: #ffffff;
    color: #111827;
}

QSplitter::handle {
    background-color: #e5e7eb;
    width: 1px;
}
QSplitter::handle:hover { background-color: #22c55e; }

#sidebarShell {
    background-color: #f8fafc;
    border-right: 1px solid #e5e7eb;
}

#sidebarTitle {
    color: #111827;
    font-size: 18px;
    font-weight: 700;
}

#sidebarSubtitle {
    color: #475569;
}

#sidebarCount {
    color: #22c55e;
    font-weight: 600;
}

#navigationCard {
    background-color: #ffffff;
    border: 1px solid #e5e7eb;
    border-radius: 12px;
}

#navigationSearch {
    background-color: #ffffff;
    color: #111827;
    border: 1px solid #cbd5e1;
    border-radius: 8px;
    padding: 8px 10px;
}

#navigationSearch:focus {
    border: 1px solid #22c55e;
}

QToolBar {
    background-color: #ffffff;
    border: none;
    border-bottom: 1px solid #e5e7eb;
    spacing: 4px;
    padding: 10px 16px;
}

#brand, #brand QLabel {
    background-color: transparent;
    color: #111827;
}

QToolBar QToolButton {
    background-color: transparent;
    color: #111827;
    border: 1px solid transparent;
    border-radius: 6px;
    padding: 6px 12px;
    font-weight: 600;
}
QToolBar QToolButton:hover {
    background-color: rgba(34, 197, 94, 0.10);
}

QStatusBar {
    background-color: #ffffff;
    color: #475569;
    border-top: 1px solid #e5e7eb;
    padding: 0 14px;
    min-height: 28px;
}

QTreeWidget {
    background-color: #ffffff;
    color: #111827;
    border: none;
    padding: 8px 0;
    outline: none;
    show-decoration-selected: 1;
}
QTreeWidget::item {
    padding: 6px 10px;
    color: #111827;
    border: none;
}
QTreeWidget::item:hover:!selected {
    background-color: #f3f4f6;
}
QTreeWidget::item:selected,
QTreeWidget::item:selected:active {
    background-color: #dcfce7;
    color: #111827;
    font-weight: 600;
}
QTreeWidget::branch {
    background-color: #ffffff;
}

QTabWidget, QTabWidget::pane, QTabBar {
    background-color: #ffffff;
}
QTabWidget::pane {
    border: none;
    border-top: 1px solid #e5e7eb;
    top: -1px;
}
QTabBar::tab {
    background-color: #ffffff;
    color: #475569;
    padding: 12px 24px;
    border: none;
    border-bottom: 2px solid transparent;
    font-weight: 500;
}
QTabBar::tab:selected {
    color: #111827;
    border-bottom: 2px solid #22c55e;
    font-weight: 600;
}

QPlainTextEdit, QLineEdit, QSpinBox, QComboBox {
    background-color: #ffffff;
    color: #111827;
    border: 1px solid #cbd5e1;
    border-radius: 6px;
    selection-background-color: #dcfce7;
    selection-color: #111827;
}
QPlainTextEdit:focus, QLineEdit:focus, QSpinBox:focus, QComboBox:focus {
    border-color: #22c55e;
}
QPlainTextEdit {
    border-radius: 8px;
    padding: 14px;
}
QLineEdit, QSpinBox, QComboBox {
    padding: 8px 12px;
}

QPushButton {
    background-color: #ffffff;
    color: #111827;
    border: 1px solid #cbd5e1;
    border-radius: 6px;
    padding: 8px 18px;
}
QPushButton:hover {
    background-color: #f8fafc;
    border-color: #22c55e;
}
QPushButton[primary="true"] {
    background-color: #22c55e;
    color: #ffffff;
    border: 1px solid #22c55e;
    font-weight: 600;
}
QPushButton[primary="true"]:hover {
    background-color: #16a34a;
    border-color: #16a34a;
}

QScrollBar:vertical, QScrollBar:horizontal {
    background: transparent;
}
QScrollBar::handle:vertical, QScrollBar::handle:horizontal {
    background: #cbd5e1;
    border-radius: 6px;
}
QScrollBar::handle:vertical:hover, QScrollBar::handle:horizontal:hover {
    background: #22c55e;
}

QToolTip {
    background-color: #ffffff;
    color: #111827;
    border: 1px solid #22c55e;
    border-radius: 4px;
    padding: 5px 9px;
}
"""


def _divider() -> QFrame:
    frame = QFrame()
    frame.setProperty("role", "divider")
    frame.setFrameShape(QFrame.Shape.HLine)
    return frame


def _set_role(widget, role):
    widget.setProperty("role", role)
    return widget


class RunDemoWorker(QObject):
    sortie = Signal(str)
    erreur = Signal(str)
    fini = Signal()

    def __init__(self, chemin: str) -> None:
        super().__init__()
        self.chemin = chemin

    def run(self) -> None:
        try:
            module = importlib.import_module(self.chemin)
            if not hasattr(module, "demo"):
                self.sortie.emit(f"{self.chemin} : pas de fonction demo()")
                return
            buf = io.StringIO()
            with redirect_stdout(buf):
                module.demo()
            self.sortie.emit(buf.getvalue())
        except Exception as e:
            self.erreur.emit(f"{type(e).__name__}: {e}")
        finally:
            self.fini.emit()


class ValueFormPanel(QWidget):
    def __init__(self, spec: Spec, label: str):
        super().__init__()
        self._spec = spec
        self._widgets: dict = {}

        outer = QVBoxLayout(self)
        outer.setContentsMargins(24, 20, 24, 20)
        outer.setSpacing(12)

        title = QLabel(label)
        _set_role(title, "title")
        outer.addWidget(title)

        subtitle = QLabel("Renseignez les valeurs ci-dessous puis lancez le calcul.")
        _set_role(subtitle, "subtitle")
        outer.addWidget(subtitle)
        outer.addWidget(_divider())

        form = QFormLayout()
        form.setLabelAlignment(Qt.AlignmentFlag.AlignLeft)
        form.setSpacing(10)
        for champ in spec.champs:
            widget = self._make_widget(champ)
            self._widgets[champ.cle] = widget
            label_w = QLabel(champ.label if not champ.note else f"{champ.label}\n{champ.note}")
            form.addRow(label_w, widget)
        outer.addLayout(form)

        row = QHBoxLayout()
        btn = QPushButton("Lancer avec ces valeurs")
        btn.setProperty("primary", True)
        btn.clicked.connect(self._run)
        row.addWidget(btn)
        row.addStretch(1)
        outer.addLayout(row)

        outer.addWidget(QLabel("Resultat"))
        self._output = QPlainTextEdit()
        self._output.setReadOnly(True)
        self._output.setFont(QFont("Menlo", 12))
        self._output.setPlaceholderText("Le resultat sera affiche ici.")
        outer.addWidget(self._output, 1)

    def _make_widget(self, champ: Champ) -> QWidget:
        if champ.type == TEXT:
            widget = QLineEdit()
            widget.setText(str(champ.defaut))
            return widget
        if champ.type in (MULTILINE, BYTES_UTF8):
            widget = QPlainTextEdit()
            widget.setPlainText(str(champ.defaut))
            widget.setMaximumHeight(110)
            return widget
        if champ.type == INT:
            widget = QSpinBox()
            widget.setRange(int(champ.minimum), int(champ.maximum))
            widget.setValue(int(champ.defaut) if champ.defaut != "" else 0)
            return widget
        if champ.type == BYTES_HEX:
            widget = QLineEdit()
            widget.setText(str(champ.defaut))
            widget.setFont(QFont("Menlo", 12))
            return widget
        if champ.type == CHOICE:
            widget = QComboBox()
            widget.addItems(list(champ.options))
            if champ.defaut in champ.options:
                widget.setCurrentText(str(champ.defaut))
            return widget
        raise ValueError(f"Type de champ inconnu : {champ.type}")

    def _read_field(self, champ: Champ):
        widget = self._widgets[champ.cle]
        if champ.type == TEXT:
            return widget.text()
        if champ.type == MULTILINE:
            return widget.toPlainText()
        if champ.type == BYTES_UTF8:
            return widget.toPlainText().encode("utf-8")
        if champ.type == INT:
            return widget.value()
        if champ.type == BYTES_HEX:
            txt = widget.text().strip().replace(" ", "")
            return bytes.fromhex(txt) if txt else b""
        if champ.type == CHOICE:
            return widget.currentText()
        raise ValueError(f"Type de champ inconnu : {champ.type}")

    def _run(self):
        try:
            values = {champ.cle: self._read_field(champ) for champ in self._spec.champs}
        except ValueError as e:
            self._output.setPlainText(f"[ERREUR ENTREE] {e}")
            return
        try:
            result = self._spec.runner(values)
        except Exception as e:
            result = f"[ERREUR EXECUTION] {type(e).__name__}: {e}"
        self._output.setPlainText(result)


class CipherForgeWindow(QMainWindow):
    def __init__(self) -> None:
        super().__init__()
        self.setWindowTitle("Locker")
        self.resize(1320, 840)
        self._thread: QThread | None = None
        self._worker: RunDemoWorker | None = None
        self._nav_filter = ""

        splitter = QSplitter(Qt.Orientation.Horizontal)
        splitter.setHandleWidth(1)

        self.sidebar = QWidget()
        self.sidebar.setObjectName("sidebarShell")
        sidebar_layout = QVBoxLayout(self.sidebar)
        sidebar_layout.setContentsMargins(16, 16, 16, 16)
        sidebar_layout.setSpacing(10)

        title = QLabel("Navigateur d'algorithmes")
        title.setObjectName("sidebarTitle")
        sidebar_layout.addWidget(title)

        subtitle = QLabel("Parcourez par thème ou cherchez un module.")
        subtitle.setObjectName("sidebarSubtitle")
        subtitle.setWordWrap(True)
        sidebar_layout.addWidget(subtitle)

        self.nav_count = QLabel("")
        self.nav_count.setObjectName("sidebarCount")
        sidebar_layout.addWidget(self.nav_count)

        self.navigation_search = QLineEdit()
        self.navigation_search.setObjectName("navigationSearch")
        self.navigation_search.setPlaceholderText("Chercher un algorithme, thème ou alias")
        self.navigation_search.textChanged.connect(self._refresh_navigation)
        sidebar_layout.addWidget(self.navigation_search)

        card = QFrame()
        card.setObjectName("navigationCard")
        card_layout = QVBoxLayout(card)
        card_layout.setContentsMargins(0, 0, 0, 0)
        card_layout.setSpacing(0)

        self.arbre = QTreeWidget()
        self.arbre.setHeaderHidden(True)
        self.arbre.setIndentation(14)
        self.arbre.itemDoubleClicked.connect(self._double_click_module)
        self.arbre.currentItemChanged.connect(self._current_module_changed)
        card_layout.addWidget(self.arbre, 1)
        sidebar_layout.addWidget(card, 1)
        splitter.addWidget(self.sidebar)

        self.tabs = QTabWidget()
        self.tabs.setDocumentMode(True)

        scenar_widget = QWidget()
        scenar_layout = QVBoxLayout(scenar_widget)
        scenar_layout.setContentsMargins(24, 20, 24, 20)
        scenar_layout.setSpacing(12)
        scenar_title = QLabel("Sortie du scénario")
        _set_role(scenar_title, "title")
        scenar_layout.addWidget(scenar_title)
        scenar_subtitle = QLabel("Lancez le scénario prédéfini d'un module pour voir la sortie complète.")
        _set_role(scenar_subtitle, "subtitle")
        scenar_subtitle.setWordWrap(True)
        scenar_layout.addWidget(scenar_subtitle)
        scenar_layout.addWidget(_divider())
        self.sortie = QPlainTextEdit()
        self.sortie.setReadOnly(True)
        self.sortie.setFont(QFont("Menlo", 12))
        self.sortie.setPlaceholderText("Sélectionnez un module et lancez le scénario.")
        scenar_layout.addWidget(self.sortie, 1)

        self.custom_stack = QStackedWidget()
        self._stack_index: dict[str, int] = {}
        default_widget = QWidget()
        default_layout = QVBoxLayout(default_widget)
        default_layout.setContentsMargins(24, 60, 24, 24)
        default_layout.setSpacing(8)
        default_title = QLabel("Selectionnez un module")
        _set_role(default_title, "title")
        default_title.setAlignment(Qt.AlignmentFlag.AlignCenter)
        default_layout.addWidget(default_title)
        default_subtitle = QLabel("Choisissez un algorithme dans la barre latérale pour le tester avec vos propres valeurs.")
        _set_role(default_subtitle, "subtitle")
        default_subtitle.setAlignment(Qt.AlignmentFlag.AlignCenter)
        default_subtitle.setWordWrap(True)
        default_layout.addWidget(default_subtitle)
        default_layout.addStretch(1)
        self.custom_stack.addWidget(default_widget)
        for module_path, label in MODULES.values():
            panel = self._create_custom_panel(module_path, label)
            self._stack_index[module_path] = self.custom_stack.addWidget(panel)

        self.tabs.addTab(self.custom_stack, "Tester avec mes valeurs")
        self.tabs.addTab(scenar_widget, "Scenario")
        splitter.addWidget(self.tabs)
        splitter.setSizes([320, 1000])
        splitter.setCollapsible(0, False)
        splitter.setCollapsible(1, False)
        self.setCentralWidget(splitter)

        toolbar = QToolBar("Actions")
        toolbar.setMovable(False)
        brand_widget = QWidget()
        brand_widget.setObjectName("brand")
        brand_widget.setFixedWidth(300)
        brand_layout = QHBoxLayout(brand_widget)
        brand_layout.setContentsMargins(24, 0, 8, 0)
        brand_layout.setSpacing(8)
        brand_label = QLabel("Locker")
        brand_label.setStyleSheet("QLabel { color: #111827; font-size: 22px; font-weight: 700; background-color: transparent; }")
        brand_layout.addWidget(brand_label)
        brand_layout.addStretch(1)
        toolbar.addWidget(brand_widget)

        spacer = QWidget()
        spacer.setFixedWidth(28)
        toolbar.addWidget(spacer)

        self._action_run_btn = QPushButton("Lancer scenario")
        self._action_run_btn.setProperty("primary", True)
        self._action_run_btn.setShortcut("Ctrl+R")
        self._action_run_btn.clicked.connect(self._run_selected)
        toolbar.addWidget(self._action_run_btn)
        toolbar.addWidget(QWidget())
        self._action_clear_btn = QPushButton("Effacer")
        self._action_clear_btn.setProperty("primary", True)
        self._action_clear_btn.setShortcut("Ctrl+L")
        self._action_clear_btn.clicked.connect(self.sortie.clear)
        toolbar.addWidget(self._action_clear_btn)

        self._action_run = QAction("Lancer scenario", self)
        self._action_run.setShortcut("Ctrl+R")
        self._action_run.triggered.connect(self._run_selected)
        self._action_clear = QAction("Effacer", self)
        self._action_clear.setShortcut("Ctrl+L")
        self._action_clear.triggered.connect(self.sortie.clear)
        self.addAction(self._action_run)
        self.addAction(self._action_clear)
        self.addToolBar(toolbar)

        self.setStatusBar(QStatusBar())
        self._status = QLabel(" Pret")
        _set_role(self._status, "status-idle")
        self.statusBar().addWidget(self._status)
        self._progress = QProgressBar()
        self._progress.setRange(0, 0)
        self._progress.setMaximumWidth(180)
        self._progress.hide()
        self.statusBar().addPermanentWidget(self._progress)
        self._module_status = QLabel("")
        _set_role(self._module_status, "subtitle")
        self.statusBar().addPermanentWidget(self._module_status)

        self._refresh_navigation("")

    def _create_custom_panel(self, module_path: str, label: str) -> QWidget:
        if module_path in PANELS_PERSO:
            return self._wrap_panel(PANELS_PERSO[module_path](), label)
        if module_path in SPECS:
            return ValueFormPanel(SPECS[module_path], label)
        return self._unavailable_panel(label)

    def _wrap_panel(self, panel: QWidget, label: str) -> QWidget:
        container = QWidget()
        layout = QVBoxLayout(container)
        layout.setContentsMargins(24, 20, 24, 20)
        layout.setSpacing(12)
        title = QLabel(label)
        _set_role(title, "title")
        layout.addWidget(title)
        subtitle = QLabel("Mode interactif. Démarrez le scénario depuis la barre d'outils si le panneau n'expose pas de champs.")
        _set_role(subtitle, "subtitle")
        subtitle.setWordWrap(True)
        layout.addWidget(subtitle)
        layout.addWidget(_divider())
        layout.addWidget(panel, 1)
        return container

    def _unavailable_panel(self, label: str) -> QWidget:
        widget = QWidget()
        layout = QVBoxLayout(widget)
        layout.setContentsMargins(24, 40, 24, 24)
        layout.setSpacing(8)
        title = QLabel(label)
        _set_role(title, "title")
        title.setAlignment(Qt.AlignmentFlag.AlignCenter)
        layout.addWidget(title)
        subtitle = QLabel("Pas de saisie personnalisée pour ce module. Lancez le scénario prédéfini.")
        _set_role(subtitle, "subtitle")
        subtitle.setAlignment(Qt.AlignmentFlag.AlignCenter)
        subtitle.setWordWrap(True)
        layout.addWidget(subtitle)
        layout.addStretch(1)
        return widget

    def _refresh_navigation(self, query: str = "") -> None:
        current = self.arbre.currentItem()
        current_path = current.data(0, Qt.ItemDataRole.UserRole) if current is not None else None
        self._nav_filter = query
        self.arbre.clear()

        visible = 0
        selected_item = None
        for theme in THEME_ORDER:
            theme_item = QTreeWidgetItem([THEMES[theme]])
            f = theme_item.font(0)
            f.setBold(True)
            f.setPointSize(11)
            theme_item.setFont(0, f)
            theme_item.setFlags(theme_item.flags() & ~Qt.ItemFlag.ItemIsSelectable)

            for (theme_name, slug), (module_path, label) in MODULES.items():
                if theme_name != theme:
                    continue
                if not _navigation_matches(theme_name, slug, module_path, label, query):
                    continue
                leaf = QTreeWidgetItem([label])
                leaf.setData(0, Qt.ItemDataRole.UserRole, module_path)
                theme_item.addChild(leaf)
                visible += 1
                if current_path == module_path:
                    selected_item = leaf

            if theme_item.childCount() > 0:
                self.arbre.addTopLevelItem(theme_item)
                theme_item.setExpanded(True)

        self.nav_count.setText(f"{visible} module(s) displayed")
        if selected_item is not None:
            self.arbre.setCurrentItem(selected_item)
        elif self.arbre.topLevelItemCount() > 0:
            first_theme = self.arbre.topLevelItem(0)
            if first_theme.childCount() > 0:
                self.arbre.setCurrentItem(first_theme.child(0))

    def _current_module_changed(self, item, _previous):
        if item is None:
            return
        module_path = item.data(0, Qt.ItemDataRole.UserRole)
        if module_path and module_path in self._stack_index:
            self.custom_stack.setCurrentIndex(self._stack_index[module_path])
        else:
            self.custom_stack.setCurrentIndex(0)

    def _double_click_module(self, item: QTreeWidgetItem, _column: int) -> None:
        module_path = item.data(0, Qt.ItemDataRole.UserRole)
        if module_path:
            self._run(module_path)

    def _run_selected(self) -> None:
        item = self.arbre.currentItem()
        if item is None:
            return
        module_path = item.data(0, Qt.ItemDataRole.UserRole)
        if module_path:
            self._run(module_path)

    def _busy(self) -> bool:
        if self._thread is None:
            return False
        try:
            return self._thread.isRunning()
        except RuntimeError:
            self._thread = None
            self._worker = None
            return False

    def _set_status(self, text: str, running: bool, module_path: str = "") -> None:
        self._status.setText(text)
        self._module_status.setText(f"  {module_path}" if module_path else "")
        if running:
            _set_role(self._status, "status-active")
            self._progress.show()
        else:
            _set_role(self._status, "status-idle")
            self._progress.hide()

    def _run(self, module_path: str) -> None:
        if self._busy():
            self.statusBar().showMessage("Occupe : attendez la fin du run.", 2500)
            return
        self.tabs.setCurrentIndex(1)
        self.sortie.appendPlainText(f"\n=== {module_path} ===")
        self._set_status(" En cours", True, module_path)

        worker = RunDemoWorker(module_path)
        thread = QThread()
        worker.moveToThread(thread)
        thread.started.connect(worker.run)
        worker.sortie.connect(self.sortie.appendPlainText)
        worker.erreur.connect(lambda msg: self.sortie.appendPlainText(f"\n[ERREUR] {msg}"))
        worker.fini.connect(thread.quit)
        thread.finished.connect(lambda: self._thread_finished(thread, worker))
        thread.finished.connect(worker.deleteLater)
        thread.finished.connect(thread.deleteLater)
        self._worker = worker
        self._thread = thread
        thread.start()

    def _thread_finished(self, thread, worker) -> None:
        if self._thread is thread:
            self._thread = None
        if self._worker is worker:
            self._worker = None
        self._set_status(" Pret", False)


def run_gui() -> None:
    app = QApplication(sys.argv)
    app.setStyle("Fusion")
    app.setStyleSheet(STYLESHEET)
    window = CipherForgeWindow()
    window.show()
    sys.exit(app.exec())


DemoWorker = RunDemoWorker
FormPanel = ValueFormPanel
CryptoFenetre = CipherForgeWindow


if __name__ == "__main__":
    run_gui()
