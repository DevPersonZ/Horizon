# nahh why wyvren cracking ts ???
from __future__ import annotations
import ctypes
import json
import os
import re
import shlex
import shutil
import subprocess
import sys
import tempfile
import time
import urllib.parse
import urllib.request
import zipfile
from datetime import datetime
from dataclasses import dataclass
from html import escape
from pathlib import Path
from string import Template

from PySide6.QtCore import (
    Property, QEasingCurve, QEvent, QObject, QPoint, QPropertyAnimation,
    QRectF, QRect, QRunnable, QSettings, QSize, Qt, QThread, QThreadPool, QTimer,
    QUrl, QVariantAnimation, Signal,
)
from PySide6.QtGui import (
    QAction, QColor, QDesktopServices, QFontDatabase, QGuiApplication, QIcon, QLinearGradient,
    QPainter, QPainterPath, QPen, QPixmap, QRadialGradient, QShortcut, QKeySequence,
)
from PySide6.QtSvg import QSvgRenderer
from PySide6.QtWidgets import (
    QAbstractButton, QApplication, QButtonGroup, QColorDialog, QFileDialog, QFrame,
    QGraphicsOpacityEffect, QGridLayout, QHBoxLayout, QLabel, QLineEdit, QMainWindow,
    QMessageBox, QProgressBar, QPushButton, QScrollArea, QSizePolicy, QSlider, QStackedWidget,
    QTextEdit, QVBoxLayout, QWidget,
)
from shiboken6 import isValid


APP_NAME = "Horizon Loader"
APP_VERSION = "2.1.0"
STEAM_APP_ID = "1533390"
GAME_EXE = "Gorilla Tag.exe"
GAME_FOLDER = "Gorilla Tag"
DRAWER_W = 330
TITLEBAR_H = 64

AlignCenter = Qt.AlignmentFlag.AlignCenter
AlignVCenter = Qt.AlignmentFlag.AlignVCenter
AlignLeft = Qt.AlignmentFlag.AlignLeft
Pointing = Qt.CursorShape.PointingHandCursor
AA = QPainter.RenderHint.Antialiasing
NoPen = Qt.PenStyle.NoPen
NoBrush = Qt.BrushStyle.NoBrush

TM: "ThemeManager" = None  # set in main() once QApplication exists




FONT_UI = '"Century Gothic", "URW Gothic", "Avenir Next", "Futura", "Segoe UI", Arial, sans-serif'
FONT_TITLE = '"Technological", "Orbitron", "Century Gothic", sans-serif'
FONT_GAME = '"Copperplate Gothic Bold", "Copperplate Gothic Light", "Copperplate Gothic", "Copperplate", "Trajan Pro", Georgia, serif'


def load_custom_fonts():
    here = Path(__file__).resolve().parent
    for folder in (here / "fonts", here):
        if not folder.is_dir():
            continue
        for f in folder.iterdir():
            if f.suffix.lower() in (".ttf", ".otf"):
                QFontDatabase.addApplicationFont(str(f))


# ───────────────────────────── icon bullshit ─────────────────────────────
ICONS = {
    "menu": '<path d="M4 8h16"/><path d="M4 16h10"/>',
    "close": '<path d="M6 6l12 12"/><path d="M18 6L6 18"/>',
    "minimize": '<path d="M6 12h12"/>',
    "maximize": '<rect x="5" y="5" width="14" height="14" rx="3.5"/>',
    "restore": '<rect x="9" y="9" width="10" height="10" rx="3"/><path d="M15 5H8a3 3 0 0 0-3 3v7"/>',
    "home": '<path d="M4 11.5L12 4l8 7.5V19a1.5 1.5 0 0 1-1.5 1.5H15.5V14h-7v6.5H5.5A1.5 1.5 0 0 1 4 19z"/>',
    "play": '<path d="M8 5.5v13a1 1 0 0 0 1.5.86l10-6.5a1 1 0 0 0 0-1.72l-10-6.5A1 1 0 0 0 8 5.5z"/>',
    "box": '<path d="M12 3l8 4.5v9L12 21l-8-4.5v-9z"/><path d="M4 7.5L12 12l8-4.5"/><path d="M12 12v9"/>',
    "sliders": '<path d="M4 7h9"/><path d="M19 7h1"/><path d="M4 17h1"/><path d="M11 17h9"/><circle cx="16" cy="7" r="2.5"/><circle cx="8" cy="17" r="2.5"/>',
    "folder": '<path d="M3.5 8A2.5 2.5 0 0 1 6 5.5h3.2c.6 0 1.2.3 1.6.8l1 1.2H18A2.5 2.5 0 0 1 20.5 10v7a2.5 2.5 0 0 1-2.5 2.5H6A2.5 2.5 0 0 1 3.5 17z"/>',
    "trash": '<path d="M5 7h14"/><path d="M10 7V5h4v2"/><path d="M7 7l.8 11a2 2 0 0 0 2 1.9h4.4a2 2 0 0 0 2-1.9L17 7"/><path d="M10.5 11v5"/><path d="M13.5 11v5"/>',
    "refresh": '<path d="M20 11a8 8 0 0 0-14.3-4.5L4 8.5"/><path d="M4 4v4.5h4.5"/><path d="M4 13a8 8 0 0 0 14.3 4.5l1.7-2"/><path d="M20 20v-4.5h-4.5"/>',
    "search": '<circle cx="10.5" cy="10.5" r="6.5"/><path d="M20 20l-4.9-4.9"/>',
    "download": '<path d="M12 4v11"/><path d="M7.5 10.5L12 15l4.5-4.5"/><path d="M5 19.5h14"/>',
    "terminal": '<rect x="3" y="4.5" width="18" height="15" rx="3.5"/><path d="M7.5 9.5l3 2.5-3 2.5"/><path d="M13 15h3.5"/>',
    "info": '<circle cx="12" cy="12" r="9"/><path d="M12 11v5.5"/><path d="M12 7.6v.01"/>',
    "palette": '<path d="M12 3.5a8.5 8.5 0 1 0 0 17c1.4 0 2-.9 2-1.9 0-1.3-1-1.6-1-2.6 0-1 .8-1.5 1.8-1.5H17a3.5 3.5 0 0 0 3.5-3.5C20.5 6.7 16.7 3.5 12 3.5z"/><path d="M8 11v.01"/><path d="M11 7.8v.01"/><path d="M15.2 8.6v.01"/>',
    "check": '<path d="M5 12.5l4.5 4.5L19 7.5"/>',
    "external": '<path d="M14 4h6v6"/><path d="M20 4l-9 9"/><path d="M18 14v3.5a2.5 2.5 0 0 1-2.5 2.5h-9A2.5 2.5 0 0 1 4 17.5v-9A2.5 2.5 0 0 1 6.5 6H10"/>',
    "power": '<path d="M12 3.5v8"/><path d="M7.2 6.8a7.5 7.5 0 1 0 9.6 0"/>',
    "plus": '<path d="M12 5v14"/><path d="M5 12h14"/>',
    "vr": '<path d="M3.5 9.5A2.5 2.5 0 0 1 6 7h12a2.5 2.5 0 0 1 2.5 2.5v5A2.5 2.5 0 0 1 18 17h-3l-1.2-2h-3.6L9 17H6a2.5 2.5 0 0 1-2.5-2.5z"/>',
    "shield": '<path d="M12 3.5L19 6v5.5c0 4.2-3 7.4-7 9-4-1.6-7-4.8-7-9V6z"/>',
    "zap": '<path d="M13.5 3L5.5 13.5H11L10 21l8.5-10.5H13z"/>',
    "file": '<path d="M7.5 3.5h6L19 9v10a1.5 1.5 0 0 1-1.5 1.5h-10A1.5 1.5 0 0 1 6 19V5a1.5 1.5 0 0 1 1.5-1.5z"/><path d="M13.5 3.5V9H19"/>',
    "moon": '<path d="M19.5 14.5A8 8 0 0 1 9.5 4.5a8 8 0 1 0 10 10z"/>',
    "sun": '<circle cx="12" cy="12" r="3.8"/><path d="M12 3.5v1.8"/><path d="M12 18.7v1.8"/><path d="M3.5 12h1.8"/><path d="M18.7 12h1.8"/><path d="M6 6l1.3 1.3"/><path d="M16.7 16.7L18 18"/><path d="M6 18l1.3-1.3"/><path d="M16.7 7.3L18 6"/>',
    "contrast": '<circle cx="12" cy="12" r="8.5"/><path d="M12 3.5a8.5 8.5 0 0 1 0 17z"/>',
    "alert": '<path d="M12 4l9 15.5H3z"/><path d="M12 10v4.2"/><path d="M12 17.2v.01"/>',
    "copy": '<rect x="8.5" y="8.5" width="11" height="11" rx="2.5"/><path d="M15.5 8.5v-2A2.5 2.5 0 0 0 13 4H6.5A2.5 2.5 0 0 0 4 6.5V13a2.5 2.5 0 0 0 2.5 2.5h2"/>',
    "list": '<path d="M9 7h11"/><path d="M9 12h11"/><path d="M9 17h11"/><path d="M4.5 7v.01"/><path d="M4.5 12v.01"/><path d="M4.5 17v.01"/>',
    "gamepad": '<path d="M7 7.5h10a4 4 0 0 1 3.9 3.2l.8 4a2.7 2.7 0 0 1-5.1 1.9L15.2 15H8.8l-1.4 1.6a2.7 2.7 0 0 1-5.1-1.9l.8-4A4 4 0 0 1 7 7.5z"/><path d="M8 10.5v3"/><path d="M6.5 12h3"/><path d="M15.5 11.5v.01"/><path d="M17.5 13.5v.01"/>',
    "eye": '<path d="M2.5 12S6 5.5 12 5.5 21.5 12 21.5 12 18 18.5 12 18.5 2.5 12 2.5 12z"/><circle cx="12" cy="12" r="2.8"/>',
    "wand": '<path d="M5 19l9.5-9.5"/><path d="M13 8l3 3"/><path d="M17.5 3.5v3"/><path d="M16 5h3"/><path d="M20 10v2"/><path d="M19 11h2"/><path d="M8 4v2"/><path d="M7 5h2"/>',
#    thankfully im good at image shi
}
FILLED_ICONS = {"play", "zap"}
# soft tinted fill behind the outline, gives the set a duotone look
DUO_ICONS = {"home", "box", "folder", "info", "palette", "vr", "shield", "file", "moon", "sun", "alert", "gamepad", "maximize", "restore"}
_icon_cache: dict = {}


def icon_pixmap(name: str, color: str, size: int = 20) -> QPixmap:
    dpr = max(2.0, QGuiApplication.primaryScreen().devicePixelRatio() if QGuiApplication.primaryScreen() else 2.0)
    key = (name, color, size, dpr)
    if key in _icon_cache:
        return _icon_cache[key]
    fill = color if (name in FILLED_ICONS or name in DUO_ICONS) else "none"
    fill_op = "0.18" if name in DUO_ICONS else "1"
    svg = (
        '<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 24 24" '
        f'fill="{fill}" fill-opacity="{fill_op}" stroke="{color}" stroke-width="1.8" stroke-linecap="round" '
        f'stroke-linejoin="round">{ICONS[name]}</svg>'
    )
    pm = QPixmap(int(size * dpr), int(size * dpr))
    pm.fill(Qt.GlobalColor.transparent)
    pm.setDevicePixelRatio(dpr)
    painter = QPainter(pm)
    painter.setRenderHint(AA)
    QSvgRenderer(svg.encode("utf-8")).render(painter, QRectF(0, 0, size, size))
    painter.end()
    _icon_cache[key] = pm
    return pm


# ───────────────────────────── Color bullshit ─────────────────────────────
def mix(a: QColor, b: QColor, t: float) -> QColor:
    return QColor(
        int(a.red() + (b.red() - a.red()) * t),
        int(a.green() + (b.green() - a.green()) * t),
        int(a.blue() + (b.blue() - a.blue()) * t),
    )


def shift_hue(c: QColor, deg: float) -> QColor:
    h, s, v, _ = c.getHsvF()
    if h < 0:
        h = 0.0
    return QColor.fromHsvF((h + deg / 360.0) % 1.0, s, v)


def lum(c: QColor) -> float:
    return (0.299 * c.red() + 0.587 * c.green() + 0.114 * c.blue()) / 255.0


def contrast_text(c: QColor) -> str:
    return "#0b0d14" if lum(c) > 0.6 else "#ffffff"


def rgba(c: QColor, a: int) -> str:
    return f"rgba({c.red()}, {c.green()}, {c.blue()}, {a})"


# ───────────────────────────── theme model ─────────────────────────────
PRESETS = [
    ("rexon purple", "#8b5cf6"), ("ocean", "#38bdf8"), ("mint", "#34d399"), ("lava", "#f97316"),
    ("rose", "#fb7185"), ("sunrise", "#facc15"), ("crimson cauldron", "#ef4444"), ("orchid", "#e879f9"),
]
MODES = {
    "mono": ("mono", "contrast"),
    "midnight": ("night", "moon"),
    "charcoal": ("coal", "contrast"),
    "light": ("light", "sun"),
}


@dataclass
class Theme:
    accent: str = "#ffffff"
    mode: str = "mono"
    gradient: bool = False


def build_palette(t: Theme) -> dict:
    a = QColor(t.accent)
    if t.mode == "mono":
        # the design: pure black, white outlines, white text. "subtle" is for hairlines that shouldn't glare
        base = dict(bg="#000000", panel="#000000", card="#000000", border="#ffffff", hover="#1a1a1a",
                    text="#ffffff", muted="#b5b5b5", danger="#ff6b6b", success="#4ade80", warn="#fbbf24",
                    subtle="#3a3a3a")
        tint = 0.0
    elif t.mode == "light":
        base = dict(bg="#eef0f7", panel="#f8f9fd", card="#ffffff", border="#dcdfeb", hover="#e8ebf5",
                    text="#171b2d", muted="#667091", danger="#dc2626", success="#059669", warn="#d97706")
        tint = 0.04
    elif t.mode == "charcoal":
        base = dict(bg="#0e0e0f", panel="#151516", card="#1d1d1f", border="#2b2b2e", hover="#27272a",
                    text="#ededf0", muted="#8d8d96", danger="#f87171", success="#34d399", warn="#fbbf24")
        tint = 0.02
    else:
        base = dict(bg="#0a0c13", panel="#0f121b", card="#161a27", border="#232a3f", hover="#1d2235",
                    text="#e8ebf8", muted="#868fac", danger="#f87171", success="#34d399", warn="#fbbf24")
        tint = 0.05
    pal = dict(base)
    for k in ("bg", "panel", "card", "hover"):
        pal[k] = mix(QColor(base[k]), a, tint).name()
    pal["border"] = mix(QColor(base["border"]), a, tint * 1.2).name()
    pal["subtle"] = base.get("subtle", pal["border"])
    a2 = shift_hue(a, 38) if t.gradient else a
    if t.mode == "light":
        at = a.darker(135) if lum(a) > 0.45 else a
    else:
        at = a.lighter(135) if lum(a) < 0.45 else a
    pal.update(
        accent=a.name(), accent2=a2.name(), accent_text=at.name(), on_accent=contrast_text(a),
        accent_hover=a.lighter(112).name(), accent_soft=rgba(a, 40), accent_line=rgba(a, 120),
        danger_soft=rgba(QColor(base["danger"]), 40), success_soft=rgba(QColor(base["success"]), 40),
    )
    return pal


