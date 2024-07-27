import asyncio
import logging

from lsprotocol import types
from pygls.lsp.client import BaseLanguageClient

logging.basicConfig(level=logging.INFO)


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
    # await client.start_io("pylsp")
    await client.initialize_async(
        types.InitializeParams(
            capabilities=types.ClientCapabilities(
                text_document=types.TextDocumentClientCapabilities(
                    semantic_tokens=types.SemanticTokensClientCapabilities(
                        requests=types.SemanticTokensClientCapabilitiesRequestsType(
                            range=True, full=True
                        ),
                        # full list of token types & modifiers here:
                        # https://github.com/DetachHead/basedpyright/blob/010fd19059944942311b7c5a4148ca30f892f8a0/packages/pyright-internal/src/languageService/semanticTokensProvider.ts#L19-L39
                        token_types=["class", "type", "function"],
                        token_modifiers=[],
                        formats=[types.TokenFormat.Relative],
                    )
                )
            ),
            # capabilities=types.ClientCapabilities(),
            # workspace_folders=[
            #     types.WorkspaceFolder("folder", "file:///home/axis/p/axedit")
            # ],
        )
    )
    client.initialized(types.InitializedParams())
    client.workspace_did_change_configuration(
        types.DidChangeConfigurationParams(types.ConfigurationParams([]))
    )

    @client.feature(types.WINDOW_LOG_MESSAGE)
    def log_message(ls: LanguageClient, params: types.LogMessageParams):
        pass

    file_path = "file:///home/axis/p/axedit/tree.py"
    client.text_document_did_open(
        types.DidOpenTextDocumentParams(
            text_document=types.TextDocumentItem(
                uri=file_path, language_id="python", version=1, text="pr"
            )
        )
    )

    response = await client.text_document_completion_async(
        types.CompletionParams(
            types.TextDocumentIdentifier(file_path),
            types.Position(0, 1),
        )
    )
    print(f"AUTOCOMPLETE RESULTS = {[item.label for item in response.items]}")

    response = await client.text_document_semantic_tokens_full_async(
        types.SemanticTokensParams(types.TextDocumentIdentifier(file_path))
    )
    print(f"SEMANTIC TOKENS RESULT = {response}")

    await client.shutdown_async(None)
    client.exit(None)
    await client.stop()


asyncio.run(main())
