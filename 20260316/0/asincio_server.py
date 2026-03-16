import asyncio
import shlex

async def echo(reader, writer):
    while data := await reader.readline():
        try:
            command, *args = shlex.split(data.decode("utf-8"))
        except:
            continue
        if command == "print":
            writer.write(data[len(command) + 1:])
        elif command == "info":
            if len(args) == 0:
                continue
            if args[0] == "host":
                writer.write((str(writer.get_extra_info('peername')[0]) + "\n").encode("utf-8"))
            elif args[0] == "port":
                writer.write((str(writer.get_extra_info('peername')[1]) + "\n").encode("utf-8"))

    writer.close()
    await writer.wait_closed()

async def main():
    server = await asyncio.start_server(echo, '0.0.0.0', 1337)
    async with server:
        await server.serve_forever()

asyncio.run(main())
