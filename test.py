import asyncio

async def dc_user():
            await asyncio.sleep(20)
            print("You have been reported a zombie and didn't respond!")
            print("'s session terminated because they acted like a zombie!")





async def main():
        task1 = asyncio.create_task(dc_user())
        await task1


asyncio.run(main())
