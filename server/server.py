import asyncio
from asyncio import StreamReader, StreamWriter
import json
from bot.misc import logger

from .distribution import distribution

async def handle_connection(reader:StreamReader, writer:StreamWriter):
    addr = writer.get_extra_info("peername")
    logger.info("Connected by", addr)
    while True:
        # Receive
        logger.info('Receive')
        try:
            data = await reader.readuntil(separator=b'\n')
        except ConnectionError:
            logger.info(f"Client suddenly closed while receiving from {addr}")
            break
        if not data:
            break
        # data.pop() # remove separator '\n'
        data = json.loads(data)
        # print(f"Data {data}")
        await distribution(data)
        logger.info('data validated')
    writer.close()
    logger.info("Disconnected by", addr)

async def server_main(host, port):
    server = await asyncio.start_server(handle_connection, host, port)
    async with server:
        await server.serve_forever()
