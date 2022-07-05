#!/usr/bin/env python3

import sys, json
import asyncio
from websockets import connect

class EchoWebsocket:
    async def __aenter__(self):
        self._conn = connect('wss://ws.binaryws.com/websockets/v3')
        self.websocket = await self._conn.__aenter__()
        return self

    async def __aexit__(self, *args, **kwargs):
        await self._conn.__aexit__(*args, **kwargs)

    async def send(self, message):
        await self.websocket.send(message)

    async def receive(self):
        return await self.websocket.recv()

class mtest:
    def __init__(self):
        self.wws = EchoWebsocket()
        self.loop = asyncio.get_event_loop()

    def get_ticks(self):
        return self.loop.run_until_complete(self.__async__get_ticks())

    async def __async__get_ticks(self):
        async with self.wws as echo:
            await echo.send(json.dumps({'ticks_history': 'R_50', 'end': 'latest', 'count': 1}))
            return await echo.receive()


if __name__ == "__main__":
    a = mtest()

    foo = a.get_ticks()
    print(foo)

    print("async works like a charm!")

    foo = a.get_ticks()
    print(foo)
