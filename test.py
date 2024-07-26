import asyncio

from lsprotocol import types
from pygls.lsp.client import BaseLanguageClient


class LanguageClient(BaseLanguageClient):

    async def server_exit(self, server: asyncio.subprocess.Process):
        """Called when the server process exits."""

        #   0: all good
        # -15: terminated
        print(server.returncode)
        if server.returncode not in {0, -15}:
            print(f"Server process exited with code: {server.returncode}")

            if server.stderr is not None:
                stderr = await server.stderr.read()
                print(f"Stderr:\n{stderr.decode('utf8')}")

        raise SystemExit(server.returncode)


async def main():
    client = LanguageClient("example-client", "v1")
    await client.start_io("basedpyright-langserver", "--stdio")
    # await client.start_io("pyright-langserver", "--stdio")
    await client.initialize_async(
        types.InitializeParams(
            capabilities=types.ClientCapabilities(),
            root_uri="file:///home/axis/p/axedit",
        )
    )
    client.initialized(types.InitializedParams())

    response = await client.text_document_completion_async(
        types.CompletionParams(
            types.TextDocumentIdentifier("file:///home/axis/p/axedit/axedit/cli.py"),
            types.Position(0, 2),
        )
    )
    print(f"AUTOCOMPLETE RESULTS = {response}")
    response = await client.text_document_semantic_tokens_full_async(
        types.SemanticTokensParams(
            types.TextDocumentIdentifier("file:///home/axis/p/axedit/axedit/cli.py")
        )
    )
    print(f"SEMANTIC TOKENS RESULT = {response}")

    await client.shutdown_async(None)
    client.exit(None)
    await client.stop()


asyncio.run(main())
