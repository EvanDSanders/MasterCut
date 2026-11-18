from fnmatch import fnmatchcase
from typing import Literal

from pydantic import BaseModel

MatchType = Literal["class", "substring", "glob"]


class Window(BaseModel):
    """How to recognise a window: match_type, the string to match, and a display name."""

    match_type: MatchType
    pattern: str
    name: str

    def matches(self, title: str = "", wm_class: str = "", executable: str = "") -> bool:
        pattern = self.pattern.lower()
        if self.match_type == "class":
            return wm_class.lower() == pattern
        if self.match_type == "substring":
            return pattern in title.lower()
        return any(
            fnmatchcase(value.lower(), pattern)
            for value in (title, wm_class, executable)
            if value
        )
