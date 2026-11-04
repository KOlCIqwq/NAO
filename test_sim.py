import sys
import os
import time
from naoqi import ALProxy

# Add RobotPositions directory to import path
script_dir = os.path.dirname(os.path.abspath(__file__))
positions_dir = os.path.join(script_dir, "RobotPositions")
sys.path.insert(0, positions_dir)

def run_sequence(ip, port):
    print("Connecting to robot at {}:{}...".format(ip, port))
    try:
        motion = ALProxy("ALMotion", ip, port)
        posture = ALProxy("ALRobotPosture", ip, port)
    except Exception as e:
        print("Failed to connect: {}".format(e))
        return

    print("Waking up robot and setting initial posture...")
    motion.wakeUp()
    posture.goToPosture("StandInit", 0.8)

    # 6 standing moves executed fluidly in succession
    sequence = [
        "17-SitRelax"
    ]

    for move_name in sequence:
        print("--> Executing: {}".format(move_name))
        mod = __import__(move_name)
        mod.main(ip, port)
        time.sleep(0.1)

    print("Returning to StandInit and resting...")
    posture.goToPosture("StandInit", 0.6)
    motion.rest()
    print("Test sequence finished successfully.")

if __name__ == "__main__":
    ip = "127.0.0.1"
    port = int(sys.argv[1]) if len(sys.argv) > 1 else 9559
    run_sequence(ip, port)