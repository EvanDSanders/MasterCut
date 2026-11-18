from abc import abstractmethod
from dataclasses import dataclass
from typing import Optional

from PySide6.QtCore import QObject, Signal

from src.Configuration.DataTypes.Window import Window


@dataclass(frozen=True)
class WindowInfo:
    id: int
    title: str = ""
    wm_class: str = ""
    executable: str = ""
    pid: int = 0


class Detection(QObject):
    """Abstract window detection. Platform subclasses implement the hook and state query."""

    focusChanged = Signal(object)        # WindowInfo | None
    windowFocused = Signal(object, object)  # Window, WindowInfo
    windowUnfocused = Signal(object)     # Window

    def __init__(self, windows: Optional[list[Window]] = None, parent=None):
        super().__init__(parent)
        self._windows: list[Window] = list(windows or [])
        self._current: Optional[WindowInfo] = None
        self._active: Optional[Window] = None
        self._hooked = False

    # --- configuration ---
    def setWindows(self, windows: list[Window]) -> None:
        self._windows = list(windows)
        self._evaluate(self._current)

    @property
    def windows(self) -> list[Window]:
        return list(self._windows)

    # --- state ---
    @property
    def focusedWindow(self) -> Optional[WindowInfo]:
        return self._current

    @property
    def activeMatch(self) -> Optional[Window]:
        return self._active

    def match(self, info: Optional[WindowInfo]) -> Optional[Window]:
        if info is None:
            return None
        for w in self._windows:
            if w.matches(info.title, info.wm_class, info.executable):
                return w
        return None

    def isWindowFocused(self, window: Window) -> bool:
        return self._active == window

    def checkFocus(self) -> Optional[WindowInfo]:
        """Query the window manager now and update state."""
        info = self.queryFocusedWindow()
        self._evaluate(info)
        return info

    # --- hook lifecycle ---
    @property
    def isHooked(self) -> bool:
        return self._hooked

    def start(self) -> None:
        if self._hooked:
            return
        self.hook()
        self._hooked = True
        self.checkFocus()

    def stop(self) -> None:
        if not self._hooked:
            return
        self.unhook()
        self._hooked = False

    # --- for subclasses ---
    def _onWindowEvent(self, info: Optional[WindowInfo]) -> None:
        """Subclasses call this whenever the window manager reports a focus/title change."""
        self._evaluate(info)

    def _evaluate(self, info: Optional[WindowInfo]) -> None:
        if info != self._current:
            self._current = info
            self.focusChanged.emit(info)
        new = self.match(info)
        if new != self._active:
            old, self._active = self._active, new
            if old is not None:
                self.windowUnfocused.emit(old)
            if new is not None:
                self.windowFocused.emit(new, info)

    @abstractmethod
    def hook(self) -> None:
        """Begin listening to the window manager; call _onWindowEvent on updates."""

    @abstractmethod
    def unhook(self) -> None:
        """Stop listening and release resources."""

    @abstractmethod
    def queryFocusedWindow(self) -> Optional[WindowInfo]:
        """Return the currently focused window, or None."""
