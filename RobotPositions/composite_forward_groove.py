''' Composite Layered Move: 7-Move_forward locomotion + Astley arm sway '''
import sys
from naoqi import ALProxy

def main(robotIP="127.0.0.1", port=9559):
    try:
        motion = ALProxy("ALMotion", robotIP, port)
    except Exception as e:
        print("Could not create proxy to ALMotion: %s" % e)
        return

    # Free arms for concurrent dance
    motion.setMoveArmsEnabled(False, False)

    # 1. Non-blocking forward step (dx = 0.04m)
    motion.post.moveTo(0.04, 0.0, 0.0)

    # 2. Concurrently execute Astley arm sway (4.24s, 2 bars at 113.3 BPM)
    names = [
        "HeadYaw",
        "LShoulderPitch", "LShoulderRoll", "LElbowYaw", "LElbowRoll", "LWristYaw",
        "RShoulderPitch", "RShoulderRoll", "RElbowYaw", "RElbowRoll", "RWristYaw"
    ]
    times = [
        [1.06, 2.12, 3.18, 4.24],
        [1.06, 2.12, 3.18, 4.24],
        [1.06, 2.12, 3.18, 4.24],
        [1.06, 2.12, 3.18, 4.24],
        [1.06, 2.12, 3.18, 4.24],
        [1.06, 2.12, 3.18, 4.24],
        [1.06, 2.12, 3.18, 4.24],
        [1.06, 2.12, 3.18, 4.24],
        [1.06, 2.12, 3.18, 4.24],
        [1.06, 2.12, 3.18, 4.24],
        [1.06, 2.12, 3.18, 4.24],
    ]
    keys = [
        [-0.38, 0.38, -0.38, 0.0],
        [1.43, 1.08, 1.43, 1.4],
        [0.09, 0.66, 0.09, 0.18],
        [-0.44, -1.22, -0.44, -1.35],
        [-1.48, -1.48, -1.48, -0.5],
        [-0.61, -0.61, -0.61, 0.0],
        [1.08, 1.43, 1.08, 1.4],
        [-0.66, -0.09, -0.66, -0.18],
        [1.22, 0.44, 1.22, 1.35],
        [1.48, 1.48, 1.48, 0.5],
        [0.61, 0.61, 0.61, 0.0],
    ]

    try:
        motion.angleInterpolation(names, keys, times, True)
    except Exception as e:
        print("Sway interpolation error: %s" % e)

    motion.waitUntilMoveIsFinished()

if __name__ == "__main__":
    ip = sys.argv[1] if len(sys.argv) > 1 else "127.0.0.1"
    port = int(sys.argv[2]) if len(sys.argv) > 2 else 9559
    main(ip, port)
