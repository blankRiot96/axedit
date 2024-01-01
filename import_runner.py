import types

from wrapt_timeout_decorator import timeout


def import_mod() -> types.ModuleType:
    try:
        import runner

        print("henlo")
        return runner
    finally:
        ...


def resultant():
    return timeout(1)(import_mod)()
