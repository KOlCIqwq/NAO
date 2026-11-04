"""
NAO Choreography Executor
Reads the PDDL-generated choreography plan and executes it sequentially on the NAO robot.
Compatible with Python 2.7 (Choregraphe SDK) and Python 3.

Supports synchronized background audio playback (inspired by TheDebuggers / PartyNAO).
"""

import sys
import os
import json
import time
import subprocess

# Add RobotPositions directory to import path
script_dir = os.path.dirname(os.path.abspath(__file__))
positions_dir = os.path.join(script_dir, "RobotPositions")
sys.path.insert(0, positions_dir)

try:
    from naoqi import ALProxy
except ImportError:
    ALProxy = None

def start_music(audio_path):
    """Launches non-blocking background music player."""
    if not audio_path or not os.path.exists(audio_path):
        return None
    print("Starting background music: {}".format(audio_path))
    try:
        if sys.platform.startswith("win"):
            cmd = 'powershell -NoProfile -Command "$p = New-Object -ComObject wmplayer.ocx; $p.openPlayer(\'{}\')"'.format(os.path.abspath(audio_path).replace("\\", "/"))
            return subprocess.Popen(cmd, shell=True)
        else:
            player = "mpg123" if os.system("which mpg123 > /dev/null 2>&1") == 0 else "afplay"
            return subprocess.Popen([player, audio_path])
    except Exception as e:
        print("Could not start audio playback: {}".format(e))
        return None

def stop_music(proc):
    """Terminates background music playback cleanly."""
    if proc is not None:
        try:
            proc.terminate()
        except Exception:
            pass

def load_plan(plan_file="choreography_plan.json"):
    plan_path = os.path.join(script_dir, plan_file)
    if not os.path.exists(plan_path):
        print("Plan file not found. Running nao_planner to generate one...")
        import nao_planner
        nao_planner.generate_full_choreography()

    with open(plan_path, "r") as f:
        data = json.load(f)
    return data

def execute_plan(ip="127.0.0.1", port=9559, plan_file="choreography_plan.json", music_file=None):
    if ALProxy is None:
        print("ERROR: naoqi library not found. Please run within Choregraphe environment (e.g. run_sim.bat).")
        return False

    data = load_plan(plan_file)
    moves = data.get("moves", [])
    total_dur = data.get("total_duration", 0)

    print("=== NAO Choreography Execution ===")
    print("Connecting to robot at {}:{}...".format(ip, port))
    try:
        motion = ALProxy("ALMotion", ip, port)
        posture = ALProxy("ALRobotPosture", ip, port)
    except Exception as e:
        print("Failed to connect to ALProxy: {}".format(e))
        return False

    print("Robot connected successfully.")
    print("Waking up robot and setting StandInit...")
    motion.wakeUp()
    posture.goToPosture("StandInit", 0.8)

    # Optional audio track start
    music_proc = None
    if not music_file:
        for candidate in ["music.mp3", "music.wav", "track.mp3", "song.mp3"]:
            if os.path.exists(os.path.join(script_dir, candidate)):
                music_file = os.path.join(script_dir, candidate)
                break
    if music_file and os.path.exists(music_file):
        music_proc = start_music(music_file)

    print("Executing {} planned moves (Estimated duration: {:.1f}s)...".format(len(moves), total_dur))
    start_time = time.time()

    for idx, move_file in enumerate(moves, 1):
        mod_name = os.path.splitext(move_file)[0]
        print("--> Step {:02d}/{:02d}: Executing {}".format(idx, len(moves), mod_name))
        try:
            mod = __import__(mod_name)
            if hasattr(mod, "main"):
                mod.main(ip, port)
            else:
                print("Warning: Move {} has no main() function".format(mod_name))
        except Exception as e:
            print("Error executing {}: {}".format(mod_name, e))

        time.sleep(0.1)

    elapsed = time.time() - start_time
    print("\n=== Choreography Complete ===")
    print("Actual execution time: {:.1f} seconds".format(elapsed))

    stop_music(music_proc)
    print("Returning to StandInit and resting...")
    posture.goToPosture("StandInit", 0.6)
    motion.rest()
    print("Finished successfully.")
    return True

if __name__ == "__main__":
    ip = "127.0.0.1"
    port = 59939
    music_arg = None

    args = sys.argv[1:]
    if len(args) > 0 and args[0].isdigit():
        port = int(args[0])
        args = args[1:]
    for idx, a in enumerate(args):
        if a in ["--music", "-m"] and idx + 1 < len(args):
            music_arg = args[idx + 1]

    execute_plan(ip, port, music_file=music_arg)
