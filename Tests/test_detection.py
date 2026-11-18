"""Manual test: run `python -m Tests.test_detection` from repo root, then switch windows. Ctrl+C to quit."""
import signal
import sys

from PySide6.QtCore import QCoreApplication

from src.Configuration.DataTypes.Window import Window
from src.Platforms.LinuxX11.Detection import X11Detection

WINDOWS = [
    Window(match_type="class", pattern="konsole", name="Konsole"),
    Window(match_type="substring", pattern="Blender", name="Blender"),
    Window(match_type="glob", pattern="*.exe", name="Windows EXE"),
]


def main() -> int:
    app = QCoreApplication(sys.argv)
    signal.signal(signal.SIGINT, lambda *_: app.quit())
    det = X11Detection(WINDOWS)
    det.focusChanged.connect(lambda i: print(f"[focus]     {i}"))
    det.windowFocused.connect(lambda w, i: print(f"[CALLBACK]  matched   '{w.name}' ({w.match_type}:{w.pattern}) -> {i.title!r}"))
    det.windowUnfocused.connect(lambda w: print(f"[CALLBACK]  unmatched '{w.name}'"))
    det.start()
    print("Hooked X11. Focus windows to test; Ctrl+C to exit.")
    code = app.exec()
    det.stop()
    return code


if __name__ == "__main__":
    sys.exit(main())
