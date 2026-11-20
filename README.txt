================================================================================
NAO Planning Challenge - Music-Synchronized Choreography Planning System
Fundamentals of Artificial Intelligence - Universita di Bologna
================================================================================

TEAM INFORMATION:
-----------------
Student Name(s): [FILL TEAM MEMBER NAME(S)]
Student Email(s): [FILL INSTITUTIONAL EMAIL(S)]
Project Repository: https://github.com/KOlCIqwq/NAO

PROJECT OVERVIEW:
-----------------
This project implements an automated, music-synchronized choreography planner and
execution engine for the NAO humanoid robot (tested on virtual NAO in Choregraphe
Suite 2.8, compatible with physical NAO and runnable cross-platform).

Track: Rick Astley - "Never Gonna Give You Up" (rick_120s.mp3 / rick_120s.wav,
calibrated at 113.3 BPM, 120.0s duration).

1. Audio Rhythm & Structure Analysis (audio_analyzer.py):
   - Pure-Python parser extracting per-bar RMS energy (1.0-5.0 scale), beat-dip
     pause flags, and 4-bar phrase sections from rick_120s.wav (with pure-Python
     MP3 fallback if WAV is absent).

2. Autonomous State-Space A* Choreography Planner (nao_planner.py):
   - Extracts physical kinematic features (duration, angular velocity, amplitude,
     pause holds, start/end pose continuity) directly from RobotPositions/*.py.
   - Solves forward state-space A* search optimizing musical bar energy alignment,
     beat-quantized durations, expressiveness, and stage coverage:
       * Initial state : 14-StandInit.py (StandInit)
       * Goal state    : 6-Crouch.py (Crouch)
       * All 6 mandatory positions (Slide 13) scheduled dynamically in
         posture-consistent order:
           WipeForehead.py, Hello.py, 15-StandZero.py,
           16-Sit.py, 17-SitRelax.py, 11-Stand.py
       * 5 official intermediate positions (Slides 16/17):
           3-Double_movement.py, sprinkler.py, 4-Arms_opening.py,
           8-Move_backward.py, 7-Move_forward.py
       * Combined with beat-quantized pop dance motifs and course movements
         (29 total moves in choreography_plan.json, ~111.0s planned, < 120s limit,
         net zero stage displacement dx = 0, dy = 0).

3. Cross-Platform Choreography Executor (execute_choreography.py):
   - Loads choreography_plan.json and runs synchronized background audio
     (Windows winmm MCI / macOS afplay / Linux mpg123; degrades gracefully if
     no audio player/file is present).
   - Adaptive beat-sync scaling aligns move boundaries to musical beats in real time
     inside Choregraphe simulation.
   - Simulator stability handling: verified direct joint interpolation for Sit /
     SitRelax and a two-stage Crouch tuck before Stand to prevent virtual physics
     ground collisions and tipping.

REQUIRED LIBRARIES & ENVIRONMENT:
---------------------------------
- Planner (nao_planner.py, audio_analyzer.py):
  Python 2.7 or Python 3.x using only the Python standard library (zero external
  dependencies required; optional numpy/scipy only for generic WAV BPM detection).
- Executor (execute_choreography.py):
  Python 2.7 + SoftBank Robotics NAOqi Python SDK (naoqi, included with
  Choregraphe Suite 2.8).

HOW TO RUN & TEST ON SIMULATED NAO (CROSS-PLATFORM):
----------------------------------------------------
1. Launch Choregraphe Suite 2.8 with a virtual NAO connected (default port 9559).

2. Execute the choreography:
   - Linux / macOS (with pynaoqi on PYTHONPATH):
       PYTHONPATH=/path/to/pynaoqi/lib python execute_choreography.py 127.0.0.1 9559 --music rick_120s.mp3
     (or any host/port: python execute_choreography.py <IP> <PORT> --music rick_120s.mp3)

   - Windows (via Choregraphe Python 2.7 wrapper):
       .\run_sim.bat execute_choreography.py 9559 --music rick_120s.mp3
       .\run_sim.bat execute_choreography.py <IP> <PORT> --music rick_120s.mp3

3. Dry-run verification (no Choregraphe connection needed):
   - Linux / macOS:
       python execute_choreography.py dry_run
   - Windows:
       .\run_sim.bat execute_choreography.py dry_run

4. Regenerate the choreography plan (optional, choreography_plan.json included):
   - python nao_planner.py --music rick_120s.mp3

REPOSITORY STRUCTURE:
---------------------
- nao_planner.py          : Forward state-space A* choreography planner.
- audio_analyzer.py       : Pure-Python audio rhythm, bar energy, and section analyzer.
- execute_choreography.py : Cross-platform NAOqi execution runner with beat sync & stability.
- choreography_plan.json  : Generated 29-step choreography plan (< 120s).
- rick_120s.mp3           : 120s audio track ("Never Gonna Give You Up", 113.3 BPM).
- rick_120s.wav           : 120s WAV track used for exact per-bar energy/beat extraction.
- run_sim.bat             : Windows helper invoking Choregraphe Suite 2.8 Python 2.7.
- README.txt              : Setup, team info, and cross-platform execution instructions.
- RobotPositions/         : Mandatory, official intermediate, course, and motif motion scripts.
