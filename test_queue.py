import multiprocessing


def linter_process(queue, response_queue):
    while True:
        src, mouse_pos = queue.get()
        if src is None:  # Exit signal
            break
        lints = f"Linter suggestions for {src} at {mouse_pos}"
        response_queue.put(("linter", lints))


def autocomplete_process(queue, response_queue):
    while True:
        src, mouse_pos = queue.get()
        if src is None:  # Exit signal
            break
        completions = f"Autocomplete suggestions for {src} at {mouse_pos}"
        response_queue.put(("autocomplete", completions))


if __name__ == "__main__":
    queue = multiprocessing.Queue()
    response_queue = multiprocessing.Queue()

    linter = multiprocessing.Process(
        target=linter_process, args=(queue, response_queue)
    )
    autocomplete = multiprocessing.Process(
        target=autocomplete_process, args=(queue, response_queue)
    )

    linter.start()
    autocomplete.start()

    src = "example source code"
    mouse_pos = (10, 20)

    queue.put((src, mouse_pos))
    queue.put((src, mouse_pos))

    linter_response = response_queue.get()
    autocomplete_response = response_queue.get()

    print(f"Main process received from linter: {linter_response[1]}")
    print(f"Main process received from autocomplete: {autocomplete_response[1]}")

    queue.put((None, None))
    queue.put((None, None))

    linter.join()
    autocomplete.join()
