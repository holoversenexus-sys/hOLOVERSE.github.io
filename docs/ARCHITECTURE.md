# Autonomous AR Development Agent Architecture

## Vision
An autonomous agent that designs, builds, tests, and deploys spatial-computing features end-to-end. The system fuses retrieval-augmented generation (RAG), reinforcement learning (RL), and simulation feedback loops to continuously improve AR capabilities.

## Core Capabilities
- **Spatial Computing Expertise:** Scene understanding, SLAM/visual-inertial odometry integration, physics-aware interactions, and real-time rendering constraints.
- **Advanced AI Tooling:** RAG for grounded code generation and documentation synthesis; RL for policy optimization over tool selections and iterative build actions.
- **Autonomous DevOps:** Manages repositories, runs build pipelines, executes tests, and deploys artifacts (Unity/XR, native mobile, webXR) with observability hooks.
- **Self-Optimization:** Tracks rewards from compilation success, test coverage, performance metrics, and user telemetry to refine action policies.

## High-Level Architecture
```
[User/Goal] -> [Planner] -> [RAG Synthesizer] -> [Action Policy (RL)]
            -> [Tool Executor] -> [Build/Test/Deploy Pipelines]
            -> [Sensors: Logs, Metrics, Scene Simulators]
            -> [Reward Shaper & Memory Store]
```

## Large Action Model (LAM) autonomous flow
1. **Perception:** Normalize raw inputs (text, screenshots, audio metadata) into structured observations with tokens and modality tags.
2. **Intent Recognition:** Extract the user goal and constraints from the observation (heuristics now, policy/LLM later).
3. **Task Decomposition:** Use the planner to break the intent into ordered steps with rationales and dependencies.
4. **Action Planning + Memory:** RAG synthesizes a draft using retrieved exemplars; the policy selects the next tool using encoded state plus memory-backed plan context.
5. **Execution:** Tool executor runs the chosen action (Unity automation, builds, tests) and emits telemetry that feeds reward shaping and future policy updates.

The Python harness in `src/agent/lam.py` wires these stages so they can be swapped for production components (e.g., perception via OCR/ASR, intent via LLM, action planning via RL), while keeping the trace (goal, constraints, plan) available for observability.

### Planner
- Decomposes goals into actionable steps.
- Consults the long-term memory store (vector DB) for prior solutions and design patterns.

### RAG Synthesizer
- Retrieves code snippets, API references, and research papers.
- Generates context-aware patches or scene configurations with provenance.

### Action Policy (RL)
- Chooses tool invocations (edit file, run tests, launch simulator, query docs) based on current state.
- Reward composed from build success, frame-time budgets, tracking stability, UX metrics, and regression avoidance.
- Supports offline training (batch rollouts) and online fine-tuning (DQN/actor-critic/GRPO) with constrained safety checks.

### Tool Executor
- Sandboxed command runner with guardrails (rate limits, secret scrubbing).
- Integrates with package managers, Unity CLI, mobile build tools, and cloud render farms.

### Build/Test/Deploy Pipelines
- CI-friendly stages for linting, unit/integration tests, XR rendering benchmarks, and device deployment.
- Telemetry exporters emit traces, logs, and structured rewards to the memory store for iterative improvement.

### Sensors & Reward Shaper
- Observability adapters collect:
  - Runtime metrics: frame time, GPU/CPU load, memory pressure.
  - Tracking fidelity: reprojection error, feature count, anchor stability.
  - UX: input latency, interaction errors.
- Reward shaper fuses metrics with domain rules (e.g., penalize >16ms frames on 60fps targets).

### Memory & Knowledge Graph
- Vector store for semantic retrieval (code, design docs, runbooks, shaders, URP/HDRP settings).
- Knowledge graph linking goals, actions, outcomes, and artifacts to enable causal reasoning and reuse.

## Data Flows
1. **Goal Intake:** Parse requirements -> planner creates task graph.
2. **Context Build:** RAG pulls relevant code/docs -> synthesizer drafts plan or patch.
3. **Action Selection:** RL policy ranks candidate tool calls -> executor runs safest/highest value.
4. **Evaluation:** Build/test/sim outputs -> sensors compute rewards -> memory updated.
5. **Adaptation:** Policy updated with new rollouts; embeddings refreshed for future retrieval.

## Extensibility Points
- **New Tools:** Register Unity Editor automation, ARCore/ARKit diagnostics, shader profiling, or custom simulators.
- **New Modalities:** Incorporate 3D asset generation, gesture synthesis, or physics curriculum learning.
- **Safety:** Static/dynamic guards, secrets scanning, protected branches, and gated deploy approvals.

## Animation System Architecture (Phase 5 focus)
- **TimelineEditor (UI):** Bottom-docked panel rendering ruler, playhead, track lanes, and keyframe diamonds. Splits static and dynamic canvases to reduce rebuilds; keyboard handlers for play/pause (Space), insert key (K), and copy/paste (Ctrl/Cmd+C/V).
- **AnimationTimeline Model:** Holds duration, frame rate, current time, and `AnimationTrack` list. Each track maps to a scene object and carries sorted `KeyframeData` entries plus mute/lock flags.
- **KeyframeRecorder:** Observes transform/material property changes when armed or auto-keyframe is enabled; inserts/merges keyframes on the active track at the current time with frame snapping. Emits undoable commands for all edits.
- **AnimationPlayer:** Fixed-step (60 Hz) playback loop with speed multipliers and optional reverse/loop modes. Performs per-track interpolation (linear, SmoothStep, Bezier, Quaternion SLERP) and batches property applications per object.
- **CurveEditor:** Per-property graph with Bezier tangents and tangent mode controls. Supports box selection, retiming, scaling, and snapping to frame increments.
- **Baker & Exporter:** Converts timelines to Unity `AnimationClip`s at 30/60 FPS, performs key reduction, and embeds baked data into scene JSON as well as USDZ/GLB exports. Preset generator seeds common motions (Rotate360, Bounce, Fade, Orbit).
- **Performance Guards:** Track culling when the panel is closed, buffer reuse to avoid GC spikes, off-screen object throttling, and profiling target of 60 FPS with 10 animated objects over 5s clips.

## Minimal Stack Recommendations
- **Language:** Python for orchestration; Rust/C++ bindings for performance-critical CV modules.
- **RAG:** Local LLM + embedding model; vector DB (e.g., Qdrant/FAISS); document loaders for Unity docs, forums, and codebase.
- **RL:** PyTorch + RLlib/Lightning; replay buffers for tool trajectories; GRPO/actor-critic for policy learning.
- **Pipelines:** GitHub Actions/GitLab CI with Unity CLI, mobile build targets, WebXR bundling, and artifact storage.

## Next Steps
- Implement the agent skeleton (planner, RAG, policy, executor) with plug-in interfaces.
- Add simulation-backed tests (Unity playmode, headless WebXR) feeding metrics into rewards.
- Stand up vector DB and experiment tracker (MLflow/W&B) for end-to-end training runs.
