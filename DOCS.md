# NAO Planning Challenge Documentation

This document explains the architecture, motion kinematics, AI planning pipeline, and simulator stabilization for the music-synchronized NAO dance system developed for the Fundamentals of Artificial Intelligence competition at the University of Bologna.

## 1. System architecture

The project takes a 120-second music track (Rick Astley - "Never Gonna Give You Up", calibrated at 113.3 BPM) and produces a music-synchronized classical STRIPS choreography on the humanoid NAO robot in Choregraphe Suite 2.8.

The architecture consists of four interconnected layers:

1. **Rhythm analysis (audio_analyzer.py)**: Extracts beat onsets, bar boundaries (2.12 seconds per 4-beat bar at 113.3 BPM), and dynamic root-mean-square energy envelopes across the track.
2. **Classical AI planning (nao_planner.py, domain.pddl, problem.pddl)**: Performs forward state-space search to optimize survey criteria (public engagement, human characterization, musical energy alignment, and stage coverage) while strictly adhering to the mandatory position progression.
3. **Execution engine (execute_choreography.py)**: Loads the resulting plan, coordinates background audio playback, handles direct joint angle interpolation via ALMotion, manages non-blocking locomotion steps, and prevents physical simulator falls.
4. **Motion library (RobotPositions/)**: Contains atomic keyframe dances, Choregraphe timeline exports, and layered composite moves that combine base stepping with simultaneous upper-body gestures.

## 2. Planning domain and classical STRIPS model

The competition rules specify that the choreography must follow six mandatory milestones in strict sequence:
- P1: 14-StandInit.py (initial ready pose)
- P2: 4-Arms_opening.py (introductory arm expansion)
- P3: 6-Crouch.py (center-stage drop)
- P4: 16-Sit.py (transition to ground)
- P5: 17-SitRelax.py (relaxed floor posture)
- P6: 11-Stand.py (rising back to feet)

Between these mandatory milestones, the planner must interleave at least five intermediate positions chosen from the candidate library. The entire performance must complete within 120.0 seconds and return the robot to its exact starting coordinates (net dx = 0, net dy = 0).

### STRIPS modeling (domain.pddl)

The planning domain models three core actions:
- **execute_mandatory**: Advances the current phase from phase(N) to phase(N+1), requiring the robot to match the valid precondition posture and establishing the postcondition posture.
- **execute_intermediate**: Executes a stationary dance movement while preserving the current posture and musical phase.
- **execute_displacement**: Executes a locomotion movement that shifts the robot between spatial grid nodes (pos_center, pos_north, pos_south, pos_east, pos_west).

### Multi-objective heuristic search (nao_planner.py)

Standard STRIPS solvers do not natively account for musical bar alignment or kinematic fluidity. To solve this, nao_planner.py implements an A* forward state-space search driven by a multi-objective cost function:

Move candidates are evaluated using physical kinematic parameters extracted directly from joint keyframe trajectories rather than arbitrary subjective scores:
- **Joint velocity (energy)**: Mean angular velocity in radians per second across all joints, distinguishing fast explosive dances (whip at 1.23 rad/s, sprinkler at 0.66 rad/s) from slow gestures (Hello at 0.20 rad/s, handkiss at 0.11 rad/s).
- **Motion amplitude (public impact)**: Maximum angular excursion across all joints (new_speedy at 4.17 rad, dab at 3.54 rad versus small arm gestures at < 1.4 rad).
- **Rhythm synchrony**: Exact mathematical offset between move duration and the 113.3 BPM musical beat (0.53s) and 4-beat bar (2.12s).
- **Human characterization**: Differentiates iconic pantomime and signature choreography (Rick Astley sway at 5.5, Saxophone at 5.0, finger snaps at 5.0) from plain walking steps (2.0) or zero poses (1.0).

```python
reward = (public_score * 3.0) + (human_score * 3.0) + space_bonus - (energy_error * 2.0) - (beat_error * 1.5)
cost_delta = max(0.5, 36.0 - reward)
new_g = g + cost_delta
```

The search state is tracked as a 9-tuple:
```python
state = (time, phase, posture, x, y, used_moves_tuple, plan_history, phase_move_count, visited_stage_flag)
```

Key search constraints enforced during expansion:
- **Positive edge weights**: Reformulating the cost as regret ensures non-negative step costs, preventing the infinite node expansions that occur when negative rewards are fed directly into a min-heap.
- **Stage boundaries**: The displacement tracker restricts coordinates to a 3x3 grid (x in [-1, 1], y in [-1, 1]).
- **Floor drop location**: P3 (6-Crouch) cannot execute unless x == 0 and y == 0, guaranteeing that the robot drops to the floor at center stage.
- **Final phase homing**: Any displacement action taken during Phase 6 must reduce the distance back to (0, 0).
- **Repetition limits**: High-energy signature moves (such as astley_arm_sway and composite steps) can execute up to two times across the routine, while standard moves execute at most once.