QSS = Template(r"""
* { font-family: $font_ui; font-size: 13px; color: $text; outline: none; }
QMainWindow, QWidget#Root, QWidget#Transparent { background: transparent; }
QLabel { background: transparent; }
QDialog, QMessageBox { background: $panel; }
QToolTip { background: $card; color: $text; border: 1px solid $border; padding: 6px 9px; border-radius: 8px; }

QFrame#Shell { background: $bg; border: 2px solid $border; border-radius: 18px; }
QFrame#Shell[max="true"] { border-radius: 0px; }
QFrame#TitleBar { background: transparent; border: none; }
QLabel#AppName { font-family: $font_title; font-size: 34px; font-weight: normal; }
QLabel#PlayEyebrow { font-family: $font_title; font-size: 22px; font-weight: normal; }
QLabel#PlayTitle { font-family: $font_game; font-size: 42px; font-weight: normal; }
QLabel#PlayStatus { color: $muted; font-size: 11px; font-weight: normal; }

QFrame#Sidebar { background: transparent; border: none; }
QFrame#MiniCard { background: $card; border: 1px solid $border; border-radius: 12px; }
QLabel#Section { color: $muted; font-size: 11px; font-weight: 700; }
QLabel#H1 { font-size: 24px; font-weight: 800; }
QLabel#H2 { font-size: 15px; font-weight: 700; }
QLabel#Muted { color: $muted; font-size: 12px; }
QLabel#RowTitle { font-weight: 600; }
QLabel#StatValue { font-size: 20px; font-weight: 700; }
QLabel#ModName { font-size: 14px; font-weight: 600; }
QFrame#ModRow[off="true"] QLabel#ModName { color: $muted; }

QPushButton#NavBtn { background: $bg; border: 1px solid $border; border-radius: 9px; padding: 0 8px; text-align: center; color: $text; font-weight: normal; font-size: 15px; }
QPushButton#NavBtn:hover { background: $hover; }
QPushButton#NavBtn:checked { background: $text; color: $bg; }

QFrame#Card { background: $card; border: 1px solid $border; border-radius: 14px; }
QFrame#ModRow { background: $card; border: 1px solid $subtle; border-radius: 12px; }
QFrame#ModRow:hover { border-color: $border; }
QFrame#IconTile { background: $accent_soft; border: none; border-radius: 10px; }
QFrame#Divider { background: $subtle; border: none; min-height: 1px; max-height: 1px; }
QFrame#DropZone { border: 2px dashed transparent; border-radius: 14px; background: transparent; }
QFrame#DropZone[drag="true"] { border-color: $accent; background: $accent_soft; }
QFrame#Toast { background: $card; border: 1px solid $border; border-radius: 12px; }
QFrame#Scrim { background: rgba(0, 0, 0, 140); border-bottom-left-radius: 13px; border-bottom-right-radius: 13px; }
QFrame#Drawer { background: $panel; border: none; border-right: 1px solid $border; border-bottom-left-radius: 13px; }
QFrame#DrawerHead { background: transparent; border: none; border-bottom: 1px solid $border; }

QLabel#Badge { border-radius: 9px; padding: 3px 10px; font-size: 11px; font-weight: 700; }
QLabel#Badge[on="true"] { background: $success_soft; color: $success; }
QLabel#Badge[on="false"] { background: $hover; color: $muted; }

QPushButton { background: $card; border: 1px solid $border; border-radius: 10px; padding: 8px 14px; font-weight: 600; }
QPushButton:hover { background: $hover; border-color: $accent_line; }
QPushButton:pressed { background: $accent_soft; }
QPushButton:disabled { color: $muted; }
QPushButton#Primary { background: qlineargradient(x1:0, y1:0, x2:1, y2:0, stop:0 $accent, stop:1 $accent2); color: $on_accent; border: none; border-radius: 11px; padding: 10px 18px; font-weight: 700; }
QPushButton#Primary:hover { background: qlineargradient(x1:0, y1:0, x2:1, y2:0, stop:0 $accent_hover, stop:1 $accent2); }
QPushButton#Primary:disabled { background: $border; color: $muted; }
QPushButton#IconBtn { padding: 0; border-radius: 10px; min-width: 38px; max-width: 38px; min-height: 38px; max-height: 38px; }
QPushButton#IconBtn[danger="true"]:hover { background: $danger_soft; border-color: $danger; }
QPushButton#TitleBtn { background: $bg; border: 1px solid $border; border-radius: 8px; padding: 0; }
QPushButton#TitleBtn:hover { background: $text; }
QPushButton#Pill { background: transparent; border: 1px solid $border; border-radius: 15px; padding: 6px 14px; color: $muted; }
QPushButton#Pill:hover { color: $text; background: $hover; }
QPushButton#Pill:checked { background: $accent_soft; border-color: $accent; color: $accent_text; }
QPushButton#ModeCard { text-align: left; padding: 11px 12px; border-radius: 11px; color: $muted; }
QPushButton#ModeCard:checked { background: $accent_soft; border-color: $accent; color: $accent_text; }
QPushButton#PlayBtn { background: $bg; color: $text; border: 1px solid $border; border-radius: 14px; padding: 0; min-height: 64px; max-height: 64px; font-size: 26px; font-weight: normal; }
QPushButton#PlayBtn:hover { background: $hover; }
QPushButton#PlayBtn:pressed { background: $text; color: $bg; }
QPushButton#PlayBtn:disabled { background: $bg; color: $muted; border-color: $subtle; }
QPushButton#ModeBtn { background: $bg; color: $text; border: 1px solid $border; border-radius: 9px; padding: 0 12px; min-height: 36px; max-height: 36px; font-size: 14px; font-weight: normal; }
QPushButton#ModeBtn:hover { background: $hover; }
QPushButton#ModeBtn:checked { background: $text; color: $bg; }

QLabel#HeroEyebrow { color: rgba(255, 255, 255, 190); font-size: 11px; font-weight: 800; }
QLabel#HeroTitle { color: #ffffff; font-size: 34px; font-weight: 800; }
QLabel#HeroSub { color: rgba(255, 255, 255, 215); font-size: 14px; }
QFrame#HeroChip { background: rgba(255, 255, 255, 36); border-radius: 12px; }
QFrame#HeroChip QLabel { color: #ffffff; font-weight: 600; font-size: 12px; }
QPushButton#ProfileCard { text-align: left; padding: 14px 16px; border-radius: 14px; }
QPushButton#ProfileCard:checked { background: $accent_soft; border-color: $accent; }
QLabel#ImpactScore { font-size: 42px; font-weight: 800; }
QLabel#ImpactHint { color: $muted; font-size: 12px; }

QLineEdit { background: $card; border: 1px solid $border; border-radius: 10px; padding: 9px 12px; selection-background-color: $accent; selection-color: $on_accent; }
QLineEdit:focus { border: 1px solid $accent; }
QTextEdit#LogView { background: $panel; border: 1px solid $border; border-radius: 12px; padding: 8px; font-family: "Cascadia Mono", "Consolas", "Menlo", "DejaVu Sans Mono", monospace; font-size: 12px; selection-background-color: $accent; selection-color: $on_accent; }
QSpinBox { background: $card; border: 1px solid $border; border-radius: 6px; padding: 3px; }

QProgressBar { background: $subtle; border: none; border-radius: 4px; min-height: 8px; max-height: 8px; text-align: center; color: transparent; }
QProgressBar::chunk { border-radius: 4px; background: qlineargradient(x1:0, y1:0, x2:1, y2:0, stop:0 $accent, stop:1 $accent2); }

QScrollArea, QAbstractScrollArea { background: transparent; border: none; }
QScrollBar:vertical { background: transparent; width: 10px; margin: 2px; }
QScrollBar::handle:vertical { background: $subtle; border-radius: 3px; min-height: 30px; }
QScrollBar::handle:vertical:hover { background: $muted; }
QScrollBar:horizontal { background: transparent; height: 10px; margin: 2px; }
QScrollBar::handle:horizontal { background: $subtle; border-radius: 3px; min-width: 30px; }
QScrollBar::add-line, QScrollBar::sub-line { width: 0px; height: 0px; }
QScrollBar::add-page, QScrollBar::sub-page { background: transparent; }

QSlider::groove:horizontal { height: 8px; border-radius: 4px; background: $subtle; }
QSlider::sub-page:horizontal, QSlider::add-page:horizontal { background: transparent; }
QSlider::handle:horizontal { background: #ffffff; border: 2px solid $accent; width: 14px; height: 14px; margin: -5px 0; border-radius: 9px; }
""")


class ThemeManager(QObject):
    """Owns the current theme, persists it, applies the stylesheet, and re-tints icons."""
    changed = Signal()

    def __init__(self):
        super().__init__()
        self.settings = QSettings("HorizonLoader", "HorizonLoader")
        self.theme = Theme()
        self.pal = build_palette(self.theme)
        self._bound: list = []
        self._timer = QTimer(self)
        self._timer.setSingleShot(True)
        self._timer.timeout.connect(self.apply)

    # ----- mutation -----
    def set_accent(self, hex_color: str):
        c = QColor(hex_color)
        if c.isValid():
            self.theme.accent = c.name()
            self._schedule()

    def set_mode(self, mode: str):
        if mode in MODES:
            self.theme.mode = mode
            self._schedule()

    def set_gradient(self, on: bool):
        self.theme.gradient = bool(on)
        self._schedule()

    def reset(self):
        self.theme = Theme()
        self._schedule()

    def _schedule(self):
        self.settings.setValue("theme/accent", self.theme.accent)
        self.settings.setValue("theme/mode", self.theme.mode)
        self.settings.setValue("theme/gradient", self.theme.gradient)
        self.pal = build_palette(self.theme)
        self._timer.start(25)  # coalesce rapid slider drags

    def apply(self):
        self.pal = build_palette(self.theme)
        app = QApplication.instance()
        app.setStyleSheet(QSS.substitute({**self.pal, "font_ui": FONT_UI, "font_title": FONT_TITLE, "font_game": FONT_GAME}))
        app.setWindowIcon(QIcon(icon_pixmap("zap", self.pal["accent"], 64)))
        self.refresh_icons()
        self.changed.emit()

    # ----- icons -----
    def resolve(self, role: str) -> str:
        if role == "accent":
            return self.pal["accent_text"]
        return self.pal.get(role, role)

    def bind_icon(self, widget, name: str, role="text", size: int = 18):
        first = not hasattr(widget, "_icon_spec")
        widget._icon_spec = [name, role, size]
        if first:
            self._bound.append(widget)
            if callable(role) and isinstance(widget, QAbstractButton) and widget.isCheckable():
                widget.toggled.connect(lambda *_a, w=widget: self.apply_icon(w))
        self.apply_icon(widget)

    def apply_icon(self, widget):
        if not isValid(widget):
            return
        name, role, size = widget._icon_spec
        if callable(role):
            role = role(widget)
        pm = icon_pixmap(name, self.resolve(role), size)
        if isinstance(widget, QLabel):
            widget.setPixmap(pm)
        else:
            widget.setIcon(QIcon(pm))
            if hasattr(widget, "setIconSize"):
                widget.setIconSize(QSize(size, size))

    def refresh_icons(self):
        self._bound = [w for w in self._bound if isValid(w)]
        for w in self._bound:
            self.apply_icon(w)


# ───────────────────────────── small utilities ─────────────────────────────
def repolish(w: QWidget):
    w.style().unpolish(w)
    w.style().polish(w)
    w.update()


def human_size(n: float) -> str:
    for unit in ("B", "KB", "MB", "GB"):
        if n < 1024 or unit == "GB":
            return f"{int(n)} B" if unit == "B" else f"{n:.1f} {unit}"
        n /= 1024
    return f"{n:.1f} GB"


def open_path(path: Path):
    QDesktopServices.openUrl(QUrl.fromLocalFile(str(path)))


def reveal_path(path: Path):
    if sys.platform == "win32" and path.is_file():
        subprocess.Popen(f'explorer /select,"{path}"')
    else:
        open_path(path if path.is_dir() else path.parent)


def scrolled(widget: QWidget) -> QScrollArea:
    sa = QScrollArea()
    sa.setWidgetResizable(True)
    sa.setFrameShape(QFrame.Shape.NoFrame)
    sa.setHorizontalScrollBarPolicy(Qt.ScrollBarPolicy.ScrollBarAlwaysOff)
    sa.setWidget(widget)
    widget.setAutoFillBackground(False)
    sa.viewport().setAutoFillBackground(False)
    return sa


def icon_btn(icon: str, tip: str, danger: bool = False) -> QPushButton:
    b = QPushButton()
    b.setObjectName("IconBtn")
    b.setToolTip(tip)
    b.setCursor(Pointing)
    b.setProperty("danger", "true" if danger else "false")
    TM.bind_icon(b, icon, "danger" if danger else "text", 18)
    return b


def text_btn(label: str, icon: str, primary: bool = False) -> QPushButton:
    b = QPushButton("  " + label)
    b.setCursor(Pointing)
    if primary:
        b.setObjectName("Primary")
    TM.bind_icon(b, icon, "on_accent" if primary else "text", 18)
    return b


def card_header(icon: str, title: str) -> QHBoxLayout:
    h = QHBoxLayout()
    h.setSpacing(10)
    ic = QLabel()
    ic.setFixedSize(22, 22)
    TM.bind_icon(ic, icon, "accent", 20)
    t = QLabel(title)
    t.setObjectName("H2")
    h.addWidget(ic)
    h.addWidget(t)
    h.addStretch(1)
    return h


def make_card() -> tuple[QFrame, QVBoxLayout]:
    f = QFrame()
    f.setObjectName("Card")
    v = QVBoxLayout(f)
    v.setContentsMargins(20, 18, 20, 18)
    v.setSpacing(12)
    return f, v


def divider() -> QFrame:
    d = QFrame()
    d.setObjectName("Divider")
    d.setFixedHeight(1)
    return d


def setting_row(title: str, desc: str, control: QWidget) -> QWidget:
    w = QWidget()
    h = QHBoxLayout(w)
    h.setContentsMargins(0, 4, 0, 4)
    h.setSpacing(16)
    v = QVBoxLayout()
    v.setSpacing(2)
    t = QLabel(title)
    t.setObjectName("RowTitle")
    d = QLabel(desc)
    d.setObjectName("Muted")
    d.setWordWrap(True)
    v.addWidget(t)
    v.addWidget(d)
    h.addLayout(v, 1)
    h.addWidget(control, 0, AlignVCenter)
    return w


def section_label(text: str) -> QLabel:
    l = QLabel(text)
    l.setObjectName("Section")
    return l


