# System Test Plan - Vidatron

## 1. Test Objectives
The purpose of system testing for Vidatron is to validate that the final integrated system works correctly, safely, and reliably across its main user journeys before final submission and demo.

This plan now covers both:
- core robot behavior (movement, safety, reminders, docking, runtime setup), and
- AI voice interaction integrated from `vidatron_ai` into `updatedui` (wake word, transcription, response generation, TTS, conversation UI states, follow-ups, and session exit).

System testing focuses on confirming that the completed product supports:
- healthy habit reminders and expressive interaction,
- safe movement and obstacle/cliff handling,
- docking and charging behavior,
- audio and visual feedback,
- runtime startup and user separation on Raspberry Pi, and
- AI conversation behavior end-to-end on the Home screen.

The objectives of this testing phase are to:
- verify that all selected final-sprint features function together as one integrated system,
- confirm that core user journeys complete successfully from start to finish,
- identify any remaining high- or medium-severity defects,
- validate focused non-functional requirements such as response time, reliability, usability, and basic runtime security,
- confirm AI conversation quality gates (wake detect, transcript display, follow-up flow, exit intent handling, and reminder deferral during active conversation),
- confirm readiness for the final advisor demo and release submission.

---

## 2. Scope
System testing includes the final implemented user stories and integrated modules:

- **S0** - Basic Drive and Motor Control  
  Includes validation of movement implementation in `movement/main.py`, `movement/movement.py`, and `movement/config.py`.

- **S1** - Cliff and Obstacle Avoidance  
  Includes ultrasonic/safety behavior (`movement/ultrasonic.py`) and fail-safe stop behavior.

- **S2** - Tap-to-Trigger
- **S3** - Hydration Reminder Animation
- **S6** - Manual Docking and Charge Status
- **S12** - Set Up Raspberry Pi and Environment
- **S13** - Configure Runtime and Admin Users

- **AI Voice Integration (updated scope)**  
  Integrated behavior spanning `updatedui` + `vidatron_ai`, including:
  - wake word detection,
  - Whisper transcription,
  - local/cloud response routing,
  - Piper TTS playback,
  - Home-screen AI conversation panel and state visuals,
  - follow-up questions without repeating wake phrase,
  - "bye vidatron" (and variants) to end session,
  - reminder suppression/defer while user is actively conversing.

### Out of Scope
- **S11 - Spoken Prompts (Stretch)** remains excluded from mandatory system testing as a stretch story.
- Large documentation-only artifacts under `full_updated_ai_code/` are not runtime validation targets.

---

## 3. Core User Journeys
The following integrated user journeys are selected for final system testing:

1. **Startup and runtime journey**  
   Raspberry Pi boots directly into Vidatron runtime with correct environment, user setup, and startup behavior.

2. **Safe interaction and movement journey**  
   User activates robot through tap input, robot moves, and safely avoids obstacles and desk edges.

3. **Habit reminder journey**  
   Robot triggers hydration reminder on schedule, shows reminder animation, plays audio, and supports tap response.

4. **Expressive behavior journey**  
   Robot displays correct mood/state visuals for boot, idle, reminder, listening, thinking, and speaking states.

5. **AI voice conversation journey**  
   Wake phrase activates assistant, user question is transcribed, answer is generated and spoken, follow-ups work without re-wake, and "bye vidatron" exits to passive wake mode.

6. **Reminder + AI coexistence journey**  
   While AI conversation is active, reminder cards do not interrupt the conversation UI; reminders are deferred and shown after conversation ends.

7. **Battery and charging journey**  
   User can plug robot in and verify charging status behavior.

8. **Docking and maintenance journey**  
   Docking locator/calibration behavior functions correctly, and system can be validated in local emulated environment.

---

## 4. Test Types

### Functional System Testing
Functional testing verifies end-to-end behavior for selected user journeys, including:
- movement and safety sensing,
- tap interaction,
- reminder scheduling and display,
- battery monitoring and docking,
- startup/runtime behavior,
- AI wake/transcribe/respond/speak loop,
- AI follow-up and exit behavior,
- AI/reminder interaction rules.

### Non-Functional Testing
Focused non-functional checks include:
- command latency and response time,
- sensor stop timing,
- battery gauge and charging status behavior,
- sound playback timing,
- reboot persistence,
- reliability across repeated trials,
- runtime/admin security separation,
- usability of visible and audible feedback,
- AI wake latency and end-to-end response time,
- transcript panel readability (no clipping, overlap, or overflow outside bounds),
- conversation scroll behavior under long exchanges.

### Acceptance Testing
Acceptance testing confirms Vidatron is acceptable for final demo and submission by verifying normal end-to-end journeys for both robot and AI interaction behavior.

### Regression Testing
After any defect fixes, impacted test cases are re-run and documented in execution logs.
Special regression focus areas:
- startup/runtime permissions,
- movement safety stop paths,
- AI state transitions (waiting/listening/thinking/speaking/follow-up),
- "bye" exit reliability,
- reminder deferral and restoration after AI session.

---

## 5. Test Environment and Tools
Testing will be performed using:
- physical Vidatron robot prototype,
- Raspberry Pi with custom Ubuntu runtime image,
- touch/tap sensor, docking station, battery monitoring components, display, motors, and safety sensors,
- movement subsystem code in `movement/`,
- integrated UI in `updatedui/`,
- AI stack in `vidatron_ai/` (wake model, Whisper, Ollama, Piper),
- QEMU local emulation environment (where applicable),
- manual test scripts/checklists,
- stopwatch/timer for latency and timing checks,
- GitHub documentation and execution logs for recording results.

### AI-Specific Preconditions
Before AI test execution:
- Ollama service reachable on `127.0.0.1:11434`,
- wake model file available (e.g. `Hey_veedatron.onnx`),
- Whisper binary/model paths valid,
- Piper voice model path valid,
- openWakeWord feature resources present (`melspectrogram.onnx`, `embedding_model.onnx`).

---

## 6. Entry and Exit Criteria

### Entry Criteria
- Integrated build is deployable and boots on target hardware.
- Required hardware components are connected and functional.
- AI dependencies and models are installed and path-resolved for the current machine.
- System test cases are baselined (`SYSTEM_TEST_CASES.md`).

### Exit Criteria
- All critical and high-severity test cases pass.
- No unresolved blocker defects remain for demo journeys.
- Key end-to-end flows pass at least once in a clean run:
  - startup,
  - movement safety,
  - reminder flow,
  - AI conversation flow (wake, response, follow-up, bye exit),
  - reminder deferral during AI session,
  - charging/docking flow.