## 3. Layered composite movements

Executing separate walking steps followed by static arm gestures makes the performance appear disjointed and mechanical. Furthermore, pure walking steps consume 4.2 seconds while scoring low on audience engagement.

To solve this, the motion engine layers concurrent omnidirectional walking with upper-body dance routines:

### Mechanism
In NAOqi ALMotion, calling:
```python
motionProxy.setMoveArmsEnabled(False, False)
```
detaches arm joints from the walking pattern generator. This allows locomotion and arm keyframe trajectories to run simultaneously.

1. **Background locomotion**: `motionProxy.post.moveTo(dx, dy, theta)` starts a non-blocking translation step.
2. **Concurrent dance**: `motionProxy.angleInterpolation(names, keys, times, True)` drives arms, wrists, and head through expressive keyframes matched to the 113.3 BPM tempo.
3. **Synchronization**: `motionProxy.waitUntilMoveIsFinished()` ensures the step settles before the next scheduled move begins.

### Implemented composite moves
- **composite_diagleft_snap.py**: A diagonal step left (dx = 0.03m, dy = 0.02m) layered with a 4.24-second rhythmic finger-snap routine across arms and head.
- **composite_diagright_sway.py**: A diagonal step right (dx = -0.03m, dy = -0.02m) returning the robot to center stage while performing the Rick Astley arm sway.
- **composite_forward_groove.py**: A forward advance (dx = 0.04m) layered with rhythmic forearm rolls.
- **composite_backward_groove.py**: A backward return step (dx = -0.04m) layered with chest-level finger snaps.

### Modular pop dance motifs

Monolithic moves that run for 10 to 16 seconds from start to end (such as generic gym workouts or jazz saxophone pantomimes) disrupt the driving 80s dance-pop energy of "Never Gonna Give You Up" and feel robotic due to slow wind-up and wind-down phases.

To achieve continuous, fluent human-like dancing, the candidate library provides modular dance motifs quantized strictly to musical bars at 113.3 BPM (beat = 0.53 seconds, 1 bar = 2.12 seconds, 2 bars = 4.24 seconds):

- **motif_astley_groove.py** (4.24s, 2 bars): The iconic Rick Astley shoulder and arm sway from the music video, swaying across beats 2, 4, 6, and 8.
- **motif_disco_point.py** (4.24s, 2 bars): Classic 80s disco pointing (right hand high-right on beat 2, down to hip on beat 4; left hand high-left on beat 6, down on beat 8).
- **motif_pop_clap.py** (2.12s, 1 bar): High-energy syncopated claps hitting directly on snare drum beats 2 and 4.
- **motif_sprinkler.py** (4.24s, 2 bars): Classic party sprinkler dance with right hand behind the head while the left arm ticks forward across beats 1 through 4 and sweeps back smoothly across beats 5 through 8.
- **motif_dance_wave.py** (4.24s, 2 bars): Fluid pop arm roll and chest wave with rhythmic head bounces.
- **motif_finger_snap.py** (4.24s, 2 bars): Rhythmic finger snaps alternating left and right on the snare hits.
- **motif_sitting_kiss.py** (4.24s, 2 bars): Floor engagement gesture for the calm bridge (Phase 4), blowing a kiss and waving to the audience.

Because these motifs begin and end in neutral upper-body ready postures while preserving stable standing leg angles, they chain back to back seamlessly without awkward pauses or simulator tipping.

## 4. Simulator stability and kinematic bug fixes

The physics engine in Choregraphe Suite 2.8 exhibits severe contact instability with low virtual ground friction. Default Choregraphe behaviors frequently cause simulated robots to slip, tip over, or enter 30-second inverse kinematics recovery loops. The following fixes eliminate these failures:

### 1. Eliminating SitRelax tipping and stand-up loops
- **The problem**: In default Choregraphe SitRelax, the robot splays its legs outward and leans its torso back with hands behind the pelvis. In virtual physics, attempting to transition from this splayed posture causes feet to slip forward. The center of mass falls backward, triggering an automatic fall recovery routine that takes 25 to 30 seconds.
- **The fix**: execute_choreography.py defines a stable lap-rest posture (_SITRELAX_ANGLES). Knees remain bent, feet stay tucked beneath the thighs, and hands rest forward on the lap.
- **Standing up safely**: When rising from floor postures (Sit or SitRelax), the custom posture proxy (_FastPostureProxy) first interpolates the robot into a forward-tucked Crouch posture (_CROUCH_ANGLES) in 1.6 seconds. This shifts the center of gravity directly over the feet before StandInit executes, completing the stand-up in 3.7 seconds with zero tipping.
- **Duplicate stand prevention**: Adding "11-Stand" to the executor floor-move registry prevents the pre-execution loop hook from issuing a redundant StandInit command right before 11-Stand runs.

### 2. DanceMove ankle stabilization
- **The problem**: The raw keyframe export for DanceMove.py included an ankle pitch of -0.78 radians (-45 degrees backwards). This pulled the feet backward, causing the robot to flip onto its back instantly.
- **The fix**: Ankle pitch keyframes were clamped to 0.07 radians (neutral flat ground contact) while upper-body arm and head routines were preserved.

### 3. Velocity sanitization on extracted Choregraphe moves
- **The problem**: Choregraphe boxes (such as sprinkler, workout, Saxophone, Headbang) often have adjacent keyframes placed one frame apart (0.04 seconds) for step-cuts. Attempting to rotate a joint by 1.5 radians in 0.04 seconds results in a velocity of 37 rad/s, which throws an ALMotion max velocity violation error.
- **The fix**: An automatic sanitization script calculates the angular delta between consecutive keyframes and clamps the time delta:
```python
dt_min = abs(k[i] - k[i-1]) / max_velocity
dt = max(dt_raw, dt_min, 0.20)
```
A uniform 0.65-second lead-in period is also added to the first keyframe so joints smoothly transition from their current positions.

## 5. Directory structure

```
NAO/
├── audio_analyzer.py             # Pure-Python beat and energy parser
├── choreography_plan.json        # Generated 15-move choreography plan with timing
├── domain.pddl                   # Formal STRIPS domain definition
├── problem.pddl                  # Generated STRIPS problem instance
├── nao_planner.py                # Multi-objective A* search and PDDL generator
├── execute_choreography.py       # Execution runtime with stability proxies
├── rick_120s.mp3                 # Calibrated audio track (113.3 BPM, 120s)
├── run_sim.bat                   # Wrapper configuring Choregraphe Python 2.7 environment
└── RobotPositions/               # Motion script library
    ├── 14-StandInit.py           # Mandatory P1
    ├── 4-Arms_opening.py         # Mandatory P2
    ├── 6-Crouch.py               # Mandatory P3
    ├── 16-Sit.py                 # Mandatory P4
    ├── 17-SitRelax.py            # Mandatory P5
    ├── 11-Stand.py               # Mandatory P6
    ├── astley_arm_sway.py        # Signature Rick Astley rhythmic sway
    ├── composite_diagleft_snap.py  # Layered diagonal step + finger snap
    ├── composite_diagright_sway.py # Layered diagonal return + arm sway
    ├── composite_forward_groove.py # Layered forward step + sway
    ├── composite_backward_groove.py# Layered backward step + snap
    ├── Disco.py                  # High-energy chorus dance
    ├── sprinkler.py              # Extracted 80s Sprinkler routine
    ├── Saxophone.py              # Extracted musical performance dance
    ├── Headbang.py               # Extracted high-energy finale
    ├── workout.py                # Extracted rhythmic fitness routine
    ├── sitting_handkiss.py       # Audience engagement floor routine
    └── cgrFiles/                 # Original Choregraphe archive packages
```

## 6. How to run

### Prerequisites
- Softbank Robotics Choregraphe Suite 2.8 installed at `C:\Program Files (x86)\Softbank Robotics\Choregraphe Suite 2.8`.
- Virtual NAO robot running inside Choregraphe connected to port 9559.

### Step 1: Generate or update the choreography plan
To run the rhythm analysis, perform the multi-objective A* search, and generate problem.pddl and choreography_plan.json:
```powershell
python nao_planner.py
```

### Step 2: Dry-run verification (no robot connection required)
To verify syntax, imports, joint counts, and sequencing in under two seconds:
```powershell
.\run_sim.bat execute_choreography.py dry_run
```

### Step 3: Live execution on virtual or physical NAO
With Choregraphe connected to port 9559:
```powershell
.\run_sim.bat execute_choreography.py 9559 --music rick_120s.mp3
```
The execution engine will wake up the robot, start synchronized audio playback, execute all 15 planned steps, and hold the final standing pose at completion. Total actual run time is approximately 104 seconds, comfortably under the 120-second competition limit.
