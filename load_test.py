import sys
import asyncio
import random
import time

# --- Configuration ---
# Allow passing the server IP via command line arguments for cross-computer testing
HOST = sys.argv[1] if len(sys.argv) > 1 else "127.0.0.1"
PORT = 5000
NUM_PLAYERS = 100

SESSION_DURATION_RANGE = (20.0, 120.0) # Seconds before they naturally disconnect
RECONNECT_DELAY_RANGE = (2.0, 10.0)    # Seconds waiting before re-joining target server
LAP_TIME_RANGE = (7.5, 9.0)            # Floor/Ceil float variables

# --- Global Metrics ---
metrics = {
    "sent_total": 0,
    "success_resp": 0,
    "failed_sends": 0
}

def generate_lap_time(current_best):
    """
    Simulates realistic racing improvements.
    - If no current best, sets a baseline near the upper range.
    - If current best exists, 30% chance to beat the personal best by a tiny margin.
    """
    min_lap, max_lap = LAP_TIME_RANGE
    
    if current_best is None:
        # Initial pacing lap
        return round(random.uniform(max_lap - 1.0, max_lap), 3)
    
    # 30% chance to set a new personal best
    if random.random() < 0.3:
        improvement = random.uniform(0.010, 0.200)
        new_lap = max(min_lap, current_best - improvement)
        return round(new_lap, 3)
    
    # Otherwise, they ran a slower lap than their PB (return None to indicate no network ping needed)
    return None

async def handle_connection(reader, username):
    """Background task to read and log incoming server responses across streams."""
    try:
        while True:
            data = await reader.read(1024)
            if not data:
                break
            metrics["success_resp"] += 1
            # print(f"[{username}] Received: {data.decode().strip()}")
    except asyncio.CancelledError:
        pass
    except Exception as e:
        # Connection reset/drop handled safely here
        pass

async def simulate_player(player_id):
    """
    Simulates a full realistic player lifecycle:
    Connect -> Run laps and send PBs -> Disconnect -> Reconnect
    """
    username = f"script{player_id:02d}"
    best_lap = None
    
    while True:
        reader = None
        writer = None
        receive_task = None
        
        try:
            # 1. Connect to the game server via stream
            reader, writer = await asyncio.open_connection(HOST, PORT)
        except Exception as e:
            # Server might be down or actively refusing
            await asyncio.sleep(random.uniform(*RECONNECT_DELAY_RANGE))
            continue
            
        # print(f"[{username}] Connected to {HOST}:{PORT}")
        
        # 2. Start listening for server responses concurrently
        receive_task = asyncio.create_task(handle_connection(reader, username))
        
        # 3. Determine how long this active race session will last
        session_duration = random.uniform(*SESSION_DURATION_RANGE)
        session_start = time.time()
        
        try:
            while (time.time() - session_start) < session_duration:
                # Provide a random disconnect chance (1% per loop) simulating real-world packet drops
                if random.random() < 0.01:
                    print(f"\033[93m[{username}] Network connection abruptly dropped!\033[0m") 
                # Generate a newly completed lap time
                new_lap = generate_lap_time(best_lap)
                
                # Only broadcast the score if they set a personal best or it's their first lap
                if new_lap is not None:
                    best_lap = new_lap
                    message = f"{username}#{best_lap}"
                    
                    writer.write(message.encode())
                    await writer.drain()
                    metrics["sent_total"] += 1
                    
                    # Burst traffic simulation: 5% chance of race completion bugs causing spammed duplicate metrics
                    if random.random() < 0.05:
                        burst_count = random.randint(2, 4)
                        for _ in range(burst_count):
                            best_lap = max(LAP_TIME_RANGE[0], best_lap - random.uniform(0.001, 0.050))
                            burst_msg = f"{username}#{round(best_lap, 3)}"
                            writer.write(burst_msg.encode())
                            await writer.drain()
                            metrics["sent_total"] += 1
                            
                # Simulate the time it takes to drive a lap between network pushes
                await asyncio.sleep(random.uniform(2.0, 5.0))
                
        except Exception as e:
            metrics["failed_sends"] += 1
            print(f"\033[91m[{username}] Session error: {e}\033[0m")
            
        finally:
            # 4. Clean up connection gracefully
            if receive_task:
                receive_task.cancel()
            if writer:
                try:
                    writer.close()
                    await writer.wait_closed()
                except:
                    pass
                    
        # 5. Session finished, wait before re-entering a new active lobby
        # print(f"[{username}] Session ended. Reconnecting later...")
        await asyncio.sleep(random.uniform(*RECONNECT_DELAY_RANGE))

async def print_metrics():
    """Prints live network health metrics tracking total IO overhead."""
    while True:
        await asyncio.sleep(5)
        print(f"\n\033[1;94m--- BURST STRESS TEST METRICS ---\033[0m")
        print(f"\033[96mTotal Updates Sent  :\033[0m {metrics['sent_total']}")
        print(f"\033[92mSuccessful Respon.  :\033[0m {metrics['success_resp']}")
        print(f"\033[91mFailed TCP Writes   :\033[0m {metrics['failed_sends']}")
        print(f"\033[1;94m---------------------------------\033[0m\n")

async def main():
    print(f"\033[1;92mStarting Realistic Asyncio Load Test against {HOST}:{PORT} with {NUM_PLAYERS} players.\033[0m")
    
    # Bundle player simulated sessions along with the metrics printer coroutine
    tasks = [simulate_player(i) for i in range(NUM_PLAYERS)]
    tasks.append(print_metrics())
    
    await asyncio.gather(*tasks)

if __name__ == "__main__":
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        print("\n\033[1;92m[+] Stress test terminated successfully. Final Metrics:\033[0m")
        print(f"\033[96mTotal Updates Sent  :\033[0m {metrics['sent_total']}")
        print(f"\033[92mSuccessful Respon.  :\033[0m {metrics['success_resp']}")
        print(f"\033[91mFailed TCP Writes   :\033[0m {metrics['failed_sends']}")
