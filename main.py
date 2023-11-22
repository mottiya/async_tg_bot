from loguru import logger
import signal

from bot import logging, misc, database, handlers
from server.server import server_main
from config import SERVER_HOST, SERVER_PORT


def sigterm_handler(_signo, _stack_frame):
    logger.critical('SIGTERM CLOSE')
    misc.loop.stop()

async def on_startup():
    await logging.setup()
    await misc.setup()
    await database.setup()

    logger.info("Configure webhook...")
    await misc.bot.delete_webhook(drop_pending_updates=True)

    await handlers.setup(misc.dp)

async def on_shutdown():
    await misc.bot.delete_webhook()

async def main():
    await on_startup()
    await misc.dp.start_polling(misc.bot, allowed_updates=misc.dp.resolve_used_update_types())
    await on_shutdown()

def run():
    misc.loop.create_task(server_main(SERVER_HOST, SERVER_PORT))
    misc.loop.create_task(main())
    misc.loop.run_forever()
    misc.loop.close()

if __name__ == '__main__':
    signal.signal(signal.SIGTERM, sigterm_handler)
    run()
