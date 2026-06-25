import asyncio

from django.core.management.base import BaseCommand

from ...mcp_server import DjangoMCPServer


class Command(BaseCommand):
    help = 'Starts the MCP server for Django design'

    def add_arguments(self, parser):
        parser.add_argument('--http', action='store_true', help='Run in HTTP/SSE mode')
        parser.add_argument('--port', type=int, default=8000, help='Port for HTTP mode')
        parser.add_argument('--host', default='127.0.0.1', help='Host for HTTP mode')

    def handle(self, *args, **options):
        server = DjangoMCPServer()

        if options['http']:
            self.stdout.write(self.style.SUCCESS(f"Starting MCP HTTP server on {options['host']}:{options['port']}"))
            try:
                import uvicorn
                from mcp.server.sse import sse_server
                from starlette.applications import Starlette
                from starlette.routing import Route

                async def run_http():
                    async with sse_server(server.server) as (read_stream, write_stream):
                        app = Starlette(
                            routes=[
                                Route("/sse", endpoint=read_stream),
                                Route("/messages", endpoint=write_stream, methods=["POST"]),
                            ]
                        )
                        config = uvicorn.Config(app, host=options['host'], port=options['port'])
                        runner = uvicorn.Server(config)
                        await runner.serve()

                asyncio.run(run_http())
            except ImportError:
                self.stderr.write(self.style.ERROR("HTTP mode requires 'starlette', 'uvicorn', and 'sse-starlette'."))
                return
        else:
            self.stdout.write(self.style.SUCCESS("Starting MCP stdio server..."))
            asyncio.run(server.run())
