import json
import logging
from pathlib import Path

from PySide6.QtGui import QKeySequence
from PySide6.QtWidgets import QMenu, QMenuBar

logger = logging.getLogger("CA:ShortcutsManager")

# Mapping between Qt PortableText modifier names and human-readable words used in JSON files.
_PORTABLE_TO_WORDS = {"Ctrl": "Control", "Meta": "Super"}
_WORDS_TO_PORTABLE = {v: k for k, v in _PORTABLE_TO_WORDS.items()}


def _to_words(portable: str) -> str:
    """Convert Qt portable shortcut string to word form for JSON storage.

    e.g. "Ctrl+Shift+D" -> "Control+Shift+D", "Meta+Z" -> "Super+Z"
    """
    for src, dst in _PORTABLE_TO_WORDS.items():
        portable = portable.replace(src, dst)
    return portable


def _from_words(words: str) -> str:
    """Convert word-form shortcut string back to Qt portable text.

    e.g. "Control+Shift+D" -> "Ctrl+Shift+D", "Super+Z" -> "Meta+Z"
    """
    for src, dst in _WORDS_TO_PORTABLE.items():
        words = words.replace(src, dst)
    return words


CONFIG_DIR = Path.home() / ".cgaspects"
SHORTCUTS_FILE = CONFIG_DIR / "shortcuts.json"
SHORTCUTS_DEFAULT_FILE = CONFIG_DIR / "shortcuts_default.json"


class ActionRecord:
    __slots__ = ("action", "object_name", "display_name", "menu_path", "default_shortcut")

    def __init__(self, action, object_name, display_name, menu_path, default_shortcut):
        self.action = action
        self.object_name = object_name
        self.display_name = display_name
        self.menu_path = menu_path
        self.default_shortcut = default_shortcut


class ShortcutsManager:
    """
    Manages QAction keyboard shortcuts for CrystalAspects.

    Discovers all QActions by walking the live menubar, loads user overrides
    from ~/.cgaspects/shortcuts.json, and applies them on startup.
    """

    def __init__(self, menubar: QMenuBar):
        self._menubar = menubar
        self._records: dict[str, ActionRecord] = {}
        self._user_overrides: dict[str, str] = {}

        self._discover_actions()
        self._write_defaults()
        self._load_overrides()
        self._apply_overrides()

    def _discover_actions(self) -> None:
        seen: set[str] = set()
        for top_action in self._menubar.actions():
            menu = top_action.menu()
            if menu is None:
                continue
            menu_title = top_action.text().replace("&", "")
            self._walk_menu(menu, menu_title, seen)

    def _walk_menu(self, menu: QMenu, path: str, seen: set[str]) -> None:
        for action in menu.actions():
            if action.isSeparator():
                continue
            submenu = action.menu()
            if submenu is not None:
                sub_title = action.text().replace("&", "")
                self._walk_menu(submenu, f"{path} > {sub_title}", seen)
                continue
            obj_name = action.objectName()
            if not obj_name or obj_name in seen:
                continue
            seen.add(obj_name)
            display = action.text().replace("&", "").strip()
            default_sc = action.shortcut().toString(QKeySequence.PortableText)
            self._records[obj_name] = ActionRecord(
                action=action,
                object_name=obj_name,
                display_name=display,
                menu_path=path,
                default_shortcut=default_sc,
            )
            logger.debug("Discovered: %s [%s] default=%r", obj_name, path, default_sc)

    def _write_defaults(self) -> None:
        """Write all current code defaults to shortcuts_default.json on every startup."""
        CONFIG_DIR.mkdir(parents=True, exist_ok=True)
        defaults = {
            obj_name: _to_words(rec.default_shortcut)
            for obj_name, rec in sorted(self._records.items())
        }
        try:
            with SHORTCUTS_DEFAULT_FILE.open("w", encoding="utf-8") as f:
                json.dump(defaults, f, indent=2, ensure_ascii=False)
            logger.debug(
                "Wrote %d default shortcut(s) to %s", len(defaults), SHORTCUTS_DEFAULT_FILE
            )
        except OSError as exc:
            logger.warning("Could not write shortcuts_default.json: %s", exc)

    def _load_overrides(self) -> None:
        if not SHORTCUTS_FILE.exists():
            return
        try:
            with SHORTCUTS_FILE.open("r", encoding="utf-8") as f:
                data = json.load(f)
            if isinstance(data, dict):
                # Convert word-form ("Control+O") back to portable ("Ctrl+O") for Qt
                self._user_overrides = {
                    k: _from_words(v)
                    for k, v in data.items()
                    if isinstance(k, str) and isinstance(v, str)
                }
                logger.info("Loaded %d shortcut override(s)", len(self._user_overrides))
        except (json.JSONDecodeError, OSError) as exc:
            logger.warning("Could not read shortcuts.json: %s", exc)

    def _apply_overrides(self) -> None:
        for obj_name, shortcut_str in self._user_overrides.items():
            if obj_name in self._records:
                self._records[obj_name].action.setShortcut(QKeySequence(shortcut_str))
                logger.debug("Applied override: %s -> %r", obj_name, shortcut_str)

    def save_overrides(self, overrides: dict[str, str]) -> None:
        CONFIG_DIR.mkdir(parents=True, exist_ok=True)
        to_save: dict[str, str] = {}
        for obj_name, shortcut_str in overrides.items():
            rec = self._records.get(obj_name)
            if rec is None:
                continue
            canonical = QKeySequence(shortcut_str).toString(QKeySequence.PortableText)
            rec.action.setShortcut(QKeySequence(canonical))
            if canonical != rec.default_shortcut:
                to_save[obj_name] = _to_words(canonical)
        self._user_overrides = to_save
        try:
            with SHORTCUTS_FILE.open("w", encoding="utf-8") as f:
                json.dump(to_save, f, indent=2, ensure_ascii=False)
            logger.info("Saved %d shortcut override(s)", len(to_save))
        except OSError as exc:
            logger.error("Could not write shortcuts.json: %s", exc)

    def reset_to_defaults(self) -> None:
        for rec in self._records.values():
            rec.action.setShortcut(QKeySequence(rec.default_shortcut))
        self._user_overrides = {}
        CONFIG_DIR.mkdir(parents=True, exist_ok=True)
        try:
            with SHORTCUTS_FILE.open("w", encoding="utf-8") as f:
                json.dump({}, f)
        except OSError as exc:
            logger.error("Could not clear shortcuts.json: %s", exc)

    def get_records(self) -> list[ActionRecord]:
        return sorted(self._records.values(), key=lambda r: (r.menu_path, r.display_name))

    def get_current_shortcut(self, obj_name: str) -> str:
        rec = self._records.get(obj_name)
        if rec is None:
            return ""
        return rec.action.shortcut().toString(QKeySequence.PortableText)
