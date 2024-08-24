import asyncio


def set_interval(interval):
    def scheduler(fcn):
        async def wrapper(*args, **kwargs):
            while True:
                asyncio.create_task(fcn(*args, **kwargs))
                await asyncio.sleep(interval)
        return wrapper
    return scheduler

def start_interval(callback):
    asyncio.run(callback)
