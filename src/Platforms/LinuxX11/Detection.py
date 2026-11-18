import os
from typing import Optional

from PySide6.QtCore import QSocketNotifier
from Xlib import X, display
from Xlib.error import BadWindow, XError

from src.BackgroundDetection.Detection import Detection, WindowInfo


class X11Detection(Detection):
    """Focus detection via _NET_ACTIVE_WINDOW property changes on the X11 root window."""

    def __init__(self, windows=None, parent=None):
        super().__init__(windows, parent)
        self._display: Optional[display.Display] = None
        self._root = None
        self._notifier: Optional[QSocketNotifier] = None
        self._watched = None
        self._atom_active = None
        self._atom_name = None
        self._atom_name_legacy = None

    def hook(self) -> None:
        self._display = display.Display()
        self._root = self._display.screen().root
        self._atom_active = self._display.intern_atom("_NET_ACTIVE_WINDOW")
        self._atom_name = self._display.intern_atom("_NET_WM_NAME")
        self._atom_name_legacy = self._display.intern_atom("WM_NAME")
        self._root.change_attributes(event_mask=X.PropertyChangeMask)
        self._watchActive()
        self._display.flush()
        self._notifier = QSocketNotifier(
            self._display.fileno(), QSocketNotifier.Type.Read, self
        )
        self._notifier.activated.connect(self._drain)

    def unhook(self) -> None:
        if self._notifier:
            self._notifier.setEnabled(False)
            self._notifier.deleteLater()
            self._notifier = None
        if self._display:
            self._display.close()
        self._display = None
        self._root = None
        self._watched = None

    def queryFocusedWindow(self) -> Optional[WindowInfo]:
        if self._display is None:
            tmp = display.Display()
            try:
                return self._read(tmp, tmp.screen().root)
            finally:
                tmp.close()
        return self._read(self._display, self._root)

    # --- internals ---
    def _drain(self) -> None:
        changed = False
        while self._display.pending_events():
            ev = self._display.next_event()
            if ev.type != X.PropertyNotify:
                continue
            if ev.window == self._root and ev.atom == self._atom_active:
                self._watchActive()
                changed = True
            elif ev.atom in (self._atom_name, self._atom_name_legacy):
                changed = True
        if changed:
            self._onWindowEvent(self._read(self._display, self._root))

    def _activeId(self, d, root) -> int:
        prop = root.get_full_property(d.intern_atom("_NET_ACTIVE_WINDOW"), X.AnyPropertyType)
        return int(prop.value[0]) if prop and len(prop.value) else 0

    def _watchActive(self) -> None:
        try:
            if self._watched is not None:
                self._watched.change_attributes(event_mask=0)
        except (BadWindow, XError):
            pass
        self._watched = None
        wid = self._activeId(self._display, self._root)
        if wid:
            win = self._display.create_resource_object("window", wid)
            try:
                win.change_attributes(event_mask=X.PropertyChangeMask)
                self._watched = win
            except (BadWindow, XError):
                pass
        self._display.flush()

    def _read(self, d, root) -> Optional[WindowInfo]:
        wid = self._activeId(d, root)
        if not wid:
            return None
        win = d.create_resource_object("window", wid)
        try:
            title = ""
            prop = win.get_full_property(d.intern_atom("_NET_WM_NAME"), X.AnyPropertyType)
            if prop:
                v = prop.value
                title = v.decode("utf-8", "replace") if isinstance(v, bytes) else str(v)
            elif (name := win.get_wm_name()):
                title = name if isinstance(name, str) else name.decode("latin-1")
            cls = win.get_wm_class()
            wm_class = cls[1] if cls and len(cls) > 1 else (cls[0] if cls else "")
            pid_prop = win.get_full_property(d.intern_atom("_NET_WM_PID"), X.AnyPropertyType)
            pid = int(pid_prop.value[0]) if pid_prop and len(pid_prop.value) else 0
        except (BadWindow, XError):
            return None
        exe = ""
        if pid:
            try:
                exe = os.path.basename(os.readlink(f"/proc/{pid}/exe"))
            except OSError:
                pass
        return WindowInfo(wid, title, wm_class, exe, pid)