# ───────────────────────────── game / mod discovery ─────────────────────────────
def _steam_roots() -> list[Path]:
    roots: list[Path] = []
    if sys.platform == "win32":
        try:
            import winreg
            for hive, key, val in (
                (winreg.HKEY_CURRENT_USER, r"Software\Valve\Steam", "SteamPath"),
                (winreg.HKEY_LOCAL_MACHINE, r"SOFTWARE\WOW6432Node\Valve\Steam", "InstallPath"),
                (winreg.HKEY_LOCAL_MACHINE, r"SOFTWARE\Valve\Steam", "InstallPath"),
            ):
                try:
                    with winreg.OpenKey(hive, key) as k:
                        roots.append(Path(winreg.QueryValueEx(k, val)[0]))
                except OSError:
                    pass
        except ImportError:
            pass
        for env in ("ProgramFiles(x86)", "ProgramFiles"):
            base = os.environ.get(env)
            if base:
                roots.append(Path(base) / "Steam")
    else:
        home = Path.home()
        roots += [home / ".steam" / "steam", home / ".local" / "share" / "Steam",
                  home / ".var" / "app" / "com.valvesoftware.Steam" / ".local" / "share" / "Steam"]
    return [r for r in roots if r.exists()]


def detect_game_dir() -> Path | None:
    candidates: list[Path] = []
    for root in _steam_roots():
        libs = [root]
        vdf = root / "steamapps" / "libraryfolders.vdf"
        if vdf.exists():
            try:
                text = vdf.read_text(encoding="utf-8", errors="ignore")
                libs += [Path(m.replace("\\\\", "\\")) for m in re.findall(r'"path"\s+"([^"]+)"', text)]
            except OSError:
                pass
        candidates += [lib / "steamapps" / "common" / GAME_FOLDER for lib in libs]
    if sys.platform == "win32":
        for drive in "CDEFGH":
            candidates.append(Path(f"{drive}:/Program Files/Oculus/Software/Software/another-axiom-gorilla-tag"))
            candidates.append(Path(f"{drive}:/Oculus/Software/Software/another-axiom-gorilla-tag"))
    for c in candidates:
        try:
            if (c / GAME_EXE).exists():
                return c
        except OSError:
            continue
    return None


def file_version(path: Path) -> str:
    """Read the Win32 FileVersion of a DLL (returns '' elsewhere / on failure)."""
    if sys.platform != "win32":
        return ""
    try:
        import ctypes
        from ctypes import wintypes
        ver = ctypes.windll.version
        p = str(path)
        size = ver.GetFileVersionInfoSizeW(p, None)
        if not size:
            return ""
        buf = ctypes.create_string_buffer(size)
        if not ver.GetFileVersionInfoW(p, 0, size, buf):
            return ""
        lp = ctypes.c_void_p()
        ln = wintypes.UINT()
        if not ver.VerQueryValueW(buf, "\\", ctypes.byref(lp), ctypes.byref(ln)) or not ln.value:
            return ""

        class FIXED(ctypes.Structure):
            _fields_ = [(n, wintypes.DWORD) for n in (
                "sig", "struc", "fvms", "fvls", "pvms", "pvls", "mask", "flags", "os", "type", "sub", "dtms", "dtls")]

        info = ctypes.cast(lp, ctypes.POINTER(FIXED)).contents
        parts = [info.fvms >> 16, info.fvms & 0xFFFF, info.fvls >> 16, info.fvls & 0xFFFF]
        if not any(parts):
            return ""
        while len(parts) > 2 and parts[-1] == 0:
            parts.pop()
        return ".".join(str(x) for x in parts)
    except Exception:
        return ""


def guess_version(stem: str) -> str:
    m = re.search(r"[vV]?(\d+(?:\.\d+){1,3})", stem)
    return m.group(1) if m else ""


@dataclass
class Mod:
    path: Path
    name: str
    enabled: bool
    size: int
    mtime: float
    version: str
    folder: str


def scan_mods(plugins: Path) -> list[Mod]:
    mods: list[Mod] = []
    if not plugins.exists():
        return mods
    for p in plugins.rglob("*"):
        try:
            if not p.is_file():
                continue
            low = p.name.lower()
            if low.endswith(".dll"):
                enabled, stem = True, p.name[:-4]
            elif low.endswith(".dll.disabled"):
                enabled, stem = False, p.name[:-13]
            else:
                continue
            st = p.stat()
            rel = p.parent.relative_to(plugins)
            folder = "" if str(rel) == "." else str(rel)
            mods.append(Mod(p, stem, enabled, st.st_size, st.st_mtime,
                            file_version(p) or guess_version(stem), folder))
        except (OSError, ValueError):
            continue
    mods.sort(key=lambda m: (m.name.lower(), m.folder))
    return mods


def mod_key(m: Mod) -> str:
    return f"{m.folder}/{m.name}" if m.folder else m.name


def app_data_dir() -> Path:
    if sys.platform == "win32":
        base = Path(os.environ.get("APPDATA", str(Path.home() / "AppData" / "Roaming")))
    else:
        base = Path.home() / ".config"
    p = base / "HorizonLoader"
    p.mkdir(parents=True, exist_ok=True)
    return p


def player_log_paths() -> list[Path]:
    home = Path.home()
    return [
        home / "AppData" / "LocalLow" / "Another Axiom" / "Gorilla Tag" / "Player.log",
        home / "AppData" / "LocalLow" / "Another Axiom" / "Gorilla Tag" / "Player-prev.log",
    ]


# ───────────────────────────── performance boost ─────────────────────────────
PERF_PROFILES = {
    "stock": dict(priority=False, quiet_logs=False, gfx_jobs=False, nolog=False, d3d11=False, workers=False, no_throttle=False),
    "boost": dict(priority=True, quiet_logs=True, gfx_jobs=True, nolog=True, d3d11=False, workers=True, no_throttle=True),
    "max": dict(priority=True, quiet_logs=True, gfx_jobs=True, nolog=True, d3d11=True, workers=True, no_throttle=True),
}

PERF_WEIGHTS = dict(priority=18, quiet_logs=14, gfx_jobs=22, nolog=8, d3d11=16, workers=12, no_throttle=10)
PERF_LABELS = {
    "stock": ("STOCK", "unity defaults. horizon won't touch your game files."),
    "boost": ("BOOST", "high priority, no logs, gfx jobs and more threads."),
    "max": ("MAX", "everything in boost plus direct3d 11 and the heavier windows tweaks."),
    "custom": ("CUSTOM", "your own mix. gets applied every time you launch."),
}


def cpu_workers() -> int:
    n = os.cpu_count() or 4
    return max(2, min(15, n - 1))


def perf_score(opts: dict) -> int:
    return min(100, sum(PERF_WEIGHTS[k] for k, on in opts.items() if on and k in PERF_WEIGHTS))


def _ini_patch(path: Path, updates: dict[str, dict[str, str]], spaced: bool = True):
    sections: dict[str, dict[str, str]] = {}
    order: list[str] = []
    current = ""
    if path.exists():
        try:
            text = path.read_text(encoding="utf-8", errors="ignore")
        except OSError:
            text = ""
        for raw in text.splitlines():
            line = raw.strip()
            if line.startswith("[") and line.endswith("]"):
                current = line[1:-1]
                if current not in sections:
                    sections[current] = {}
                    order.append(current)
            elif "=" in line and current and not line.startswith("#") and not line.startswith(";"):
                k, _, v = line.partition("=")
                sections.setdefault(current, {})[k.strip()] = v.strip()
    for sec, kvs in updates.items():
        if sec not in sections:
            order.append(sec)
            sections[sec] = {}
        sections[sec].update(kvs)
    sep = " = " if spaced else "="
    lines: list[str] = []
    for sec in order:
        lines.append(f"[{sec}]")
        for k, v in sections[sec].items():
            lines.append(f"{k}{sep}{v}")
        lines.append("")
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text("\n".join(lines).rstrip() + "\n", encoding="utf-8")


def _boot_patch(path: Path, updates: dict[str, str], remove: bool):
    data: dict[str, str] = {}
    extra: list[str] = []
    if path.exists():
        try:
            for raw in path.read_text(encoding="utf-8", errors="ignore").splitlines():
                if "=" in raw and not raw.lstrip().startswith("#"):
                    k, _, v = raw.partition("=")
                    data[k.strip()] = v.strip()
                elif raw.strip():
                    extra.append(raw)
        except OSError:
            pass
    if remove:
        for k in updates:
            data.pop(k, None)
    else:
        data.update(updates)
    path.parent.mkdir(parents=True, exist_ok=True)
    body = "".join(f"{k}={v}\n" for k, v in data.items())
    if extra:
        body += "\n".join(extra) + "\n"
    path.write_text(body, encoding="utf-8")


def _backup(path: Path):
    bak = path.with_suffix(path.suffix + ".horizonbak")
    if path.exists() and not bak.exists():
        shutil.copy2(path, bak)


def _restore_or_keep(path: Path):
    bak = path.with_suffix(path.suffix + ".horizonbak")
    if bak.exists():
        shutil.copy2(bak, path)


def apply_performance_files(game_dir: Path, opts: dict) -> list[str]:
    """HOLY MOLY!!!!!!11 BEPINEX WORK FAST :DDDDDDDDDD"""
    applied: list[str] = []
    bep_cfg = game_dir / "BepInEx" / "config" / "BepInEx.cfg"
    door = game_dir / "doorstop_config.ini"
    boot = game_dir / "Gorilla Tag_Data" / "boot.config"

    if opts.get("quiet_logs"):
        _backup(bep_cfg)
        _ini_patch(bep_cfg, {
            "Logging.Console": {"Enabled": "false"},
            "Logging.Disk": {"UnityLogListening": "false", "LogLevels": "Fatal, Error, Warning, Message"},
        })
        if door.exists():
            _backup(door)
            _ini_patch(door, {"UnityDoorstop": {"redirectOutputLog": "false"}}, spaced=False)
        applied.append("quiet bepinex logs")
    else:
        _restore_or_keep(bep_cfg)
        _restore_or_keep(door)

    gfx = {
        "gfx-enable-gfx-jobs": "1",
        "gfx-enable-native-gfx-jobs": "1",
        "gc-max-time-slice": "3",
    }
    if boot.parent.exists():
        _backup(boot)
        _boot_patch(boot, gfx, remove=not opts.get("gfx_jobs"))
        if opts.get("gfx_jobs"):
            applied.append("Unity gfx jobs")

    return applied


def unity_boost_args(opts: dict) -> list[str]:
    args: list[str] = []
    if opts.get("nolog"):
        args.append("-nolog")
    if opts.get("d3d11"):
        args += ["-force-d3d11", "-force-feature-level-11-0"]
    if opts.get("workers"):
        args += ["-job-worker-count", str(cpu_workers())]
    return args


def find_game_pid() -> int | None:
    if sys.platform != "win32":
        return None
    try:
        out = subprocess.run(
            ["tasklist", "/FI", f"IMAGENAME eq {GAME_EXE}", "/FO", "CSV", "/NH"],
            capture_output=True, text=True, timeout=6, creationflags=0x08000000,
        ).stdout
        for line in out.splitlines():
            parts = [p.strip().strip('"') for p in line.split(",")]
            if len(parts) >= 2 and parts[0].lower() == GAME_EXE.lower():
                return int(parts[1])
    except (OSError, ValueError, subprocess.TimeoutExpired):
        return None
    return None


def _set_priority(pid: int) -> bool:
    if sys.platform != "win32":
        return False
    PROCESS_SET_INFORMATION = 0x0200
    PROCESS_QUERY_LIMITED_INFORMATION = 0x1000
    HIGH = 0x00000080
    k32 = ctypes.windll.kernel32
    h = k32.OpenProcess(PROCESS_SET_INFORMATION | PROCESS_QUERY_LIMITED_INFORMATION, False, pid)
    if not h:
        return False
    try:
        return bool(k32.SetPriorityClass(h, HIGH))
    finally:
        k32.CloseHandle(h)


def _disable_power_throttle(pid: int) -> bool:
    if sys.platform != "win32":
        return False
    ProcessPowerThrottling = 4
    PROCESS_SET_INFORMATION = 0x0200

    class STATE(ctypes.Structure):
        _fields_ = [
            ("Version", ctypes.c_uint32),
            ("ControlMask", ctypes.c_uint32),
            ("StateMask", ctypes.c_uint32),
        ]

    st = STATE(1, 0x1, 0)  # exespeed thing w throttle
    k32 = ctypes.windll.kernel32
    h = k32.OpenProcess(PROCESS_SET_INFORMATION, False, pid)
    if not h:
        return False
    try:
        return bool(k32.SetProcessInformation(h, ProcessPowerThrottling, ctypes.byref(st), ctypes.sizeof(st)))
    except Exception:
        return False
    finally:
        k32.CloseHandle(h)


# ───────────────────────────── cool text for bg workers ─────────────────────────────
class _CheckSignals(QObject):
    done = Signal(bool)


class RunningCheck(QRunnable):
    """Is Gorilla Tag currently running? Runs off the UI thread."""

    def __init__(self):
        super().__init__()
        self.setAutoDelete(False)
        self.signals = _CheckSignals()

    def run(self):
        running = False
        try:
            if sys.platform == "win32":
                out = subprocess.run(
                    ["tasklist", "/FI", f"IMAGENAME eq {GAME_EXE}", "/NH"],
                    capture_output=True, text=True, timeout=6, creationflags=0x08000000,
                ).stdout
                running = GAME_EXE.lower() in out.lower()
            else:
                running = subprocess.run(["pgrep", "-fi", "Gorilla Tag"], capture_output=True, timeout=6).returncode == 0
        except Exception:
            running = False
        self.signals.done.emit(running)


class _BoostSignals(QObject):
    done = Signal(bool, str)


class BoostWorker(QRunnable):
    """Wait for Gorilla Tag, then pin High priority and disable EcoQoS throttling."""

    def __init__(self, high_priority: bool, no_throttle: bool):
        super().__init__()
        self.setAutoDelete(False)
        self.high_priority = high_priority
        self.no_throttle = no_throttle
        self.signals = _BoostSignals()

    def run(self):
        pid = None
        for _ in range(48):
            pid = find_game_pid()
            if pid:
                break
            time.sleep(0.75)
        if not pid:
            self.signals.done.emit(False, "game started, but horizon couldn't lock in process tweaks.")
            return
        bits = []
        if self.high_priority and _set_priority(pid):
            bits.append("high priority")
        if self.no_throttle and _disable_power_throttle(pid):
            bits.append("ecoqos off")
        if bits:
            self.signals.done.emit(True, "live boost: " + " · ".join(bits))
        else:
            self.signals.done.emit(False, "process tweaks didn't stick (try launching as administrator).")


