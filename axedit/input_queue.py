import enum
import re
import typing as t
from dataclasses import dataclass

from axedit import shared
from axedit.classes import CharList
from axedit.utils import Time


class Action(enum.Enum):
    INSERT = enum.auto()
    DELETE = enum.auto()


@dataclass(slots=True, frozen=True)
class HistoryElement:
    text: str
    pos: tuple[int, int]
    action: Action


class HistoryManager:
    """Manages the file history"""

    def __init__(self) -> None:
        self.history: list[HistoryElement] = []

    def insert(self, text: str, pos: tuple[int, int]):
        self.history.append(HistoryElement(text, pos, Action.INSERT))

    def delete(self, text: str, pos: tuple[int, int]):
        self.history.append(HistoryElement(text, pos, Action.DELETE))

    def _undo_insert(self, element: HistoryElement):
        pass

    def _undo_delete(self, element: HistoryElement):
        carried_over = ""
        lines = element.text.splitlines()
        for i, line in enumerate(map(CharList, lines)):
            if carried_over:
                line.extend(carried_over)
            y = element.pos[1] + i
            x = 0 if i else element.pos[0]
            try:
                shared.chars[y][x:x] = line
            except IndexError:
                shared.chars.append(line)
            carried_over = "".join(shared.chars[y][x + len(line) - len(carried_over) :])
            if 0 < i < len(lines) - 1:
                del shared.chars[y][x + len(line) - len(carried_over) :]
            if i == 0:
                del shared.chars[y][x + len(line) :]

        shared.cursor_pos.x = len(line) + x - len(carried_over)
        shared.cursor_pos.y = y

    def undo(self):
        return
        if not self.history:
            return

        element = self.history.pop()
        if element.action == Action.INSERT:
            self._undo_insert(element)
        elif element.action == Action.DELETE:
            self._undo_delete(element)


PgKey: t.TypeAlias = int | str


class InputManager:
    def __init__(self, mapping: dict[PgKey | tuple[PgKey, ...], t.Callable]) -> None:
        self.mapping = mapping

    def scan_for_input(self, binding: PgKey | tuple[PgKey]) -> bool:
        if isinstance(binding, tuple):
            if binding == tuple(shared.action_queue):
                shared.action_queue.clear()
                return True
            return False
        return shared.kp[binding]

    def update(self):
        for binding, call in self.mapping.items():
            if self.scan_for_input(binding):
                call()


RegexPattern: t.TypeAlias = str


class RegexManager:
    def __init__(self, mapping: dict[RegexPattern, t.Callable]) -> None:
        self.mapping = mapping

    def update(self):
        if not shared.actions_modified:
            return

        for pattern, call in self.mapping.items():
            if re.match(pattern, shared.action_str) is None:
                continue

            call()
            shared.action_queue.clear()
            break


EventType: t.TypeAlias = int


class EventManager:
    def __init__(self, mapping: dict[EventType, t.Callable]) -> None:
        self.mapping = mapping

    def update(self):
        for event in shared.events:
            call = self.mapping.get(event.type)
            if call is not None:
                call(event)


class KeyManager:
    def __init__(self, mapping: dict[PgKey, t.Callable]) -> None:
        self.mapping = mapping

    def update(self):
        for key, call in self.mapping.items():
            if shared.keys[key]:
                call()


class AcceleratedKeyPress:
    def __init__(
        self,
        key: PgKey,
        callback: t.Callable,
        timer_cd: float = 0.5,
        timer_delta: float = 0.3,
        timer_min: float = 0.02,
        base_keys: list[PgKey] | None = None,
    ) -> None:
        self.key = key
        self.callback = callback
        self.timer = Time(timer_cd)
        self.timer_cd = timer_cd
        self.timer_delta = timer_delta
        self.timer_min = timer_min

        self.input_manager = InputManager({key: self.on_first_call})
        self.key_manager = KeyManager({key: self.callback})

        self.base_keys = base_keys

    def on_first_call(self):
        self.callback()
        self.timer.reset()
        self.timer.time_to_pass = self.timer_cd

    def handle_timer(self):
        if self.timer.tick():
            self.key_manager.update()
            if self.timer.time_to_pass <= self.timer_min:
                self.timer.time_to_pass = self.timer_min
                return
            self.timer.time_to_pass -= self.timer_delta

    def get_base_key_status(self) -> bool:
        if self.base_keys is None:
            return True

        for key in self.base_keys:
            if not shared.keys[key]:
                return False

        return True

    def update(self):
        if not self.get_base_key_status():
            return
        self.input_manager.update()
        self.handle_timer()
