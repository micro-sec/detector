import asyncio
import pickle
import sys
import time

import blosc2
import websockets

ws_port = int(sys.argv[1])
ws_max_size = int(sys.argv[2])
window_size = int(sys.argv[3])
syscalls_compression = str(sys.argv[4])


async def syscall_transfer(websocket):
    start_time = time.time()
    batch = list()

    for line in sys.stdin:
        batch.append(line[1:-2].encode())
        if time.time() - start_time >= window_size:
            # Serialize batch
            pickled_batch = pickle.dumps(batch)

            # Compress (or uncompressed) data and send
            if syscalls_compression == "true":
                compressed_pickle = blosc2.compress(pickled_batch)
                await websocket.send(compressed_pickle)
                print("Batch sent containing " + str(len(batch)) + " system calls (compressed) with a size of " + str(
                    sys.getsizeof(compressed_pickle)) + " bytes")
            else:
                await websocket.send(pickled_batch)
                print("Batch sent containing " + str(len(batch)) + " system calls (uncompressed) with a size of " + str(
                    sys.getsizeof(pickled_batch)) + " bytes")

            # Clear batch and reset time
            batch = list()
            start_time = time.time()


async def main():
    async with websockets.serve(syscall_transfer, "0.0.0.0", ws_port, max_size=ws_max_size, ping_interval=None):
        await asyncio.Future()  # run forever


asyncio.run(main())
