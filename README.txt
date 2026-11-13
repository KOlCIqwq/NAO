================================================================================
NAO Planning Challenge - Music-Synchronized Choreography Planning System
Fundamentals of Artificial Intelligence - Universita di Bologna
================================================================================

TEAM INFORMATION:
-----------------
Student Name(s): [Your Name / Team Members]
Student Email(s): [Your Institutional Email(s)]
Project Repository: [Link to your GitHub / Drive / Dropbox repository]

PROJECT OVERVIEW:
-----------------
This project implements an automated, music-synchronized classical AI planning system
for the NAO humanoid robot (tested on simulated NAO in Choregraphe 2.8 and compatible
with physical robots).

Given any chosen audio track (specifically calibrated for Rick Astley - "Never Gonna Give You Up",
113.3 BPM, ~105s duration), the system:
1. Audio Rhythm & Structure Analysis:
   - Uses a zero-dependency pure-Python audio parser (audio_analyzer.py) to extract tempo
     (BPM), beat intervals (~0.53s), bar intervals (~2.12s), and energy profiles.
2. Multi-Objective Heuristic Search & Classical STRIPS Planning:
   - Evaluates all candidate moves in the pool against the 7 contest survey criteria:
     * Theme / Story representation
     * Rhythmic coherence with 113.3 BPM musical bars
     * Kinematic transition fluidity
     * Public involvement score
     * Human characterization score
     * Stage space exploration with strict net zero displacement (dx = 0, dy = 0)
   - Solves domain.pddl and problem.pddl via state-space A* search with no hardcoded move assignments.
   - Enforces the strict sequence of all 6 mandatory positions (P1 -> P2 -> P3 -> P4 -> P5 -> P6):
       P1: 14-StandInit.py
       P2: 4-Arms_opening.py
       P3: 6-Crouch.py
      P4: 16-Sit.py
      P5: 17-SitRelax.py
      P6: 11-Stand.py
   - Interleaves intermediate dance positions across performance phases instead of
     clumping them together, as specified by contest guidelines (Slide 15):
       * Phase 1 (Intro rhythm & greetings): astley_arm_sway.py, Hello.py, finger_snap.py, ThrillerClap.py
       * Phase 2 (Groove, Bézier expressions & locomotion): ThrillerSnapSnap.py, new_dance.py, 9-Diagonal_left.py, 10-Diagonal_right.py
       * Floor & Sitting Groove: 6-Crouch -> 16-Sit -> sitting_handkiss.py -> 17-SitRelax -> 11-Stand
       * Phase 6 (Chorus dance & celebration): high_clap.py, Disco.py
3. Contest Survey Optimization (Slide 11 Criteria):
   - Theme & Human Characterization: Captures Rick Astley's signature moves (finger snap,
     parallel double forearm roll, and the side-to-side arm sway).
   - Space Usage & Zero Net Displacement: Locomotion steps explore the stage while ensuring
     exact return to origin (dx = 0, dy = 0).
   - Fluidity & Safe Execution: Custom posture interpolation avoids joint snapping, eliminates
     abrupt simulator pauses, and protects against Max Velocity violations.
   - Time Constraint: Total execution completes in ~104.1 seconds (17 moves), strictly under the 120s limit.

SIMULATION STABILITY & KINEMATIC BUG FIXES:
------------------------------------------
Extensive testing inside the Choregraphe 2.8 simulator resolved several critical kinematic
and execution bugs:
1. Sitting Transition Stabilization:
   - Problem: Default inverse kinematics (IK) solver in Choregraphe caused the simulated NAO
     to collide with the ground plane when moving between Sit and SitRelax, causing left-side
     tipping and 30-second solver timeouts.
   - Fix: Implemented direct joint angle interpolation with anatomically verified joint angles
     (_SIT_ANGLES, _SITRELAX_ANGLES) completing smoothly in 2.5s with zero tipping.
