''' Motif: Sitting Audience Kiss & Groove (beat-locked 113.3 BPM, 8 beats = 4.24s, upper body ONLY) '''
import sys
import math
from naoqi import ALProxy

DEG = math.pi / 180.0

def main(robotIP="127.0.0.1", port=9559):
    try:
        motion = ALProxy("ALMotion", robotIP, port)
    except Exception as e:
        print("ALMotion error: %s" % e)
        return

    # Upper body only (sitting posture protected)
    names = [
        "HeadPitch", "HeadYaw",
        "LShoulderPitch", "LShoulderRoll", "LElbowYaw", "LElbowRoll", "LWristYaw", "LHand",
        "RShoulderPitch", "RShoulderRoll", "RElbowYaw", "RElbowRoll", "RWristYaw", "RHand"
    ]

    # Beat-locked snap-and-hold:
    # 0.40s -> 1.06s: Right hand to mouth + hold (Beats 1-2)
    # 1.45s -> 2.12s: Blow kiss flourish out + hold (Beats 3-4)
    # 2.65s -> 3.18s: Gentle head nod & wave + hold (Beats 5-6)
    # 3.71s -> 4.24s: Settle back into stable sitting upper-body pose (Beats 7-8)
    t_grid = [0.40, 1.06, 1.45, 2.12, 2.65, 3.18, 3.71, 4.24]
    times = [list(t_grid) for _ in names]

    keys = [
        [-10.0 * DEG, -10.0 * DEG, 12.0 * DEG, 12.0 * DEG, -6.0 * DEG, 6.0 * DEG, -4.0 * DEG, 0.0 * DEG],
        [0.0 * DEG, 0.0 * DEG, -8.0 * DEG, -8.0 * DEG, 14.0 * DEG, 14.0 * DEG, 0.0 * DEG, 0.0 * DEG],
        [68.0 * DEG, 68.0 * DEG, 74.0 * DEG, 74.0 * DEG, 60.0 * DEG, 60.0 * DEG, 68.0 * DEG, 68.0 * DEG],
        [15.0 * DEG, 15.0 * DEG, 16.0 * DEG, 16.0 * DEG, 22.0 * DEG, 22.0 * DEG, 15.0 * DEG, 15.0 * DEG],
        [-35.0 * DEG, -35.0 * DEG, -35.0 * DEG, -35.0 * DEG, -42.0 * DEG, -42.0 * DEG, -35.0 * DEG, -35.0 * DEG],
        [-65.0 * DEG, -65.0 * DEG, -65.0 * DEG, -65.0 * DEG, -55.0 * DEG, -55.0 * DEG, -65.0 * DEG, -65.0 * DEG],
        [0.0 * DEG, 0.0 * DEG, 0.0 * DEG, 0.0 * DEG, -20.0 * DEG, -20.0 * DEG, 0.0 * DEG, 0.0 * DEG],
        [0.3, 0.3, 0.3, 0.3, 0.5, 0.5, 0.3, 0.3],
        # Right arm: Hand to mouth -> flourish out -> wave -> settle
        [22.0 * DEG, 22.0 * DEG, -8.0 * DEG, -8.0 * DEG, 38.0 * DEG, 38.0 * DEG, 64.0 * DEG, 68.0 * DEG],
        [-10.0 * DEG, -10.0 * DEG, -26.0 * DEG, -26.0 * DEG, -20.0 * DEG, -20.0 * DEG, -15.0 * DEG, -15.0 * DEG],
        [40.0 * DEG, 40.0 * DEG, 60.0 * DEG, 60.0 * DEG, 45.0 * DEG, 45.0 * DEG, 35.0 * DEG, 35.0 * DEG],
        [86.0 * DEG, 86.0 * DEG, 26.0 * DEG, 26.0 * DEG, 50.0 * DEG, 50.0 * DEG, 65.0 * DEG, 65.0 * DEG],
        [50.0 * DEG, 50.0 * DEG, 20.0 * DEG, 20.0 * DEG, 10.0 * DEG, 10.0 * DEG, 0.0 * DEG, 0.0 * DEG],
        [0.1, 0.1, 0.95, 0.95, 0.7, 0.7, 0.3, 0.3],
    ]

    motion.angleInterpolation(names, keys, times, True)

if __name__ == "__main__":
    main()
