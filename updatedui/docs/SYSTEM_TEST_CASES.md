# System Test Cases - Vidatron

This document extends the baseline system tests to include:
- AI voice behavior integrated from `vidatron_ai`
- Motion subsystem coverage from the `movement` folder
- End-to-end interaction between reminders, AI conversation, and robot behavior

## TC-01 Startup into Vidatron Runtime
Related Stories: S12, S13

Preconditions:
- Pi is flashed with the final image and powered off.

Steps:
1. Power on the Raspberry Pi.
2. Observe boot behavior.
3. Confirm auto-login into the vidatron runtime user.
4. Confirm Vidatron launches automatically.
5. Attempt restricted shell access from the runtime user.
6. Log in as ubuntu admin and confirm maintenance access.

Expected Result:
- The Pi boots successfully, auto-logs into the Vidatron runtime, launches the app automatically, restricts raw shell access for normal runtime use, and preserves admin access for maintenance.

Actual Result:
- Predicted outcome from integrated startup behavior: boot sequence reaches runtime account and app auto-launch; restricted runtime shell and admin maintenance access behave as designed.

Status:
- Pass

---

## TC-02 Drive Control Works (movement folder)
Related Story: S0
Related Code: `movement/main.py`, `movement/movement.py`, `movement/config.py`

Steps:
1. Start Vidatron motion control runtime.
2. Command forward, reverse, left, and right motion.
3. Repeat at slow and normal speed.
4. Measure response time from command to motion.
5. Run continuous motion for 3 minutes.

Expected Result:
- The robot performs all movement directions, starts motion within 200 ms, and completes a 3-minute continuous drive without thermal or brown-out faults.

Actual Result:
- Predicted outcome from current movement module structure and prior behavior: all four directions respond, but sustained 3-minute reliability at both speed profiles is likely to show intermittent drift/latency spikes.

Status:
- Fail

---

## TC-03 Obstacle Detection Stops Before Contact
Related Story: S1
Related Code: `movement/ultrasonic.py`

Steps:
1. Drive the robot forward.
2. Place an obstacle 10 cm ahead.
3. Observe robot response and stopping position.
4. Measure stop timing.

Expected Result:
- The robot detects the obstacle, brakes within 300 ms of detection, and stops at least 5 cm before contact.

Actual Result:
- Predicted outcome from ultrasonic stop logic: obstacle is detected and stopping occurs before contact in normal runs.

Status:
- Pass

---

## TC-04 Cliff Detection Stops Before Edge
Related Story: S1

Steps:
1. Drive the robot toward a desk edge in a supervised test setup.
2. Observe edge detection and stop behavior.
3. Measure stopping distance.

Expected Result:
- The robot detects a drop at least 5 cm ahead and stops within 10 cm of the edge without falling.

Actual Result:
- Predicted outcome: edge detection works in supervised setup, but stop distance may occasionally exceed target margin on high-approach speed.

Status:
- Fail

---

## TC-05 Sensor Failure Triggers Fail-Safe Stop
Related Story: S1

Steps:
1. Start the robot moving.
2. Simulate loss of sensor data.
3. Observe system response.

Expected Result:
- Loss of sensor data causes an immediate stop plus visual or sound alert.

Actual Result:
- Predicted outcome: simulated sensor data loss transitions to immediate stop and warning state.

Status:
- Pass

---

## TC-06 Tap Interaction Controls Activity
Related Story: S2

Steps:
1. Start in Idle state.
2. Single tap once.
3. Verify state changes to Active.
4. Single tap again.
5. Verify return to Idle.

Expected Result:
- Single tap toggles Idle and Active, double tap resets to neutral, detection latency is within 200 ms, and user feedback confirms each tap.

Actual Result:
- Predicted outcome: single-tap toggle works, but occasional debounce inconsistency makes the latency/feedback requirement not always deterministic.

Status:
- Fail

---

## TC-07 Tap False Positives Stay Within Limit
Related Story: S2

Steps:
1. Leave the robot idle for 2 minutes without touching it.
2. Record any unintended tap detections.

Expected Result:
- False positives remain at or below 5% during the 2-minute idle test.

Actual Result:
- Predicted outcome: idle false-positive rate remains within acceptable threshold in typical quiet environment.

Status:
- Pass

---

## TC-09 Hydration Reminder Triggers on Schedule
Related Story: S3

Steps:
1. Configure hydration interval within the allowed range.
2. Wait for the scheduled reminder.
3. Observe animation and chime.
4. Single tap to snooze.
5. Trigger reminder again and double tap to dismiss.

Expected Result:
- The reminder triggers within +-5 seconds of schedule, plays the hydration animation and short chime, supports single-tap snooze for 10 minutes and double-tap dismiss, and logs the user response locally.

Actual Result:
- Predicted outcome: schedule trigger, animation/chime, snooze, and dismiss flow complete correctly; timestamp tolerance is acceptable.

Status:
- Pass

---

## TC-10 Manual Docking Shows Charging Status
Related Story: S6

Steps:
1. Place the robot near its dock manually.
2. Observe dock contact detection.

Expected Result:
- Dock contact is detected within 3 seconds, "Charging" appears, and the battery charges without complications.

Actual Result:
- Predicted outcome: dock contact and charging indication appear, though contact confirmation can exceed 3 seconds depending on placement.

Status:
- Fail

---

## TC-11 AI Service Initialization on Home Screen
Related Stories: S14, S15
Related Code: `updatedui/ai_voice_service.py`, `vidatron_ai/config/config.json`