2. Floor Move Continuity:
   - Problem: The executor previously assumed all dance moves started from StandInit, causing
     the robot to attempt standing up during sitting sequences (e.g., sitting_handkiss).
   - Fix: Classified sitting moves (sitting_mood, sitting_handkiss, sitting_wavess) as floor
     actions so the robot remains seated seamlessly throughout the floor routine.
3. Upper-Body Isolation for Standing and Sitting Dances:
   - Problem: Moves such as finger_snap had corrupted leg keyframes that tilted the robot onto
     its heels, causing it to fall backwards onto the floor.
   - Fix: Filtered out leg joint keyframes (Hip, Knee, Ankle) for standing upper-body moves and
     sitting dances, keeping feet flat on the floor and the torso stably anchored.
4. Bézier Curve Interpolation Support:
   - Problem: Complex moves like new_dance export multi-dimensional Bézier curves rather than
     flat angle arrays, throwing an ALMotion::angleInterpolation dimension mismatch error.
   - Fix: Added automatic detection of Bézier keyframe structures to route calls to the native
     angleInterpolationBezier handler.
5. Standing Up & Final Pose Stability:
   - Problem: Calling motion.rest() at the end cut motor stiffness, causing gravity simulation
     to drop the robot. Additionally, standing directly from SitRelax caused feet to slip outward.
   - Fix: Added a two-stage standup (tucking knees into Sit before rising to StandInit) and
     maintained motor stiffness at the end by smoothly transitioning upper-body joints to a neutral
     standing pose.

REQUIRED LIBRARIES & ENVIRONMENT:
---------------------------------
- Python 3.8+ (for generating plans via nao_planner.py - zero external dependencies required;
  standard Python library wave, struct, json, heapq, math).
- SoftBank Robotics Choregraphe Suite 2.8 (with simulated NAO or NAOqi SDK).
- Python 2.7 NAOqi runtime (provided by Choregraphe via run_sim.bat).

HOW TO RUN:
-----------
1. Generate the Choreography Plan (Python 3):
   python nao_planner.py --music rick_120s.mp3

   This analyzes the song, builds domain.pddl/problem.pddl, executes A* state-space
   search, and exports choreography_plan.json.

2. Execute on Simulated NAO (Choregraphe):
   - Launch Choregraphe and open the virtual robot (default port 9559).
   - Run the execution script:
       .\run_sim.bat execute_choreography.py 9559 --music rick_120s.mp3
   - (Or with any custom port):
       .\run_sim.bat execute_choreography.py <PORT> --music rick_120s.mp3

3. Dry-Run / Verification Mode (no Choregraphe connection needed):
   .\run_sim.bat execute_choreography.py dry_run

4. Visualizing the Dance:
   - In Choregraphe GUI: Keep the 3D Robot View open while running on port 9559.
   - In Web Browser: Open visualize_choreography.html in any modern browser for
     interactive 3D skeletal playback synchronized with rick_120s.mp3.
   - Real-time CLI Telemetry: Run .\run_sim.bat record_and_monitor.py 60
     to stream real-time joint positions and limb heights from port 9559.

REPOSITORY STRUCTURE:
---------------------
- nao_planner.py           : Classical STRIPS/PDDL planner (A* search) with multi-objective survey heuristics.
- domain.pddl              : STRIPS domain specifying postures, phases, locomotion, and preconditions.
- problem.pddl             : Problem instance automatically generated for the chosen music.
- audio_analyzer.py        : Zero-dependency song analyzer (tempo, BPM, bar intervals, energy).
- execute_choreography.py  : Robot execution runner with synchronized background audio, posture blending,
                             and simulator stability patches.
- choreography_plan.json   : Output plan with step-by-step timings and posture transitions.
- rick_120s.mp3            : 120-second cut of "Never Gonna Give You Up" (~113.3 BPM).
- visualize_choreography.html: Standalone 3D choreography visualizer with audio synchronization.
- record_and_monitor.py    : Real-time pose and joint telemetry monitor for port 9559.
- run_sim.bat              : Wrapper invoking the Choregraphe Python 2.7 NAOqi SDK environment.
- RobotPositions/          : Position scripts and motion trajectories (including astley_arm_sway.py).