class InstallWorker(QThread):
    """new inexbep :DDDD"""
    progress = Signal(int)
    status = Signal(str)
    done = Signal(bool, str)

    def __init__(self, game_dir: Path):
        super().__init__()
        self.game_dir = game_dir

    def run(self):
        tmp_path = None
        try:
            self.status.emit("checking github for the latest version")
            req = urllib.request.Request(
                "https://api.github.com/repos/BepInEx/BepInEx/releases?per_page=30",
                headers={"User-Agent": "HorizonLoader", "Accept": "application/vnd.github+json"},
            )
            with urllib.request.urlopen(req, timeout=25) as r:
                releases = json.load(r)
            url, tag = None, ""
            for rel in releases:
                if rel.get("prerelease") or rel.get("draft"):
                    continue
                if not str(rel.get("tag_name", "")).startswith("v5."):
                    continue
                for asset in rel.get("assets", []):
                    if re.fullmatch(r"BepInEx_(?:win_)?x64_5[\d.]*\.zip", asset.get("name", "")):
                        url, tag = asset["browser_download_url"], rel["tag_name"]
                        break
                if url:
                    break
            if not url:
                raise RuntimeError("no bepinex x64 found, wtf bepinex?")

            self.status.emit(f"downloading bepinex {tag}…")
            req = urllib.request.Request(url, headers={"User-Agent": "HorizonLoader"})
            with urllib.request.urlopen(req, timeout=60) as r, tempfile.NamedTemporaryFile(delete=False, suffix=".zip") as tmp:
                tmp_path = tmp.name
                total = int(r.headers.get("Content-Length") or 0)
                got = 0
                while True:
                    chunk = r.read(64 * 1024)
                    if not chunk:
                        break
                    tmp.write(chunk)
                    got += len(chunk)
                    if total:
                        self.progress.emit(int(got * 85 / total))

            self.status.emit("installing…")
            root = self.game_dir.resolve()
            with zipfile.ZipFile(tmp_path) as z:
                members = [m for m in z.infolist() if not m.is_dir()]
                for i, m in enumerate(members):
                    dest = (root / m.filename).resolve()
                    if not dest.is_relative_to(root):
                        continue
                    dest.parent.mkdir(parents=True, exist_ok=True)
                    with z.open(m) as src, open(dest, "wb") as dst:
                        shutil.copyfileobj(src, dst)
                    self.progress.emit(85 + int((i + 1) * 15 / max(1, len(members))))
            (root / "BepInEx" / "plugins").mkdir(parents=True, exist_ok=True)
            self.progress.emit(100)
            self.done.emit(True, f"bepinex {tag} installed. start the game once so it can finish setting up")
        except Exception as e:  # noqa: BLE001
            self.done.emit(False, f"install failed: {e}")
        finally:
            if tmp_path:
                try:
                    os.unlink(tmp_path)
                except OSError:
                    pass


# ───────────────────────────── reusable widgets ─────────────────────────────
class ToggleSwitch(QAbstractButton):
    def __init__(self, checked: bool = False):
        super().__init__()
        self.setCheckable(True)
        self.setCursor(Pointing)
        self.setFixedSize(46, 26)
        super().setChecked(checked)
        self._offset = 1.0 if checked else 0.0
        self._anim = QPropertyAnimation(self, b"offset", self)
        self._anim.setDuration(150)
        self._anim.setEasingCurve(QEasingCurve.Type.OutCubic)
        self.toggled.connect(self._on_toggled)
        TM.changed.connect(self.update)

    def _get_offset(self) -> float:
        return self._offset

    def _set_offset(self, v: float):
        self._offset = v
        self.update()

    offset = Property(float, _get_offset, _set_offset)

    def _on_toggled(self, on: bool):
        self._anim.stop()
        self._anim.setStartValue(self._offset)
        self._anim.setEndValue(1.0 if on else 0.0)
        self._anim.start()

    def set_silent(self, on: bool):
        self.blockSignals(True)
        self.setChecked(on)
        self.blockSignals(False)
        self._anim.stop()
        self._offset = 1.0 if on else 0.0
        self.update()

    def paintEvent(self, _e):
        p = QPainter(self)
        p.setRenderHint(AA)
        track = QRectF(1, 1, self.width() - 2, self.height() - 2)
        c = mix(QColor(TM.pal["subtle"]), QColor(TM.pal["accent"]), self._offset)
        p.setPen(NoPen)
        p.setBrush(c)
        p.drawRoundedRect(track, track.height() / 2, track.height() / 2)
        d = track.height() - 6
        x = track.left() + 3 + (track.width() - d - 6) * self._offset
        p.setBrush(mix(QColor("#ffffff"), QColor(TM.pal["on_accent"]), self._offset))
        p.drawEllipse(QRectF(x, track.top() + 3, d, d))


class Segmented(QWidget):
    """Exclusive pill buttons with icons. style: 'Pill' (normal) or 'HeroSeg' (on the banner)."""
    changed = Signal(str)

    def __init__(self, items, current: str, style: str = "Pill"):
        super().__init__()
        lay = QHBoxLayout(self)
        lay.setContentsMargins(0, 0, 0, 0)
        lay.setSpacing(8)
        self.group = QButtonGroup(self)
        self.group.setExclusive(True)
        self.buttons: dict[str, QPushButton] = {}
        if style == "ModeBtn":
            role = lambda w: "bg" if w.isChecked() else "text"  # noqa: E731
        else:
            role = lambda w: "accent" if w.isChecked() else "muted"  # noqa: E731
        for key, label, icon in items:
            b = QPushButton(("  " + label) if icon else label)
            b.setObjectName(style)
            b.setCheckable(True)
            b.setCursor(Pointing)
            if icon:
                TM.bind_icon(b, icon, role, 16)
            self.group.addButton(b)
            lay.addWidget(b)
            self.buttons[key] = b
            b.clicked.connect(lambda _=False, k=key: self.changed.emit(k))
        self.set_current(current)

    def set_current(self, key: str):
        b = self.buttons.get(key)
        if b:
            b.setChecked(True)


class Chip(QFrame):
    def __init__(self):
        super().__init__()
        self.setObjectName("HeroChip")
        lay = QHBoxLayout(self)
        lay.setContentsMargins(10, 5, 13, 5)
        lay.setSpacing(6)
        self.icon = QLabel()
        self.icon.setFixedSize(16, 16)
        self.label = QLabel()
        lay.addWidget(self.icon)
        lay.addWidget(self.label)

    def set_state(self, text: str, icon: str, color: str = "#ffffff"):
        self.label.setText(text)
        self.icon.setPixmap(icon_pixmap(icon, color, 16))


class StatCard(QFrame):
    def __init__(self, icon: str, label: str):
        super().__init__()
        self.setObjectName("Card")
        h = QHBoxLayout(self)
        h.setContentsMargins(16, 14, 16, 14)
        h.setSpacing(12)
        tile = QFrame()
        tile.setObjectName("IconTile")
        tile.setFixedSize(44, 44)
        tl = QVBoxLayout(tile)
        tl.setContentsMargins(0, 0, 0, 0)
        ic = QLabel()
        ic.setAlignment(AlignCenter)
        TM.bind_icon(ic, icon, "accent", 22)
        tl.addWidget(ic)
        v = QVBoxLayout()
        v.setSpacing(0)
        self.value = QLabel("–")
        self.value.setObjectName("StatValue")
        cap = QLabel(label)
        cap.setObjectName("Muted")
        v.addWidget(self.value)
        v.addWidget(cap)
        h.addWidget(tile)
        h.addLayout(v, 1)

    def set_value(self, text: str):
        self.value.setText(text)


class EmptyState(QWidget):
    action = Signal()

    def __init__(self):
        super().__init__()
        v = QVBoxLayout(self)
        v.setAlignment(AlignCenter)
        v.setSpacing(10)
        self.icon = QLabel()
        self.icon.setAlignment(AlignCenter)
        self.title = QLabel()
        self.title.setObjectName("H2")
        self.title.setAlignment(AlignCenter)
        self.text = QLabel()
        self.text.setObjectName("Muted")
        self.text.setAlignment(AlignCenter)
        self.text.setWordWrap(True)
        self.text.setMaximumWidth(440)
        self.btn = text_btn("action", "download", primary=True)
        self.btn.clicked.connect(self.action.emit)
        v.addWidget(self.icon)
        v.addWidget(self.title)
        v.addWidget(self.text, 0, AlignCenter)
        v.addSpacing(6)
        v.addWidget(self.btn, 0, AlignCenter)

    def set(self, icon: str, title: str, text: str, button: str | None = None, btn_icon: str = "download"):
        TM.bind_icon(self.icon, icon, "muted", 48)
        self.title.setText(title)
        self.text.setText(text)
        self.btn.setVisible(bool(button))
        if button:
            self.btn.setText("  " + button)
            TM.bind_icon(self.btn, btn_icon, "on_accent", 18)


class HeroBanner(QFrame):
    def __init__(self):
        super().__init__()
        self.setObjectName("Hero")
        TM.changed.connect(self.update)

    def paintEvent(self, _e):
        p = QPainter(self)
        p.setRenderHint(AA)
        r = QRectF(self.rect())
        path = QPainterPath()
        path.addRoundedRect(r, 18, 18)
        p.setClipPath(path)
        black = QColor("#000000")
        c1 = mix(QColor(TM.pal["accent"]), black, 0.50)
        c2 = mix(QColor(TM.pal["accent2"]), black, 0.74)
        g = QLinearGradient(r.topLeft(), r.bottomRight())
        g.setColorAt(0, c1)
        g.setColorAt(1, c2)
        p.fillRect(r, g)
        glow = QRadialGradient(r.right() - 130, r.top() + 30, 320)
        glow.setColorAt(0, QColor(255, 255, 255, 58))
        glow.setColorAt(1, QColor(255, 255, 255, 0))
        p.fillRect(r, glow)
        glow2 = QRadialGradient(r.left() + 80, r.bottom() - 20, 280)
        glow2.setColorAt(0, QColor(255, 255, 255, 36))
        glow2.setColorAt(1, QColor(255, 255, 255, 0))
        p.fillRect(r, glow2)
        p.setOpacity(0.16)
        p.drawPixmap(int(r.right() - 270), int(r.center().y() - 105), icon_pixmap("vr", "#ffffff", 210))
        p.setOpacity(0.08)
        p.drawPixmap(int(r.right() - 150), int(r.center().y() - 40), icon_pixmap("zap", "#ffffff", 120))


