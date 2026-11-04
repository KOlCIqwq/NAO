================================================================================
NAO Planning Challenge - Song-Driven Choreography Planning System
Fundamentals of Artificial Intelligence - Universita di Bologna
================================================================================

TEAM INFORMATION:
-----------------
Student Name: [Your Name]
Student Email: [Your Institutional Email]

PROJECT OVERVIEW:
-----------------
This project implements an automated, song-driven AI planning system for generating
a 2-minute rhythmic choreography for the NAO humanoid robot (simulated or physical).
Given ANY generic song file (WAV, MP3, OGG, FLAC, M4A), the system:
1. Ingests and analyzes the song: extracts exact duration (capped at <= 120.0s) and
   RMS loudness/energy profile across time slices.
2. Optimizes move selection via Music-Guided Simulated Annealing: aligns high-energy dance
   moves (e.g. Disco, new_speedy, ThrillerClap) with the song's chorus and energy peaks,
   and calm gestures (Hello, 2-Right_arm, WipeForehead) with quiet intro/verse sections.
3. Guarantees all contest requirements via Classical STRIPS/PDDL Planning:
   - Sequential execution of all 6 mandatory positions (P1 -> P2 -> P3 -> P4 -> P5 -> P6):
     P1: 14-StandInit.py
     P2: 4-Arms_opening.py
     P3: 6-Crouch.py
     P4: 16-Sit.py
     P5: 17-SitRelax.py
     P6: 11-Stand.py
   - At least 5 intermediate moves from the pool.
   - Posture transition constraints (Standing -> Crouch -> Sitting -> Standing).
   - Total duration strictly within the 2-minute (120.0s) limit.

HOW TO RUN ON ANY GIVEN SONG:
-----------------------------
1. Generate a Choreography Plan Tailored to a Specific Song:
   python nao_planner.py --music path/to/your_song.mp3
   (Or .wav, .flac, .ogg, .m4a - works on any generic song!)

   Example with the bundled classic hit:
   python nao_planner.py --music classic_hit.wav

2. Execute the Planned Choreography on Virtual NAO in Choregraphe:
   run_sim.bat execute_choreography.py <PORT> --music path/to/your_song.mp3
   Example on active simulator port (e.g. 55802):
   run_sim.bat execute_choreography.py 55802 --music classic_hit.wav

3. Execute Without Audio (Robot Movements Only):
   run_sim.bat execute_choreography.py 55802

ARCHITECTURE:
-------------
- audio_analyzer.py: Zero-dependency song analyzer extracting duration and RMS energy envelope.
- nao_planner.py: Classical STRIPS/PDDL planner (A* search) with music-guided local search.
- domain.pddl & problem.pddl: Formal PDDL specification of postures, phases, and preconditions.
- execute_choreography.py: Runner for simulated NAO (Python 2.7 / 3 compatible) with parallel audio sync.
- classic_hit.wav: 114s, 120 BPM classical dance hit for instant out-of-the-box testing.
