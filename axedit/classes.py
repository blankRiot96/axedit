import typing_extensions as t

from axedit import shared


class Pos:
    def __init__(self, x: int, y: int) -> None:
        self.x = x
        self.y = y

    def __eq__(self, __value: t.Self) -> bool:
        return __value.x == self.x and __value.y == self.y

    def __repr__(self) -> str:
        return f"Pos({self.x}, {self.y})"


class CharList(list):
    def _on_char_change(self):
        shared.chars_changed = True

        if (
            self
            and isinstance(self[0], str)
            and ("".join(self).startswith("import") or "".join(self).startswith("from"))
        ):
            shared.import_line_changed = True

    def append(self, item):
        super().append(item)
        self._on_char_change()

    def extend(self, iterable):
        super().extend(iterable)
        self._on_char_change()

    def insert(self, index, item):
        super().insert(index, item)
        self._on_char_change()

    def remove(self, item):
        super().remove(item)
        self._on_char_change()

    def pop(self, index=-1):
        popped_item = super().pop(index)
        self._on_char_change()
        return popped_item

    def __setitem__(self, index, value):
        super().__setitem__(index, value)
        self._on_char_change()

    def __delitem__(self, index):
        super().__delitem__(index)
        self._on_char_change()