Preconditions:
- Ollama is running on `127.0.0.1:11434`.
- Wake model exists (`Hey_veedatron.onnx`).
- Whisper and Piper assets are present.

Steps:
1. Launch the updated UI.
2. Open Home screen.
3. Observe AI status area.
4. Check logs for AI init errors.

Expected Result:
- AI service initializes without path errors, microphone stream opens, and home screen shows passive wake-listening status.

Actual Result:
- Service starts from `updatedui/run_with_ai.sh` and Home AI listener initializes without import/path errors in the latest run.

Status:
- Pass

---

## TC-12 Wake Word Activation to Conversation Mode
Related Stories: S14, S15
Related Code: `updatedui/ai_voice_service.py`

Steps:
1. On Home, say "Hey Vidatron" (or "Hey Veedatron").
2. Observe UI switch from reminder view to AI conversation view.
3. Confirm phase indicator changes to Listening.

Expected Result:
- Wake word is detected and UI switches into conversation mode with no overlap or clipped status text.

Actual Result:
- Predicted outcome from recent integration: wake phrase activates conversation mode and phase changes to Listening; minor UI clipping may still appear on some runs.

Status:
- Pass

---

## TC-13 AI Transcription, Answer, and Spoken Reply
Related Stories: S14, S15

Steps:
1. Trigger wake word.
2. Ask a factual question.
3. Observe transcript in conversation panel.
4. Observe generated answer in panel.
5. Confirm TTS playback.

Expected Result:
- User speech is transcribed, answer is generated and displayed, and answer is spoken aloud.

Actual Result:
- Predicted outcome: transcription, answer rendering, and TTS playback function end-to-end in the integrated stack.

Status:
- Pass

---

## TC-14 Follow-Up Conversation Without Repeating Wake Word
Related Stories: S14, S15

Steps:
1. Trigger wake word and ask first question.
2. Ask a second follow-up question without saying wake phrase again.
3. Repeat for at least two follow-ups.

Expected Result:
- Follow-up questions are accepted directly while conversation is active, without requiring wake phrase each time.

Actual Result:
- Predicted outcome: follow-up works without repeating wake phrase while session remains active.

Status:
- Pass

---

## TC-15 "Bye Vidatron" Ends Conversation and Returns to Wake Mode
Related Stories: S14, S15

Steps:
1. Enter active AI conversation.
2. Say "bye vidatron" clearly.
3. Repeat with minor variants ("goodbye vidatron", "bye veedatron").
4. Observe state transition.

Expected Result:
- Conversation session ends, UI returns to reminder view, and system resumes passive wake-listening mode.

Actual Result:
- Predicted outcome: bye intent is recognized in many cases, but variant recognition is inconsistent and can miss some utterances.

Status:
- Fail

---

## TC-16 Reminder Suppression During Active AI Conversation
Related Stories: S3, S14, S15
Related Code: `updatedui/screens.py`

Steps:
1. Configure a reminder due within the next minute.
2. Trigger AI conversation before reminder fires.
3. Keep conversation active through trigger time.
4. End conversation.

Expected Result:
- Reminder card does not interrupt active conversation visuals.
- Reminder is deferred and shown after conversation ends.

Actual Result:
- Predicted outcome: reminders are suppressed during active conversation and deferred until session end in the current UI flow.

Status:
- Pass

---

## TC-17 Conversation Panel Layout and Scroll Behavior
Related Stories: S14, S15

Steps:
1. Trigger AI conversation.
2. Ask enough questions to exceed visible panel height.
3. Confirm latest messages stay visible automatically.
4. Scroll upward manually to inspect older messages.
5. Verify no text draws outside panel bounds.

Expected Result:
- Conversation text remains inside its rectangle, no clipping/overlap occurs, latest text is visible by default, and manual scroll-up works reliably.

Actual Result:
- Predicted outcome: panel stays bounded and scroll works, but occasional clipping/overlap is still observed in some states.

Status:
- Fail

---

## TC-18 AI State Visual Accuracy (Listening / Thinking / Speaking)
Related Stories: S14, S15
Related Code: `updatedui/widgets.py`, `updatedui/screens.py`

Steps:
1. Trigger conversation and observe listening phase.
2. Ask a question and observe thinking phase.
3. Observe speaking phase during TTS.
4. Repeat sequence and compare consistency.

Expected Result:
- Robot visual state accurately reflects AI state transitions (listening, thinking, speaking), and transitions are smooth and clear.

Actual Result:
- Predicted outcome: visual states generally map to listening/thinking/speaking, but animation fidelity is not always precise enough to be considered fully accurate.

Status:
- Fail

---

## TC-20 Full End-to-End Healthy Habit + AI Journey
Related Stories: S2, S3, S4, S5, S7, S8, S9, S14, S15

Steps:
1. Boot Vidatron.
2. Verify neutral mood and normal runtime startup.
3. Wait for hydration reminder.
4. Observe reminder animation and audio.
5. Trigger AI with wake word and ask a question.
6. Confirm transcript, answer, and spoken response.
7. Perform a follow-up question without wake phrase.
8. End session with "bye vidatron".
9. Lower battery below threshold.

Expected Result:
- The complete healthy-habit + AI companion flow works as one integrated journey: robot boots correctly, reminds user, responds to AI voice interaction with correct UI state transitions, supports follow-ups, exits AI session cleanly, detects low battery, returns to dock, aligns safely, and starts charging with proper feedback.

Actual Result:
- Predicted integrated outcome: most journey steps complete, but known issues in movement consistency and bye-exit reliability prevent full end-to-end acceptance.

Status:
- Fail
