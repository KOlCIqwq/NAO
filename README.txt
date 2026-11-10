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
2. Classical STRIPS/PDDL Phase-Interleaved Planning:
   - Solves domain.pddl and problem.pddl via state-space A* search.
   - Enforces the strict sequence of all 6 mandatory positions (P1 -> P2 -> P3 -> P4 -> P5 -> P6):
       P1: 14-StandInit.py
       P2: 4-Arms_opening.py
       P3: 6-Crouch.py
       P4: 16-Sit.py
       P5: 17-SitRelax.py
       P6: 11-Stand.py
   - Interleaves at least 5 intermediate dance positions across performance phases instead of
     clumping them together, as specified by contest guidelines (Slide 15):
       * Phase 1 (Intro rhythm): finger_snap.py
       * Phase 2 (Verse groove & locomotion): 8-Move_backward.py, 7-Move_forward.py, 3-Double_movement.py
       * Floor Bridge: 6-Crouch -> 16-Sit -> 17-SitRelax -> 11-Stand
       * Phase 6 (Chorus dance & outro): astley_arm_sway.py, Hello.py
3. Contest Survey Optimization (Slide 11 Criteria):
   - Theme & Human Characterization: Captures Rick Astley's signature moves (finger snap,
     parallel double forearm roll, and the side-to-side arm sway).
   - Space Usage & Zero Net Displacement: Forward and backward locomotion steps explore the
     stage while ensuring exact return to origin (dx = 0, dy = 0).
   - Fluidity & Safe Execution: Custom posture interpolation avoids joint snapping, eliminates
     abrupt simulator pauses, and protects against Max Velocity violations.
   - Time Constraint: Total execution completes in ~98-105 seconds, strictly under the 120s limit.

REQUIRED LIBRARIES & ENVIRONMENT:
---------------------------------
- Python 3.8+ (for generating plans via nao_planner.py - zero external dependencies required;
  standard Python library wave, struct, json, heapq, math).
- SoftBank Robotics Choregraphe Suite 2.8 (with simulated NAO or NAOqi SDK).
- Python 2.7 NAOqi runtime (provided by Choregraphe via run_sim.bat).

HOW TO RUN:
-----------
1. Generate the Choreography Plan (Python 3):
   python nao_planner.py --music rick.mp3

   This analyzes the song, builds domain.pddl/problem.pddl, executes A* state-space
   search, and exports choreography_plan.json.

2. Execute on Simulated NAO (Choregraphe):
   - Launch Choregraphe and open the virtual robot (default port 9559).
   - Run the execution script:
       .\run_sim.bat execute_choreography.py 9559 --music rick.mp3
   - (Or with any custom port):
       .\run_sim.bat execute_choreography.py <PORT> --music rick.mp3

3. Dry-Run / Verification Mode (no Choregraphe connection needed):
   .\run_sim.bat execute_choreography.py dry_run

REPOSITORY STRUCTURE:
---------------------
- nao_planner.py           : Classical STRIPS/PDDL planner (A* search) with phase-interleaved allocation.
- domain.pddl              : STRIPS domain specifying postures, phases, locomotion, and preconditions.
- problem.pddl             : Problem instance automatically generated for the chosen music.
- audio_analyzer.py        : Zero-dependency song analyzer (tempo, BPM, bar intervals, energy).
- execute_choreography.py  : Robot execution runner with synchronized background audio and posture blending.
- choreography_plan.json   : Output plan with step-by-step timings and posture transitions.
- rick.mp3                 : Performance audio track ("Never Gonna Give You Up", ~113.3 BPM).
- run_sim.bat              : Wrapper invoking the Choregraphe Python 2.7 NAOqi SDK environment.
- RobotPositions/          : Position scripts and motion trajectories (including astley_arm_sway.py).
