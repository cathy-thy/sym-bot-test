#!/usr/bin/env python3
import asyncio
import logging.config
from pathlib import Path

from symphony.bdk.core.activity.command import CommandContext
from symphony.bdk.core.config.loader import BdkConfigLoader
from symphony.bdk.core.symphony_bdk import SymphonyBdk

from .order_listener import MessageListener, FormListener

from .activities import EchoCommandActivity, GreetUserJoinedActivity
from .gif_activities import GifSlashCommand, GifFormReplyActivity

# Configure logging
current_dir = Path(__file__).parent.parent
logging_conf = Path.joinpath(current_dir, 'resources', 'logging.conf')
logging.config.fileConfig(logging_conf, disable_existing_loggers=False)


async def run():
    config = BdkConfigLoader.load_from_file(Path.joinpath(current_dir, 'config.yaml'))

    async with SymphonyBdk(config) as bdk:
        datafeed_loop = bdk.datafeed()
        datafeed_loop.subscribe(MessageListener(bdk.messages()))
        datafeed_loop.subscribe(FormListener(bdk.messages()))
        #datafeed_loop.subscribe(MessageListener())

        activities = bdk.activities()
        activities.register(EchoCommandActivity(bdk.messages()))
        activities.register(GreetUserJoinedActivity(bdk.messages(), bdk.users()))
        activities.register(GifSlashCommand(bdk.messages()))
        activities.register(GifFormReplyActivity(bdk.messages()))



        # Start the datafeed read loop
        
        #activities = bdk.activities()
        
        @activities.slash("/hello")
        async def hello(context: CommandContext):
            name = context.initiator.user.display_name
            response = f"<messageML>Hello {name}, hope you are doing well!</messageML>"
            await bdk.messages().send_message(context.stream_id, response)
        
        @activities.slash("/price")
        async def price(context: CommandContext):
            logging.info("Price command triggered")
            stream_id = context.stream_id
            form = "<form id=\"price\">"
            form += "<text-field name=\"ticker\" placeholder=\"Ticker\" /><br />"
            form += "<button type=\"action\" name=\"price\">Get Price</button>"
            form += "</form>"
            await bdk.messages().send_message(stream_id, form)
        
        await datafeed_loop.start()


# Start the main asyncio run
try:
    logging.info("Running bot application...")
    asyncio.run(run())
except KeyboardInterrupt:
    logging.info("Ending bot application")
