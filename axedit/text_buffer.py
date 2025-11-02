# TODO
class TextBuffer:
    def insert(self, line: int, col: int) -> None:
        pass

    def delete(self, line: int, col: int) -> None:
        pass

    def insert_chunk(self, start: tuple[int, int]) -> None:
        pass

    def delete_chunk(self, start: tuple[int, int], end: tuple[int, int]) -> None:
        pass