class Toast(QFrame):
    def __init__(self, parent: QWidget):
        super().__init__(parent)
        self.setObjectName("Toast")
        lay = QHBoxLayout(self)
        lay.setContentsMargins(14, 10, 18, 10)
        lay.setSpacing(10)
        self.icon = QLabel()
        self.icon.setFixedSize(20, 20)
        self.text = QLabel()
        lay.addWidget(self.icon)
        lay.addWidget(self.text)
        self.fx = QGraphicsOpacityEffect(self)
        self.setGraphicsEffect(self.fx)
        self.anim = QPropertyAnimation(self.fx, b"opacity", self)
        self.anim.setDuration(220)
        self.timer = QTimer(self)
        self.timer.setSingleShot(True)
        self.timer.timeout.connect(self._fade_out)
        self.anim.finished.connect(self._after_anim)
        self._hiding = False
        self.fx.setOpacity(0.0)
        self.hide()

    def show_message(self, text: str, kind: str = "info"):
        icon, role = {"info": ("info", "accent"), "success": ("check", "success"),
                      "error": ("alert", "danger"), "warn": ("alert", "warn")}.get(kind, ("info", "accent"))
        self.icon.setPixmap(icon_pixmap(icon, TM.resolve(role), 20))
        self.text.setText(text)
        self.adjustSize()
        par = self.parentWidget()
        self.move((par.width() - self.width()) // 2, par.height() - self.height() - 28)
        self.raise_()
        self._hiding = False
        self.show()
        self.anim.stop()
        self.anim.setStartValue(self.fx.opacity())
        self.anim.setEndValue(1.0)
        self.anim.start()
        self.timer.start(3200)

    def _fade_out(self):
        self._hiding = True
        self.anim.stop()
        self.anim.setStartValue(self.fx.opacity())
        self.anim.setEndValue(0.0)
        self.anim.start()

    def _after_anim(self):
        if self._hiding:
            self.hide()


# ───────────────────────────── window chrome ─────────────────────────────
class Root(QWidget):
    """Transparent margin around the shell that doubles as the resize border for the frameless window."""
    MARGIN = 8

    def __init__(self):
        super().__init__()
        self.setObjectName("Root")
        self.setMouseTracking(True)

    def _hit(self, pos: QPoint):
        win = self.window()
        if win.isMaximized() or win.isFullScreen():
            return None
        m = self.MARGIN + 2
        l, r = pos.x() <= m, pos.x() >= self.width() - m
        t, b = pos.y() <= m, pos.y() >= self.height() - m
        return (l, r, t, b) if (l or r or t or b) else None

    def mouseMoveEvent(self, e):
        hit = self._hit(e.position().toPoint())
        if not hit:
            self.unsetCursor()
            return
        l, r, t, b = hit
        if (l and t) or (r and b):
            shape = Qt.CursorShape.SizeFDiagCursor
        elif (r and t) or (l and b):
            shape = Qt.CursorShape.SizeBDiagCursor
        elif l or r:
            shape = Qt.CursorShape.SizeHorCursor
        else:
            shape = Qt.CursorShape.SizeVerCursor
        self.setCursor(shape)

    def mousePressEvent(self, e):
        hit = self._hit(e.position().toPoint())
        if hit and e.button() == Qt.MouseButton.LeftButton:
            l, r, t, b = hit
            edges = None
            for flag, on in ((Qt.Edge.LeftEdge, l), (Qt.Edge.RightEdge, r), (Qt.Edge.TopEdge, t), (Qt.Edge.BottomEdge, b)):
                if on:
                    edges = flag if edges is None else edges | flag
            handle = self.window().windowHandle()
            if handle and edges is not None:
                handle.startSystemResize(edges)
        super().mousePressEvent(e)


class Shell(QFrame):
    resized = Signal()

    def resizeEvent(self, e):
        super().resizeEvent(e)
        self.resized.emit()


class Scrim(QFrame):
    clicked = Signal()

    def mousePressEvent(self, _e):
        self.clicked.emit()


class TitleBtn(QPushButton):
    def __init__(self, icon: str, tip: str, danger: bool = False):
        super().__init__()
        self.setObjectName("TitleBtn")
        self.setFixedSize(32, 32)
        self.setCursor(Pointing)
        self.setToolTip(tip)
        self._danger = danger
        self.setProperty("danger", "true" if danger else "false")
        TM.bind_icon(self, icon, "text", 16)

    def enterEvent(self, e):
        # button inverts to white on hover, so flip the glyph to black
        self.setIcon(QIcon(icon_pixmap(self._icon_spec[0], TM.pal["bg"], 16)))
        super().enterEvent(e)

    def leaveEvent(self, e):
        TM.apply_icon(self)
        super().leaveEvent(e)


class TitleBar(QFrame):
    def __init__(self, win: "MainWindow"):
        super().__init__()
        self.win = win
        self.setObjectName("TitleBar")
        self.setFixedHeight(TITLEBAR_H)
        h = QHBoxLayout(self)
        h.setContentsMargins(28, 6, 24, 0)
        h.setSpacing(12)
        # the design has no theme menu or maximize button; these stay around (hidden) so the rest of the app can still talk to them
        self.menu_btn = TitleBtn("menu", "Themes & appearance")
        self.menu_btn.hide()
        self.btn_max = TitleBtn("maximize", "Maximize")
        self.btn_max.hide()
        name = QLabel("HORIZON")
        name.setObjectName("AppName")
        self.btn_min = TitleBtn("minimize", "Minimize")
        self.btn_close = TitleBtn("close", "Close", danger=True)
        self.btn_min.clicked.connect(win.showMinimized)
        self.btn_max.clicked.connect(win.toggle_maximize)
        self.btn_close.clicked.connect(win.close)
        h.addWidget(name)
        h.addStretch(1)
        h.addWidget(self.btn_min, 0, Qt.AlignmentFlag.AlignTop)
        h.addWidget(self.btn_close, 0, Qt.AlignmentFlag.AlignTop)

    def set_maximized(self, mx: bool):
        TM.bind_icon(self.btn_max, "restore" if mx else "maximize", "text", 16)

    def set_menu_open(self, is_open: bool):
        pass

    def mousePressEvent(self, e):
        if e.button() == Qt.MouseButton.LeftButton:
            h = self.window().windowHandle()
            if h:
                h.startSystemMove()
        super().mousePressEvent(e)

    def mouseDoubleClickEvent(self, e):
        if e.button() == Qt.MouseButton.LeftButton:
            self.win.toggle_maximize()


class NavButton(QPushButton):
    def __init__(self, text: str, icon: str):
        super().__init__(text)
        self.setObjectName("NavBtn")
        self.setCheckable(True)
        self.setCursor(Pointing)
        self.setFixedHeight(42)


# ───────────────────────────── theme drawer (hamburger menu) ─────────────────────────────
class Swatch(QAbstractButton):
    def __init__(self, color: str, name: str):
        super().__init__()
        self.color = QColor(color)
        self.setToolTip(name)
        self.setCheckable(True)
        self.setCursor(Pointing)
        self.setFixedSize(54, 54)
        self._hover = False

    def enterEvent(self, e):
        self._hover = True
        self.update()
        super().enterEvent(e)

    def leaveEvent(self, e):
        self._hover = False
        self.update()
        super().leaveEvent(e)

    def paintEvent(self, _e):
        p = QPainter(self)
        p.setRenderHint(AA)
        c = QRectF(self.rect()).center()
        r = 19.0
        g = QLinearGradient(c.x() - r, c.y() - r, c.x() + r, c.y() + r)
        g.setColorAt(0, self.color)
        g.setColorAt(1, shift_hue(self.color, 38) if TM.theme.gradient else self.color)
        if self.isChecked() or self._hover:
            p.setPen(QPen(QColor(TM.pal["text"] if self.isChecked() else TM.pal["muted"]), 2))
            p.setBrush(NoBrush)
            p.drawEllipse(c, r + 5, r + 5)
        p.setPen(NoPen)
        p.setBrush(g)
        p.drawEllipse(c, r, r)
        if self.isChecked():
            p.drawPixmap(int(c.x() - 11), int(c.y() - 11), icon_pixmap("check", contrast_text(self.color), 22))


class AccentPreview(QWidget):
    def __init__(self):
        super().__init__()
        self.setFixedHeight(62)
        TM.changed.connect(self.update)

    def paintEvent(self, _e):
        p = QPainter(self)
        p.setRenderHint(AA)
        r = QRectF(self.rect())
        g = QLinearGradient(r.topLeft(), r.topRight())
        g.setColorAt(0, QColor(TM.pal["accent"]))
        g.setColorAt(1, QColor(TM.pal["accent2"]))
        p.setPen(NoPen)
        p.setBrush(g)
        p.drawRoundedRect(r, 14, 14)
        p.setPen(QColor(TM.pal["on_accent"]))
        f = p.font()
        f.setBold(True)
        f.setPointSize(11)
        p.setFont(f)
        p.drawText(r, AlignCenter, TM.theme.accent.upper())


def _gradient_groove(stops: list[str]) -> str:
    n = len(stops) - 1
    s = ", ".join(f"stop:{i / n:.3f} {c}" for i, c in enumerate(stops))
    return ("QSlider::groove:horizontal { height: 8px; border-radius: 4px; "
            f"background: qlineargradient(x1:0, y1:0, x2:1, y2:0, {s}); }}")


class ThemeDrawer(QFrame):
    closeRequested = Signal()

    def __init__(self):
        super().__init__()
        self.setObjectName("Drawer")
        self.setFixedWidth(DRAWER_W)
        self._slider_hex = ""
        outer = QVBoxLayout(self)
        outer.setContentsMargins(0, 0, 0, 0)
        outer.setSpacing(0)

        head = QFrame()
        head.setObjectName("DrawerHead")
        head.setFixedHeight(58)
        hl = QHBoxLayout(head)
        hl.setContentsMargins(20, 0, 14, 0)
        ic = QLabel()
        ic.setFixedSize(22, 22)
        TM.bind_icon(ic, "palette", "accent", 20)
        title = QLabel("Themes")
        title.setObjectName("H2")
        close = icon_btn("close", "Close")
        close.clicked.connect(self.closeRequested.emit)
        hl.addWidget(ic)
        hl.addWidget(title)
        hl.addStretch(1)
        hl.addWidget(close)
        outer.addWidget(head)

        content = QWidget()
        content.setObjectName("Transparent")
        v = QVBoxLayout(content)
        v.setContentsMargins(20, 16, 20, 20)
        v.setSpacing(10)

        # presets
        v.addWidget(section_label("PRESETS"))
        grid = QGridLayout()
        grid.setSpacing(2)
        self.swatches: list[Swatch] = []
        for i, (name, color) in enumerate(PRESETS):
            sw = Swatch(color, name)
            sw.clicked.connect(lambda _=False, c=color: TM.set_accent(c))
            self.swatches.append(sw)
            grid.addWidget(sw, i // 4, i % 4)
        v.addLayout(grid)
        v.addSpacing(6)

        # custom colour
        v.addWidget(section_label("CUSTOM COLOR"))
        self.preview = AccentPreview()
        v.addWidget(self.preview)
        self.sl_h, self.sl_s, self.sl_v = QSlider(Qt.Orientation.Horizontal), QSlider(Qt.Orientation.Horizontal), QSlider(Qt.Orientation.Horizontal)
        self.sl_h.setRange(0, 359)
        self.sl_s.setRange(0, 255)
        self.sl_v.setRange(80, 255)
        for letter, sl in (("Hue", self.sl_h), ("Saturation", self.sl_s), ("Brightness", self.sl_v)):
            cap = QLabel(letter)
            cap.setObjectName("Muted")
            v.addWidget(cap)
            v.addWidget(sl)
            sl.valueChanged.connect(self._on_slider)
        self.sl_h.setStyleSheet(_gradient_groove([QColor.fromHsv(i * 60 % 360, 255, 255).name() for i in range(7)]))
        row = QHBoxLayout()
        row.setSpacing(8)
        self.hex = QLineEdit()
        self.hex.setMaxLength(7)
        self.hex.setPlaceholderText("#8b5cf6")
        self.hex.editingFinished.connect(self._on_hex)
        pick = text_btn("pick…", "wand")
        pick.setToolTip("open the full color picker")
        pick.clicked.connect(self._pick_dialog)
        row.addWidget(self.hex, 1)
        row.addWidget(pick)
        v.addLayout(row)
        v.addSpacing(6)

        # background modes
        v.addWidget(section_label("BACKGROUND"))
        self.mode_group = QButtonGroup(self)
        self.mode_group.setExclusive(True)
        self.mode_btns: dict[str, QPushButton] = {}
        for key, (label, icon) in MODES.items():
            b = QPushButton("  " + label)
            b.setObjectName("ModeCard")
            b.setCheckable(True)
            b.setCursor(Pointing)
            TM.bind_icon(b, icon, lambda w: "accent" if w.isChecked() else "muted", 18)
            b.clicked.connect(lambda _=False, k=key: TM.set_mode(k))
            self.mode_group.addButton(b)
            self.mode_btns[key] = b
            v.addWidget(b)
        v.addSpacing(6)

        # style
        v.addWidget(section_label("STYLE"))
        self.grad_switch = ToggleSwitch(TM.theme.gradient)
        self.grad_switch.toggled.connect(TM.set_gradient)
        v.addWidget(setting_row("gradient accents", "mixes a second color into buttons and banners", self.grad_switch))
        v.addSpacing(6)
        reset = text_btn("reset to default", "refresh")
        reset.clicked.connect(TM.reset)
        v.addWidget(reset)
        v.addStretch(1)

        outer.addWidget(scrolled(content), 1)
        TM.changed.connect(self.sync)
        self.sync()

    def _on_slider(self):
        c = QColor.fromHsv(self.sl_h.value(), self.sl_s.value(), self.sl_v.value())
        self._slider_hex = c.name()
        self.hex.setText(c.name())
        TM.set_accent(c.name())
        self._update_slider_styles()

    def _on_hex(self):
        t = self.hex.text().strip()
        if t and not t.startswith("#"):
            t = "#" + t
        c = QColor(t)
        if c.isValid() and len(t) == 7:
            TM.set_accent(c.name())
        else:
            self.hex.setText(TM.theme.accent)

    def _pick_dialog(self):
        c = QColorDialog.getColor(QColor(TM.theme.accent), self, "Pick an accent color")
        if c.isValid():
            TM.set_accent(c.name())

    def _update_slider_styles(self):
        h, v = self.sl_h.value(), self.sl_v.value()
        self.sl_s.setStyleSheet(_gradient_groove([QColor.fromHsv(h, 0, v).name(), QColor.fromHsv(h, 255, v).name()]))
        self.sl_v.setStyleSheet(_gradient_groove([QColor.fromHsv(h, self.sl_s.value(), 80).name(),
                                                  QColor.fromHsv(h, self.sl_s.value(), 255).name()]))

    def sync(self):
        acc = TM.theme.accent.lower()
        for sw in self.swatches:
            sw.setChecked(sw.color.name().lower() == acc)
            sw.update()
        for key, b in self.mode_btns.items():
            b.setChecked(key == TM.theme.mode)
        self.grad_switch.set_silent(TM.theme.gradient)
        if not self.hex.hasFocus():
            self.hex.setText(acc)
        if acc != self._slider_hex:
            c = QColor(acc)
            h, s, v, _ = c.getHsv()
            for sl, val in ((self.sl_h, max(h, 0)), (self.sl_s, s), (self.sl_v, max(v, 80))):
                sl.blockSignals(True)
                sl.setValue(val)
                sl.blockSignals(False)
            self._update_slider_styles()
        self.preview.update()


# ───────────────────────────── pages ─────────────────────────────
class PlayPage(QWidget):
    COL_W = 400

    def __init__(self, win: "MainWindow"):
        super().__init__()
        self.setObjectName("Transparent")
        self.win = win
        self._launching = False
        self._running = False
        root = QVBoxLayout(self)
        root.setContentsMargins(28, 6, 28, 24)
        root.setSpacing(0)

        col = QWidget()
        col.setObjectName("Transparent")
        col.setFixedWidth(self.COL_W)
        v = QVBoxLayout(col)
        v.setContentsMargins(0, 0, 0, 0)
        v.setSpacing(0)

        eyebrow = QLabel("Horizon")
        eyebrow.setObjectName("PlayEyebrow")
        eyebrow.setAlignment(AlignCenter)
        title = QLabel("Gorilla Tag")
        title.setObjectName("PlayTitle")
        title.setAlignment(AlignCenter)
        v.addWidget(eyebrow)
        v.addWidget(title)
        v.addSpacing(16)

        self.launch_btn = QPushButton("Play")
        self.launch_btn.setObjectName("PlayBtn")
        self.launch_btn.setCursor(Pointing)
        self.launch_btn.clicked.connect(win.launch_game)
        v.addWidget(self.launch_btn)
        v.addSpacing(34)

        self.mode = Segmented([("modded", "Modded", None), ("vanilla", "Vanilla", None)], win.launch_mode, style="ModeBtn")
        self.mode.setToolTip("vanilla runs the exe directly with bepinex off")
        self.mode.changed.connect(win.set_launch_mode)
        self.mode.layout().setSpacing(16)
        for btn in self.mode.buttons.values():
            btn.setSizePolicy(QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Fixed)
        v.addWidget(self.mode)
        v.addSpacing(22)

        self.status = QLabel("")
        self.status.setObjectName("PlayStatus")
        self.status.setAlignment(AlignCenter)
        self.status.setWordWrap(True)
        v.addWidget(self.status)

        root.addWidget(col, 0, Qt.AlignmentFlag.AlignHCenter | Qt.AlignmentFlag.AlignTop)
        root.addStretch(1)

    def update_state(self, found: bool, bep_ok: bool, bep_ver: str, running: bool, total: int, enabled: int, boost_label: str = "stock", boost_score: int = 0):
        bits = ["game found" if found else "game not found"]
        bits.append(f"bepinex {bep_ver}".strip() if bep_ok else "bepinex not installed")
        bits.append("running" if running else "not running")
        if boost_score > 0:
            bits.append(f"{boost_label} boost {boost_score}%")
        bits.append(f"{enabled}/{total} mods on")
        self.status.setText("  ·  ".join(bits))
        self._running = running
        self._sync_launch_button()

    def set_launching(self, on: bool):
        self._launching = on
        self._sync_launch_button()

    def _sync_launch_button(self):
        if self._running:
            self.launch_btn.setText("Running")
            self.launch_btn.setEnabled(False)
        elif self._launching:
            self.launch_btn.setText("Launching…")
            self.launch_btn.setEnabled(False)
        else:
            self.launch_btn.setText("Play")
            self.launch_btn.setEnabled(True)


class ImpactMeter(QWidget):
    def __init__(self):
        super().__init__()
        self._score = 0
        self.setFixedHeight(18)
        TM.changed.connect(self.update)

    def set_score(self, n: int):
        self._score = max(0, min(100, int(n)))
        self.update()

    def paintEvent(self, _e):
        p = QPainter(self)
        p.setRenderHint(AA)
        r = QRectF(self.rect()).adjusted(0, 4, 0, -4)
        p.setPen(NoPen)
        p.setBrush(QColor(TM.pal["subtle"]))
        p.drawRoundedRect(r, 5, 5)
        if self._score:
            fill = QRectF(r.x(), r.y(), max(10, r.width() * self._score / 100.0), r.height())
            g = QLinearGradient(fill.topLeft(), fill.topRight())
            g.setColorAt(0, QColor(TM.pal["accent"]))
            g.setColorAt(1, QColor(TM.pal["accent2"]))
            p.setBrush(g)
            p.drawRoundedRect(fill, 5, 5)


class PerformancePage(QWidget):
    OPTS = [
        ("priority", "High process priority", "makes windows treat gtag like it matters more than your other apps. easiest free fps gain tbh"),
        ("no_throttle", "Disable EcoQoS throttling", "stops windows from slowing the game down when it thinks it's running in the background"),
        ("gfx_jobs", "Unity graphics jobs", "turns on gfx jobs in boot.config so rendering uses more than one core"),
        ("workers", "Extra job threads", f"adds -job-worker-count {cpu_workers()} so unity can use pretty much all your cores"),
        ("quiet_logs", "Quiet BepInEx logging", "turns off the console + unity log mirror. logging to disk can cause lag spikes if you run a lot of mods"),
        ("nolog", "Skip Unity player log", "launches with -nolog so unity stops writing to Player.log nonstop"),
        ("d3d11", "Force Direct3D 11", "dx11 runs smoother than dx12 on this unity build for most people. max profile turns it on"),
    ]

    def __init__(self, win: "MainWindow"):
        super().__init__()
        self.setObjectName("Transparent")
        self.win = win
        self._syncing = False
        root = QVBoxLayout(self)
        root.setContentsMargins(28, 24, 28, 24)
        root.setSpacing(16)

        head = QHBoxLayout()
        tv = QVBoxLayout()
        tv.setSpacing(2)
        h1 = QLabel("Performance Boost")
        h1.setObjectName("H1")
        sub = QLabel("this actually changes the game every time you launch, it's not just a slider for show")
        sub.setObjectName("Muted")
        sub.setWordWrap(True)
        tv.addWidget(h1)
        tv.addWidget(sub)
        head.addLayout(tv, 1)
        root.addLayout(head)

        meter, ml = make_card()
        row = QHBoxLayout()
        row.setSpacing(18)
        left = QVBoxLayout()
        left.setSpacing(2)
        cap = QLabel("LAUNCH PUNCH")
        cap.setObjectName("Section")
        self.score_lbl = QLabel("0%")
        self.score_lbl.setObjectName("ImpactScore")
        self.score_hint = QLabel("stock, nothing extra applied")
        self.score_hint.setObjectName("ImpactHint")
        self.score_hint.setWordWrap(True)
        left.addWidget(cap)
        left.addWidget(self.score_lbl)
        left.addWidget(self.score_hint)
        row.addLayout(left, 1)
        right = QVBoxLayout()
        right.addStretch(1)
        self.meter = ImpactMeter()
        right.addWidget(self.meter)
        right.addStretch(1)
        row.addLayout(right, 1)
        ml.addLayout(row)
        root.addWidget(meter)

        profiles, pl = make_card()
        pl.addLayout(card_header("zap", "Profiles"))
        prow = QHBoxLayout()
        prow.setSpacing(10)
        self.profile_group = QButtonGroup(self)
        self.profile_group.setExclusive(True)
        self.profile_btns: dict[str, QPushButton] = {}
        for key in ("stock", "boost", "max"):
            title, desc = PERF_LABELS[key]
            b = QPushButton(title)
            b.setToolTip(desc)
            b.setObjectName("ProfileCard")
            b.setCheckable(True)
            b.setCursor(Pointing)
            b.setMinimumHeight(52)
            b.clicked.connect(lambda _=False, k=key: self._set_profile(k))
            self.profile_group.addButton(b)
            self.profile_btns[key] = b
            prow.addWidget(b)
        pl.addLayout(prow)
        root.addWidget(profiles)

        tweaks, tl = make_card()
        tl.addLayout(card_header("sliders", "What gets applied"))
        self.switches: dict[str, ToggleSwitch] = {}
        for i, (key, title, desc) in enumerate(self.OPTS):
            sw = ToggleSwitch(False)
            sw.toggled.connect(lambda _on=False, k=key: self._on_toggle(k))
            self.switches[key] = sw
            tl.addWidget(setting_row(title, desc, sw))
            if i < len(self.OPTS) - 1:
                tl.addWidget(divider())
        root.addWidget(tweaks)

        note, nl = make_card()
        nl.addLayout(card_header("alert", "Read this"))
        warn = QLabel(
            "boost edits the bepinex config and boot.config when you launch, then bumps the game's priority while it's open. "
            "stock puts back the backups horizon saved. close gtag before you switch profiles. "
        
        )
        warn.setObjectName("Muted")
        warn.setWordWrap(True)
        nl.addWidget(warn)
        root.addWidget(note)
        root.addStretch(1)
        self.sync()

    def _set_profile(self, key: str):
        if self._syncing:
            return
        self.win.set_perf_profile(key)

    def _on_toggle(self, key: str):
        if self._syncing:
            return
        self.win.set_perf_opt(key, self.switches[key].isChecked())

    def sync(self):
        self._syncing = True
        opts = self.win.perf_opts()
        profile = self.win.perf_profile()
        for key, b in self.profile_btns.items():
            b.setChecked(key == profile)
        for key, sw in self.switches.items():
            sw.set_silent(bool(opts.get(key)))
        score = perf_score(opts)
        name = PERF_LABELS.get(profile, PERF_LABELS["custom"])[0]
        self.score_lbl.setText(f"{score}%")
        self.meter.set_score(score)
        if score <= 0:
            self.score_hint.setText("stock. horizon leaves your game files and the process alone.")
        else:
            bits = [title for k, title, _ in self.OPTS if opts.get(k)]
            self.score_hint.setText(f"{name} profile  ·  {len(bits)} live tweaks  ·  applied on the next launch")
        self._syncing = False


class ModRow(QFrame):
    toggled = Signal(object, bool)
    delete = Signal(object)
    reveal = Signal(object)

    def __init__(self, mod: Mod):
        super().__init__()
        self.mod = mod
        self.setObjectName("ModRow")
        self.setProperty("off", "false" if mod.enabled else "true")
        h = QHBoxLayout(self)
        h.setContentsMargins(14, 12, 14, 12)
        h.setSpacing(14)
        tile = QFrame()
        tile.setObjectName("IconTile")
        tile.setFixedSize(44, 44)
        tl = QVBoxLayout(tile)
        tl.setContentsMargins(0, 0, 0, 0)
        ic = QLabel()
        ic.setAlignment(AlignCenter)
        TM.bind_icon(ic, "file", "accent", 22)
        tl.addWidget(ic)
        v = QVBoxLayout()
        v.setSpacing(2)
        self.name = QLabel(mod.name)
        self.name.setObjectName("ModName")
        self.meta = QLabel()
        self.meta.setObjectName("Muted")
        v.addWidget(self.name)
        v.addWidget(self.meta)
        self.badge = QLabel()
        self.badge.setObjectName("Badge")
        self.switch = ToggleSwitch(mod.enabled)
        self.switch.setToolTip("enable / disable this mod")
        self.switch.toggled.connect(lambda on: self.toggled.emit(self, on))
        b_reveal = icon_btn("folder", "Show in folder")
        b_reveal.clicked.connect(lambda: self.reveal.emit(self.mod))
        b_del = icon_btn("trash", "Delete mod", danger=True)
        b_del.clicked.connect(lambda: self.delete.emit(self.mod))
        h.addWidget(tile)
        h.addLayout(v, 1)
        h.addWidget(self.badge)
        h.addSpacing(4)
        h.addWidget(self.switch)
        h.addWidget(b_reveal)
        h.addWidget(b_del)
        self.refresh_state()

    def refresh_state(self):
        m = self.mod
        bits = []
        if m.version:
            bits.append(f"v{m.version}")
        bits.append(human_size(m.size))
        bits.append(format_date(m.mtime))
        if m.folder:
            bits.append(f"in {m.folder}")
        self.meta.setText("  ·  ".join(bits))
        self.badge.setText("enabled" if m.enabled else "disabled")
        self.badge.setProperty("on", "true" if m.enabled else "false")
        self.setProperty("off", "false" if m.enabled else "true")
        repolish(self.badge)
        repolish(self)
        repolish(self.name)


def format_date(ts: float) -> str:
    try:
        return datetime.fromtimestamp(ts).strftime("%b %d, %Y")
    except (OverflowError, OSError, ValueError):
        return ""


class ModsPage(QWidget):
    def __init__(self, win: "MainWindow"):
        super().__init__()
        self.win = win
        self._mods: list[Mod] = []
        self._filter = "all"
        self._empty_kind = ""
        self.setAcceptDrops(True)
        root = QVBoxLayout(self)
        root.setContentsMargins(28, 24, 28, 20)
        root.setSpacing(14)

        top = QHBoxLayout()
        tv = QVBoxLayout()
        tv.setSpacing(2)
        h1 = QLabel("Mods")
        h1.setObjectName("H1")
        self.sub = QLabel("")
        self.sub.setObjectName("Muted")
        tv.addWidget(h1)
        tv.addWidget(self.sub)
        top.addLayout(tv, 1)
        add = text_btn("add mods", "plus", primary=True)
        add.clicked.connect(self._browse)
        top.addWidget(add, 0, AlignVCenter)
        root.addLayout(top)

        bar = QHBoxLayout()
        bar.setSpacing(10)
        self.search = QLineEdit()
        self.search.setPlaceholderText("search mods…")
        act = QAction(self.search)
        self.search.addAction(act, QLineEdit.ActionPosition.LeadingPosition)
        TM.bind_icon(act, "search", "muted", 16)
        self.search.textChanged.connect(self._rebuild)
        self.seg = Segmented([("all", "all", "list"), ("on", "enabled", "check"), ("off", "disabled", "power")], "all"
                             "Shiba")
        self.seg.changed.connect(self._set_filter)
        refresh = icon_btn("refresh", "Rescan plugins (F5)")
        refresh.clicked.connect(lambda: win.refresh_all(toast=True))
        folder = icon_btn("folder", "Open plugins folder")
        folder.clicked.connect(win.open_plugins_folder)
        bar.addWidget(self.search, 1)
        bar.addWidget(self.seg)
        bar.addWidget(refresh)
        bar.addWidget(folder)
        root.addLayout(bar)

        self.drop = QFrame()
        self.drop.setObjectName("DropZone")
        self.drop.setProperty("drag", "false")
        dl = QVBoxLayout(self.drop)
        dl.setContentsMargins(4, 4, 4, 4)
        self.stack = QStackedWidget()
        self.list_widget = QWidget()
        self.list_widget.setObjectName("Transparent")
        self.list_layout = QVBoxLayout(self.list_widget)
        self.list_layout.setContentsMargins(0, 0, 8, 0)
        self.list_layout.setSpacing(8)
        self.list_layout.addStretch(1)
        self.scroll = scrolled(self.list_widget)
        self.empty = EmptyState()
        self.empty.action.connect(self._empty_action)
        self.stack.addWidget(self.scroll)
        self.stack.addWidget(self.empty)
        dl.addWidget(self.stack)
        root.addWidget(self.drop, 1)

    # ----- data -----
    def set_mods(self, mods: list[Mod]):
        self._mods = mods
        self._rebuild()

    def _set_filter(self, key: str):
        self._filter = key
        self._rebuild()

    def _rebuild(self):
        while self.list_layout.count() > 1:
            it = self.list_layout.takeAt(0)
            w = it.widget()
            if w:
                w.setParent(None)
                w.deleteLater()
        q = self.search.text().strip().lower()
        shown = [m for m in self._mods
                 if (not q or q in m.name.lower() or q in m.folder.lower())
                 and (self._filter == "all" or (self._filter == "on") == m.enabled)]
        enabled = sum(m.enabled for m in self._mods)
        self.sub.setText(f"{len(self._mods)} installed  ·  {enabled} enabled" if self._mods else "no mods installed")

        if not self.win.game_dir:
            self._empty_kind = "settings"
            self.empty.set("alert", "Gorilla Tag not found", "tell horizon where your game folder is", "open settings", "sliders")
            self.stack.setCurrentWidget(self.empty)
            return
        if not self.win.bepinex_status()[0]:
            self._empty_kind = "install"
            self.empty.set("shield", "BepInEx isn't installed", "bepinex is what gtag mods run on. install it with one click, then drop your mods in", "install bepinex", "download")
            self.stack.setCurrentWidget(self.empty)
            return
        if not self._mods:
            self._empty_kind = ""
            self.empty.set("box", "No mods yet", "drag .dll or .zip mods onto this page, or hit “Add mods”")
            self.stack.setCurrentWidget(self.empty)
            return
        if not shown:
            self._empty_kind = ""
            self.empty.set("search", "Nothing matches", "try a different search or filter")
            self.stack.setCurrentWidget(self.empty)
            return
        for m in shown:
            row = ModRow(m)
            row.toggled.connect(self._on_toggle)
            row.delete.connect(self._on_delete)
            row.reveal.connect(lambda mod: reveal_path(mod.path))
            self.list_layout.insertWidget(self.list_layout.count() - 1, row)
        self.stack.setCurrentWidget(self.scroll)

    # ----- actions -----
    def _on_toggle(self, row: ModRow, on: bool):
        mod = row.mod
        new = mod.path.with_name(mod.name + (".dll" if on else ".dll.disabled"))
        try:
            if new.exists():
                raise OSError(f"{new.name} already exists")
            mod.path.rename(new)
            mod.path, mod.enabled = new, on
            row.refresh_state()
            self.win.update_overview()
            self.sub.setText(f"{len(self._mods)} installed  ·  {sum(m.enabled for m in self._mods)} enabled")
        except OSError as e:
            row.switch.set_silent(mod.enabled)
            self.win.toast(f"couldn't change {mod.name}: {e}", "error")

    def _on_delete(self, mod: Mod):
        if self.win.confirm("Delete mod?", f"“{mod.name}” will be permanently removed from your plugins folder.".lower(), "delete"):
            try:
                mod.path.unlink()
                self.win.toast(f"deleted {mod.name}", "success")
            except OSError as e:
                self.win.toast(f"couldn't delete: {e}", "error")
            self.win.refresh_mods()

    def _browse(self):
        if not self.win.game_dir:
            self.win.toast("set your game folder first", "error")
            self.win.goto(self.win.PAGE_SETTINGS)
            return
        files, _ = QFileDialog.getOpenFileNames(self, "Add mods", "", "Mods (*.dll *.zip)")
        if files:
            self.win.install_mod_files(files)

    def _empty_action(self):
        if self._empty_kind == "install":
            self.win.install_bepinex()
        elif self._empty_kind == "settings":
            self.win.goto(self.win.PAGE_SETTINGS)

    # ----- drag & drop -----
    def _set_drag(self, on: bool):
        self.drop.setProperty("drag", "true" if on else "false")
        repolish(self.drop)

    def dragEnterEvent(self, e):
        md = e.mimeData()
        if md.hasUrls() and any(u.toLocalFile().lower().endswith((".dll", ".zip")) for u in md.urls()):
            e.acceptProposedAction()
            self._set_drag(True)

    def dragLeaveEvent(self, _e):
        self._set_drag(False)

    def dropEvent(self, e):
        self._set_drag(False)
        self.win.install_mod_files([u.toLocalFile() for u in e.mimeData().urls() if u.isLocalFile()])


class LogsPage(QWidget):
    COLORS = {"fatal": "danger", "error": "danger", "warning": "warn", "debug": "muted", "message": "accent", "info": "text"}

    def __init__(self, win: "MainWindow"):
        super().__init__()
        self.win = win
        self._sig = None
        root = QVBoxLayout(self)
        root.setContentsMargins(28, 24, 28, 20)
        root.setSpacing(14)
        top = QHBoxLayout()
        tv = QVBoxLayout()
        tv.setSpacing(2)
        h1 = QLabel("BepInEx log")
        h1.setObjectName("H1")
        self.sub = QLabel("")
        self.sub.setObjectName("Muted")
        tv.addWidget(h1)
        tv.addWidget(self.sub)
        top.addLayout(tv, 1)
        live_lbl = QLabel("live")
        live_lbl.setObjectName("RowTitle")
        self.live = ToggleSwitch(True)
        top.addWidget(live_lbl, 0, AlignVCenter)
        top.addWidget(self.live, 0, AlignVCenter)
        root.addLayout(top)

        bar = QHBoxLayout()
        bar.setSpacing(10)
        self.filter = QLineEdit()
        self.filter.setPlaceholderText("filter log lines…")
        act = QAction(self.filter)
        self.filter.addAction(act, QLineEdit.ActionPosition.LeadingPosition)
        TM.bind_icon(act, "search", "muted", 16)
        self.filter.textChanged.connect(lambda _t: self.refresh(force=True))
        copy = icon_btn("copy", "Copy visible log")
        copy.clicked.connect(self._copy)
        openf = icon_btn("external", "Open log file")
        openf.clicked.connect(self._open)
        refresh = icon_btn("refresh", "Reload")
        refresh.clicked.connect(lambda: self.refresh(force=True))
        bar.addWidget(self.filter, 1)
        bar.addWidget(refresh)
        bar.addWidget(copy)
        bar.addWidget(openf)
        root.addLayout(bar)

        self.stack = QStackedWidget()
        self.view = QTextEdit()
        self.view.setObjectName("LogView")
        self.view.setReadOnly(True)
        self.view.setLineWrapMode(QTextEdit.LineWrapMode.NoWrap)
        self.empty = EmptyState()
        self.stack.addWidget(self.view)
        self.stack.addWidget(self.empty)
        root.addWidget(self.stack, 1)

    def refresh(self, force: bool = False):
        path = self.win.log_path()
        if not path or not path.exists():
            self.sub.setText("no log file yet")
            self.empty.set("terminal", "No log yet", "launch gtag with bepinex installed and the log shows up here live")
            self.stack.setCurrentWidget(self.empty)
            self._sig = None
            return
        try:
            st = path.stat()
            sig = (st.st_size, st.st_mtime_ns)
            if sig == self._sig and not force:
                return
            text = path.read_text(encoding="utf-8", errors="replace")
        except OSError as e:
            self.sub.setText(f"couldn't read log: {e}")
            return
        self._sig = sig
        lines = text.splitlines()[-2000:]
        q = self.filter.text().strip().lower()
        pat = re.compile(r"^\[(fatal|error|warning|debug|message|info)", re.I)
        out = []
        for ln in lines:
            if q and q not in ln.lower():
                continue
            m = pat.match(ln)
            role = self.COLORS.get(m.group(1).lower(), "text") if m else "muted"
            out.append(f'<div style="color:{TM.resolve(role)}; white-space:pre-wrap;">{escape(ln) or "&nbsp;"}</div>')
        sb = self.view.verticalScrollBar()
        at_bottom = sb.value() >= sb.maximum() - 6
        self.view.setHtml("".join(out))
        if at_bottom or force:
            sb.setValue(sb.maximum())
        self.sub.setText(f"{path.name}  ·  {len(lines)} lines  ·  {human_size(st.st_size)}")
        self.stack.setCurrentWidget(self.view)

    def _copy(self):
        QApplication.clipboard().setText(self.view.toPlainText())
        self.win.toast("log copied to clipboard", "success")

    def _open(self):
        p = self.win.log_path()
        if p and p.exists():
            open_path(p)
        else:
            self.win.toast("no log file yet", "warn")


class SettingsPage(QWidget):
    def __init__(self, win: "MainWindow"):
        super().__init__()
        self.setObjectName("Transparent")
        self.win = win
        root = QVBoxLayout(self)
        root.setContentsMargins(28, 24, 28, 24)
        root.setSpacing(16)
        h1 = QLabel("Settings")
        h1.setObjectName("H1")
        root.addWidget(h1)

        # game card
        gc, gl = make_card()
        gl.addLayout(card_header("gamepad", "Game"))
        prow = QHBoxLayout()
        prow.setSpacing(8)
        self.path = QLineEdit()
        self.path.setPlaceholderText("folder with Gorilla Tag.exe in it")
        self.path.editingFinished.connect(lambda: win.set_game_dir(self.path.text()))
        browse = text_btn("browse", "folder")
        browse.clicked.connect(self._browse)
        detect = text_btn("auto-detect", "search")
        detect.clicked.connect(win.detect_game)
        prow.addWidget(self.path, 1)
        prow.addWidget(browse)
        prow.addWidget(detect)
        gl.addLayout(prow)
        self.path_status = QLabel("")
        self.path_status.setObjectName("Muted")
        gl.addWidget(self.path_status)
        gl.addWidget(divider())
        self.method = Segmented([("steam", "steam", "gamepad"), ("direct", "direct exe", "terminal")], win.settings.value("game/method", "steam"))
        self.method.changed.connect(lambda k: win.settings.setValue("game/method", k))
        gl.addWidget(setting_row("launch method", "steam is the safe pick. direct runs the exe itself (vanilla always uses this)", self.method))
        self.args = QLineEdit(str(win.settings.value("game/args", "")))
        self.args.setPlaceholderText("e.g. -screen-fullscreen 0")
        self.args.setMinimumWidth(260)
        self.args.editingFinished.connect(lambda: win.settings.setValue("game/args", self.args.text()))
        gl.addWidget(setting_row("launch arguments", "extra launch args", self.args))
        self.close_sw = ToggleSwitch(win.settings.value("game/close", False, type=bool))
        self.close_sw.toggled.connect(lambda on: win.settings.setValue("game/close", on))
        gl.addWidget(setting_row("close horizon after launching", "shuts horizon once the game is up", self.close_sw))
        root.addWidget(gc)

        # bepinex card
        bc, bl = make_card()
        bl.addLayout(card_header("shield", "BepInEx"))
        self.bep_status = QLabel("")
        self.bep_status.setObjectName("Muted")
        self.bep_status.setWordWrap(True)
        bl.addWidget(self.bep_status)
        self.progress = QProgressBar()
        self.progress.setRange(0, 100)
        self.progress.setTextVisible(False)
        self.progress.hide()
        self.progress_lbl = QLabel("")
        self.progress_lbl.setObjectName("Muted")
        self.progress_lbl.hide()
        bl.addWidget(self.progress)
        bl.addWidget(self.progress_lbl)
        brow = QHBoxLayout()
        brow.setSpacing(10)
        self.install_btn = text_btn("install / update bepinex", "download", primary=True)
        self.install_btn.clicked.connect(win.install_bepinex)
        cfg = text_btn("config folder", "sliders")
        cfg.clicked.connect(win.open_config_folder)
        brow.addWidget(self.install_btn)
        brow.addWidget(cfg)
        brow.addStretch(1)
        bl.addLayout(brow)
        root.addWidget(bc)

        # folders + utilities (these used to live in the Play page's quick actions)
        fc, fl = make_card()
        fl.addLayout(card_header("folder", "Folders"))
        frow = QHBoxLayout()
        frow.setSpacing(10)
        for icon, label, cb in (
            ("folder", "game folder", win.open_game_folder),
            ("box", "plugins", win.open_plugins_folder),
            ("refresh", "rescan mods", lambda: win.refresh_all(True)),
        ):
            fb = text_btn(label, icon)
            fb.clicked.connect(lambda _=False, cb=cb: cb())
            frow.addWidget(fb)
        frow.addStretch(1)
        fl.addLayout(frow)
        root.addWidget(fc)
        root.addStretch(1)

    def _browse(self):
        d = QFileDialog.getExistingDirectory(self, "Select your Gorilla Tag folder", self.path.text() or "")
        if d:
            self.win.set_game_dir(d)

    def update_state(self, game_dir: Path | None, bep_ok: bool, bep_ver: str):
        self.path.setText(str(game_dir) if game_dir else self.path.text())
        if game_dir:
            self.path_status.setText(f"✓ found {GAME_EXE}")
        else:
            self.path_status.setText("couldn't find gorilla tag on its own. hit browse and pick the folder with Gorilla Tag.exe")
        self.bep_status.setText(
            f"bepinex {bep_ver} is installed. your mods go in bepinex/plugins." if bep_ok
            else "bepinex isn't in your game folder yet. installing grabs the latest BepInEx 5 (x64) straight from their github."
        )

    def begin_install(self):
        self.install_btn.setEnabled(False)
        self.progress.setValue(0)
        self.progress.show()
        self.progress_lbl.show()

    def set_progress(self, v: int):
        self.progress.setValue(v)

    def set_install_status(self, s: str):
        self.progress_lbl.setText(s)

    def end_install(self):
        self.install_btn.setEnabled(True)
        QTimer.singleShot(1800, lambda: (self.progress.hide(), self.progress_lbl.hide()))


class AboutPage(QWidget):
    def __init__(self):
        super().__init__()
        self.setObjectName("Transparent")
        root = QVBoxLayout(self)
        root.setContentsMargins(28, 24, 28, 24)
        root.setSpacing(16)
        c, v = make_card()
        v.setContentsMargins(28, 26, 28, 26)
        top = QHBoxLayout()
        top.setSpacing(16)
        tile = QFrame()
        tile.setObjectName("IconTile")
        tile.setFixedSize(68, 68)
        tl = QVBoxLayout(tile)
        tl.setContentsMargins(0, 0, 0, 0)
        ic = QLabel()
        ic.setAlignment(AlignCenter)
        TM.bind_icon(ic, "zap", "accent", 36)
        tl.addWidget(ic)
        tv = QVBoxLayout()
        tv.setSpacing(2)
        name = QLabel(APP_NAME)
        name.setObjectName("H1")
        ver = QLabel(f"v{APP_VERSION} - made by @._person_.")
        ver.setObjectName("Muted")
        tv.addWidget(name)
        tv.addWidget(ver)
        top.addWidget(tile)
        top.addLayout(tv, 1)
        v.addLayout(top)
        v.addWidget(divider())
        for icon, text in (
            ("box", "a bepinex mod list, you can turn mods off without deleting them"),
            ("download", "one click bepinex installer, pulls from the official github"),
            ("terminal", "a color coded bepinex log you can watch live"),
            ("gamepad", "launch through steam or the exe, with or without mods"),
            ("zap", "launch boost that edits the unity + bepinex files and bumps priority"),
        ):
            row = QHBoxLayout()
            row.setSpacing(12)
            i = QLabel()
            i.setFixedSize(20, 20)
            TM.bind_icon(i, icon, "accent", 18)
            t = QLabel(text)
            row.addWidget(i)
            row.addWidget(t, 1)
            v.addLayout(row)
        root.addWidget(c)
        dc, dl = make_card()
        dl.addLayout(card_header("info", "GTK"))
        note = QLabel("horizon was made by ._person_. on discord and idk lemming. "
                      "mods can crash or break after updates. i support modding so i wouldn't do this. "
                       "Shiba GT is a rat")
        note.setObjectName("Muted")
        note.setWordWrap(True)
        dl.addWidget(note)
        root.addWidget(dc)
        root.addStretch(1)


# ───────────────────────────── main window ─────────────────────────────
class MainWindow(QMainWindow):
    PAGE_PLAY, PAGE_MODS, PAGE_PERF, PAGE_LOGS, PAGE_SETTINGS, PAGE_ABOUT = range(6)
    NAV = [("LaunchPad", "play"), ("Mods", "box"), ("Boost", "zap"), ("Logs", "terminal"), ("Settings", "sliders"), ("Info", "info")]

    def __init__(self):
        super().__init__()
        self.settings = TM.settings
        self.game_dir: Path | None = None
        self.mods: list[Mod] = []
        self.launch_mode = str(self.settings.value("launch/mode", "modded"))
        self._running = False
        self._drawer_t = 0.0
        self._installer: InstallWorker | None = None
        self._check: RunningCheck | None = None
        self._boost: BoostWorker | None = None

        self.setWindowFlags(Qt.WindowType.FramelessWindowHint | Qt.WindowType.Window)
        self.setAttribute(Qt.WidgetAttribute.WA_TranslucentBackground)
        self.setWindowTitle(APP_NAME)
        self.resize(1140, 740)
        self.setMinimumSize(1000, 660)

        root = Root()
        self.setCentralWidget(root)
        self.root_layout = QVBoxLayout(root)
        self.root_layout.setContentsMargins(8, 8, 8, 8)
        self.shell = Shell()
        self.shell.setObjectName("Shell")
        self.shell.setCursor(Qt.CursorShape.ArrowCursor)
        self.root_layout.addWidget(self.shell)
        sl = QVBoxLayout(self.shell)
        sl.setContentsMargins(0, 0, 0, 0)
        sl.setSpacing(0)
        self.titlebar = TitleBar(self)
        sl.addWidget(self.titlebar)
        body = QHBoxLayout()
        body.setSpacing(0)
        sl.addLayout(body, 1)
        body.addWidget(self._build_sidebar())

        self.stack = QStackedWidget()
        self.play_page = PlayPage(self)
        self.perf_page = PerformancePage(self)
        self.mods_page = ModsPage(self)
        self.logs_page = LogsPage(self)
        self.settings_page = SettingsPage(self)
        self.about_page = AboutPage()
        self.stack.addWidget(scrolled(self.play_page))
        self.stack.addWidget(self.mods_page)
        self.stack.addWidget(scrolled(self.perf_page))
        self.stack.addWidget(self.logs_page)
        self.stack.addWidget(scrolled(self.settings_page))
        self.stack.addWidget(scrolled(self.about_page))
        body.addWidget(self.stack, 1)

        # overlays (theme drawer + toast)
        self.scrim = Scrim(self.shell)
        self.scrim.setObjectName("Scrim")
        self.scrim_fx = QGraphicsOpacityEffect(self.scrim)
        self.scrim.setGraphicsEffect(self.scrim_fx)
        self.scrim.clicked.connect(self.close_drawer)
        self.drawer = ThemeDrawer()
        self.drawer.setParent(self.shell)
        self.drawer.closeRequested.connect(self.close_drawer)
        self.scrim.hide()
        self.drawer.hide()
        self.toast_w = Toast(self.shell)
        self.shell.resized.connect(self._place_overlays)
        self._drawer_anim = QVariantAnimation(self)
        self._drawer_anim.setDuration(240)
        self._drawer_anim.setEasingCurve(QEasingCurve.Type.OutCubic)
        self._drawer_anim.valueChanged.connect(self._set_drawer_t)
        self._drawer_anim.finished.connect(self._drawer_anim_done)

        # timers & shortcuts
        self.log_timer = QTimer(self)
        self.log_timer.timeout.connect(self._tick_logs)
        self.log_timer.start(1500)
        self.run_timer = QTimer(self)
        self.run_timer.timeout.connect(self.poll_running)
        self.run_timer.start(4000)
        QShortcut(QKeySequence("F5"), self, activated=lambda: self.refresh_all(toast=True))
        QShortcut(QKeySequence("Escape"), self, activated=self.close_drawer)

        TM.changed.connect(self._refresh_side_status)
        self._apply_window_state()
        self.resolve_game_dir()
        self.refresh_all()
        self.goto(self.PAGE_PLAY)
        self.poll_running()

    # ----- sidebar -----
    def _build_sidebar(self) -> QFrame:
        sb = QFrame()
        sb.setObjectName("Sidebar")
        sb.setFixedWidth(236)
        v = QVBoxLayout(sb)
        v.setContentsMargins(28, 26, 10, 28)
        v.setSpacing(14)
        self.nav_group = QButtonGroup(self)
        self.nav_group.setExclusive(True)
        self.nav_buttons: list[NavButton] = []
        for i, (label, icon) in enumerate(self.NAV):
            b = NavButton(label, icon)
            self.nav_group.addButton(b, i)
            b.clicked.connect(lambda _=False, i=i: self.goto(i))
            self.nav_buttons.append(b)
            v.addWidget(b)
        v.addStretch(1)
        return sb

    def _refresh_side_status(self):
        pass  # the sidebar no longer has a status card; the Play page shows it instead

    def goto(self, i: int):
        self.stack.setCurrentIndex(i)
        self.nav_buttons[i].setChecked(True)
        if i == self.PAGE_PERF:
            self.perf_page.sync()
        elif i == self.PAGE_MODS:
            self.refresh_mods()
        elif i == self.PAGE_LOGS:
            self.logs_page.refresh(force=True)
        elif i == self.PAGE_SETTINGS:
            self.update_overview()

    def _tick_logs(self):
        if self.stack.currentIndex() == self.PAGE_LOGS and self.logs_page.live.isChecked():
            self.logs_page.refresh()

    # ----- window state -----
    def toggle_maximize(self):
        self.showNormal() if self.isMaximized() else self.showMaximized()

    def changeEvent(self, e):
        if e.type() == QEvent.Type.WindowStateChange and hasattr(self, "titlebar"):
            self._apply_window_state()
        super().changeEvent(e)

    def _apply_window_state(self):
        mx = self.isMaximized()
        m = 0 if mx else 8
        self.root_layout.setContentsMargins(m, m, m, m)
        self.shell.setProperty("max", "true" if mx else "false")
        repolish(self.shell)
        self.titlebar.set_maximized(mx)

    # ----- theme drawer -----
    def _overlay_rect(self) -> QRect:
        y0 = TITLEBAR_H + 1
        return QRect(1, y0, max(0, self.shell.width() - 2), max(0, self.shell.height() - y0 - 1))

    def _set_drawer_t(self, t):
        self._drawer_t = float(t)
        r = self._overlay_rect()
        self.scrim.setGeometry(r)
        self.scrim_fx.setOpacity(self._drawer_t)
        self.drawer.setGeometry(r.x() - int(DRAWER_W * (1 - self._drawer_t)), r.y(), DRAWER_W, r.height())
        self.scrim.raise_()
        self.drawer.raise_()
        self.toast_w.raise_()

    def _place_overlays(self):
        if self.drawer.isVisible():
            self._set_drawer_t(self._drawer_t)

    def open_drawer(self):
        if self._drawer_t >= 1.0 and self.drawer.isVisible():
            return
        self.drawer.sync()
        self.scrim.show()
        self.drawer.show()
        self.titlebar.set_menu_open(True)
        self._drawer_anim.stop()
        self._drawer_anim.setStartValue(self._drawer_t)
        self._drawer_anim.setEndValue(1.0)
        self._drawer_anim.start()

    def close_drawer(self):
        if not self.drawer.isVisible():
            return
        self.titlebar.set_menu_open(False)
        self._drawer_anim.stop()
        self._drawer_anim.setStartValue(self._drawer_t)
        self._drawer_anim.setEndValue(0.0)
        self._drawer_anim.start()

    def toggle_drawer(self):
        if self.drawer.isVisible() and self._drawer_anim.endValue() != 0.0:
            self.close_drawer()
        else:
            self.open_drawer()

    def _drawer_anim_done(self):
        if self._drawer_t <= 0.001:
            self.scrim.hide()
            self.drawer.hide()

    # ----- game / mods state -----
    @property
    def plugins_dir(self) -> Path | None:
        return self.game_dir / "BepInEx" / "plugins" if self.game_dir else None

    def log_path(self) -> Path | None:
        return self.game_dir / "BepInEx" / "LogOutput.log" if self.game_dir else None

    def bepinex_status(self) -> tuple[bool, str]:
        if not self.game_dir:
            return False, ""
        core = self.game_dir / "BepInEx" / "core" / "BepInEx.dll"
        ok = core.exists() and (self.game_dir / "winhttp.dll").exists()
        return ok, (file_version(core) if ok else "")

    def resolve_game_dir(self):
        saved = str(self.settings.value("game/path", "") or "")
        if saved and (Path(saved) / GAME_EXE).exists():
            self.game_dir = Path(saved)
            return
        found = detect_game_dir()
        if found:
            self.game_dir = found
            self.settings.setValue("game/path", str(found))

    def detect_game(self):
        found = detect_game_dir()
        if found:
            self.set_game_dir(found)
            self.toast("found gorilla tag!", "success")
        else:
            self.toast("couldn't find gorilla tag on its own, try browse", "warn")

    def set_game_dir(self, path) -> bool:
        text = str(path or "").strip().strip('"')
        if not text:
            return False
        p = Path(text)
        if p.is_file():
            p = p.parent
        if not (p / GAME_EXE).exists():
            self.toast(f"{GAME_EXE} isn't in that folder", "error")
            self.settings_page.update_state(self.game_dir, *self.bepinex_status())
            return False
        self.game_dir = p
        self.settings.setValue("game/path", str(p))
        self.refresh_all()
        return True

    def refresh_mods(self):
        plugins = self.plugins_dir
        self.mods = scan_mods(plugins) if plugins else []
        self.mods_page.set_mods(self.mods)
        self.update_overview()

    def perf_profile(self) -> str:
        p = str(self.settings.value("perf/profile", "max"))
        return p if p in (*PERF_PROFILES, "custom") else "max"

    def perf_opts(self) -> dict:
        profile = self.perf_profile()
        if profile in PERF_PROFILES:
            return dict(PERF_PROFILES[profile])
        return {k: self.settings.value(f"perf/{k}", False, type=bool) for k in PERF_WEIGHTS}

    def set_perf_profile(self, key: str):
        self.settings.setValue("perf/profile", key)
        if key in PERF_PROFILES:
            for k, v in PERF_PROFILES[key].items():
                self.settings.setValue(f"perf/{k}", v)
        self.perf_page.sync()
        self.update_overview()

    def set_perf_opt(self, key: str, on: bool):
        self.settings.setValue(f"perf/{key}", bool(on))
        self.settings.setValue("perf/profile", "custom")
        self.perf_page.sync()
        self.update_overview()

    def _arm_live_boost(self, high_priority: bool, no_throttle: bool):
        w = BoostWorker(high_priority, no_throttle)
        self._boost = w
        w.signals.done.connect(self._on_live_boost)
        QThreadPool.globalInstance().start(w)

    def _on_live_boost(self, ok: bool, msg: str):
        self.toast(msg, "success" if ok else "warn")

    def update_overview(self):
        bep_ok, bep_ver = self.bepinex_status()
        enabled = sum(m.enabled for m in self.mods)
        profile = self.perf_profile()
        opts = self.perf_opts()
        self.play_page.update_state(
            bool(self.game_dir), bep_ok, bep_ver, self._running, len(self.mods), enabled,
            PERF_LABELS.get(profile, PERF_LABELS["custom"])[0], perf_score(opts),
        )
        self.settings_page.update_state(self.game_dir, bep_ok, bep_ver)
        self._refresh_side_status()

    def refresh_all(self, toast: bool = False):
        self.refresh_mods()
        self.logs_page.refresh(force=True)
        if toast:
            self.toast(f"rescanned: {len(self.mods)} mod(s) found", "success")

    # ----- mod installs -----
    def install_mod_files(self, paths: list[str]):
        if not self.game_dir:
            self.toast("set your game folder first", "error")
            return
        plugins = self.plugins_dir
        added = 0
        try:
            plugins.mkdir(parents=True, exist_ok=True)
        except OSError as e:
            self.toast(f"can't create plugins folder: {e}", "error")
            return
        for raw in paths:
            p = Path(raw)
            try:
                if p.suffix.lower() == ".dll":
                    shutil.copy2(p, plugins / p.name)
                    added += 1
                elif p.suffix.lower() == ".zip":
                    added += self._extract_mod_zip(p, plugins)
            except (OSError, zipfile.BadZipFile) as e:
                self.toast(f"couldn't install {p.name}: {e}", "error")
        if added:
            self.refresh_mods()
            self.toast(f"installed {added} mod file(s)", "success")
        elif paths:
            self.toast("no mod files were installed", "warn")

    @staticmethod
    def _extract_mod_zip(zp: Path, plugins: Path) -> int:
        count = 0
        root = plugins.resolve()
        with zipfile.ZipFile(zp) as z:
            infos = [i for i in z.infolist() if not i.is_dir()]
            norm = {i.filename: i.filename.replace("\\", "/") for i in infos}
            structured = any(re.search(r"(?:^|/)plugins/", n, re.I) for n in norm.values())
            for info in infos:
                n = norm[info.filename]
                m = re.search(r"(?:^|/)plugins/(.+)$", n, re.I)
                if m:
                    rel = m.group(1)
                elif structured:
                    continue
                else:
                    rel = f"{zp.stem}/{n}"
                dest = (root / rel).resolve()
                if not dest.is_relative_to(root):
                    continue
                dest.parent.mkdir(parents=True, exist_ok=True)
                with z.open(info) as src, open(dest, "wb") as dst:
                    shutil.copyfileobj(src, dst)
                if rel.lower().endswith(".dll"):
                    count += 1
        return count

    # ----- BepInEx installer -----
    def install_bepinex(self):
        if not self.game_dir:
            self.toast("pick your gorilla tag folder first", "error")
            self.goto(self.PAGE_SETTINGS)
            return
        if self._running:
            self.toast("close gorilla tag first", "warn")
            return
        if self._installer and self._installer.isRunning():
            return
        self.goto(self.PAGE_SETTINGS)
        w = InstallWorker(self.game_dir)
        self._installer = w
        w.progress.connect(self.settings_page.set_progress)
        w.status.connect(self.settings_page.set_install_status)
        w.done.connect(self._on_install_done)
        self.settings_page.begin_install()
        w.start()

    def _on_install_done(self, ok: bool, msg: str):
        self.settings_page.end_install()
        self.toast(msg, "success" if ok else "error")
        self.refresh_all()

    # ----- launching -----
    def set_launch_mode(self, key: str):
        self.launch_mode = key
        self.settings.setValue("launch/mode", key)

    def launch_game(self):
        if not self.game_dir:
            self.toast("set your gorilla tag folder first", "error")
            self.goto(self.PAGE_SETTINGS)
            return
        if self._running:
            self.toast("gtag is already running", "warn")
            return
        vanilla = self.launch_mode == "vanilla"
        method = "direct" if vanilla else str(self.settings.value("game/method", "steam"))
        opts = self.perf_opts()
        boost_args = unity_boost_args(opts)
        applied: list[str] = []
        if self.game_dir and any(opts.values()):
            try:
                applied = apply_performance_files(self.game_dir, opts)
            except OSError as e:
                self.toast(f"couldn't write boost files: {e}", "error")
        elif self.game_dir:
            try:
                apply_performance_files(self.game_dir, opts)
            except OSError:
                pass
        try:
            extra = shlex.split(str(self.settings.value("game/args", "") or ""), posix=(os.name != "nt"))
            if method == "steam":
                steam_bits = extra + boost_args
                if steam_bits:
                    packed = urllib.parse.quote(" ".join(steam_bits))
                    QDesktopServices.openUrl(QUrl(f"steam://run/{STEAM_APP_ID}//{packed}"))
                else:
                    QDesktopServices.openUrl(QUrl(f"steam://rungameid/{STEAM_APP_ID}"))
            else:
                env = os.environ.copy()
                args = extra + boost_args
                if vanilla:
                    env["DOORSTOP_DISABLE"] = "1"
                    args += ["--doorstop-enabled", "false"]
                kwargs = {"creationflags": 0x00000008 | 0x00000200} if sys.platform == "win32" else {}
                subprocess.Popen([str(self.game_dir / GAME_EXE), *args], cwd=str(self.game_dir), env=env, **kwargs)
        except (OSError, ValueError) as e:
            self.toast(f"couldn't launch: {e}", "error")
            return
        mode = "vanilla" if vanilla else "modded"
        punch = perf_score(opts)
        if punch:
            self.toast(f"launching {mode} at {punch}% punch" + (f" ({', '.join(applied)})" if applied else "") + "…", "success")
        else:
            self.toast(f"launching gorilla tag ({mode})…", "success")
        self.play_page.set_launching(True)
        QTimer.singleShot(9000, lambda: self.play_page.set_launching(False))
        if opts.get("priority") or opts.get("no_throttle"):
            self._arm_live_boost(bool(opts.get("priority")), bool(opts.get("no_throttle")))
        if self.settings.value("game/close", False, type=bool):
            QTimer.singleShot(2200, self.close)

    def poll_running(self):
        if self._check is not None:
            return
        chk = RunningCheck()
        self._check = chk
        chk.signals.done.connect(self._on_running)
        QThreadPool.globalInstance().start(chk)

    def _on_running(self, running: bool):
        self._check = None
        changed = running != self._running
        self._running = running
        if running:
            self.play_page.set_launching(False)
        if changed:
            self.update_overview()

    # ----- misc helpers -----
    def open_game_folder(self):
        if self.game_dir:
            open_path(self.game_dir)
        else:
            self.toast("game folder not set", "warn")

    def open_plugins_folder(self):
        p = self.plugins_dir
        if not p:
            self.toast("game folder not set", "warn")
            return
        p.mkdir(parents=True, exist_ok=True)
        open_path(p)

    def open_config_folder(self):
        if not self.game_dir:
            self.toast("game folder not set", "warn")
            return
        p = self.game_dir / "BepInEx" / "config"
        if p.exists():
            open_path(p)
        else:
            self.toast("no config found, try installing/repairing bepinex", "warn")

    def toast(self, text: str, kind: str = "info"):
        self.toast_w.show_message(text, kind)

    def confirm(self, title: str, text: str, yes: str = "ok") -> bool:
        box = QMessageBox(self)
        box.setWindowTitle(title)
        box.setText(f"<b>{escape(title)}</b>")
        box.setInformativeText(text)
        box.setIconPixmap(icon_pixmap("trash", TM.resolve("danger"), 40))
        ok = box.addButton(yes, QMessageBox.ButtonRole.AcceptRole)
        box.addButton("cancel", QMessageBox.ButtonRole.RejectRole)
        box.exec()
        return box.clickedButton() == ok

    def closeEvent(self, e):
        if self._installer and self._installer.isRunning():
            self._installer.wait(3000)
        super().closeEvent(e)


# ───────────────────────────── entry point ─────────────────────────────
def main():
    global TM
    if sys.platform == "win32":
        try:
            import ctypes
            ctypes.windll.shell32.SetCurrentProcessExplicitAppUserModelID("horizon.launcher.gorillatag")
        except Exception:
            pass
    QApplication.setHighDpiScaleFactorRoundingPolicy(Qt.HighDpiScaleFactorRoundingPolicy.PassThrough)
    app = QApplication(sys.argv)
    app.setApplicationName(APP_NAME)
    app.setOrganizationName("horizonLauncher")
    load_custom_fonts()
    TM = ThemeManager()
    TM.apply()
    win = MainWindow()
    win.show()
    sys.exit(app.exec())


if __name__ == "__main__":
    main()

#wyvren plz dont release source ill give you 10 euro ✌️
