# movement/main.py

import random
import time

from movement.movement import (
    backward,
    forward,
    forward_arc_left,
    forward_arc_right,
    gentle_left,
    gentle_right,
    left,
    right,
    stop,
)
from movement.path_memory import mark_blocked, choose_direction
from movement.config import (
    FIRST_MOVE_DELAY_MAX_SEC,
    FIRST_MOVE_DELAY_MIN_SEC,
    IDLE_BETWEEN_MOVES_MAX_SEC,
    IDLE_BETWEEN_MOVES_MIN_SEC,
    MAX_DISTANCE_CM,
    SAFE_DISTANCE_CM,
)
from movement.ultrasonic import drop_detected, get_distance_cm, pause_triggered


def _natural_wander_move():
    """Pick a varied maneuver when the path ahead is clear (not straight-only)."""
    r = random.random()
    if r < 0.34:
        forward(duration=random.uniform(0.42, 0.62))
    elif r < 0.52:
        forward_arc_left(duration=random.uniform(0.5, 0.75))
    elif r < 0.70:
        forward_arc_right(duration=random.uniform(0.5, 0.75))
    elif r < 0.84:
        gentle_left()
    elif r < 0.94:
        gentle_right()
    else:
        # Occasional short straight then a nudge (feels like glancing / exploring)
        forward(duration=random.uniform(0.35, 0.5))
        if random.random() < 0.6:
            gentle_left() if random.random() < 0.5 else gentle_right()


def robot_loop():
    try:
        _robot_loop_impl()
    except PermissionError:
        print(
            "⛔ Autonomous mode stopped: motor I2C not accessible. "
            "Fix permissions (see message above), then restart."
        )


def _robot_loop_impl():
    print("🤖 Autonomous robot starting (idle until first wander)...")
    stop()
    time.sleep(2)

    paused = False
    pause_latched = False
    next_allowed_move_time = time.time() + random.uniform(
        FIRST_MOVE_DELAY_MIN_SEC, FIRST_MOVE_DELAY_MAX_SEC
    )

    while True:
        # -------- PAUSE SENSOR CHECK --------
        if pause_triggered():
            if not pause_latched:
                paused = not paused
                pause_latched = True

                if paused:
                    print("⏸️ PAUSED — motors stopped")
                    stop()
                else:
                    print("▶️ RESUMED")
        else:
            pause_latched = False

        # -------- IF PAUSED --------
        if paused:
            stop()
            time.sleep(1)
            continue

        # -------- DROP DETECTION --------
        if drop_detected():
            print("⚠️ DROP DETECTED! Avoiding edge...")

            stop()
            time.sleep(0.1)

            # Mark forward as unsafe (like obstacle)
            mark_blocked("forward")

            # Back up slightly
            backward()
            time.sleep(0.4)
            stop()
            time.sleep(0.1)

            # Choose new direction intelligently
            direction = choose_direction()
            print(f"🧠 New direction after drop: {direction}")

            if direction == "left":
                left()
            elif direction == "right":
                right()
            elif direction == "backward":
                backward()

            time.sleep(0.3)
            stop()
            continue

        # -------- NORMAL AUTONOMY --------
        stop()
        distance = get_distance_cm()

        if distance is None:
            print("⚠️ No distance reading")
            time.sleep(0.2)
            continue

        print(f"📏 Distance ahead: {distance:.1f} cm")

        if distance < MAX_DISTANCE_CM:
            print(f"🚨 Object detected at {distance:.1f} cm")

            if distance <= SAFE_DISTANCE_CM:
                print("🛑 Too close! Emergency avoidance")
                mark_blocked("forward")
                backward()
                right()
                continue

            mark_blocked("forward")
            direction = choose_direction()
            print(f"➡️ Choosing direction: {direction}")

            if direction == "left":
                left()
            elif direction == "right":
                right()
            elif direction == "backward":
                backward()

        else:
            print("✅ Path clear")
            if time.time() < next_allowed_move_time:
                # Stay stopped between maneuvers — reads as "paused / looking" not constant crawl
                time.sleep(0.25)
                continue
            _natural_wander_move()
            next_allowed_move_time = time.time() + random.uniform(
                IDLE_BETWEEN_MOVES_MIN_SEC, IDLE_BETWEEN_MOVES_MAX_SEC
            )

        time.sleep(0.3)


if __name__ == "__main__":
    robot_loop()