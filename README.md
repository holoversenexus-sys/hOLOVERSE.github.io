# 3rdEye: Advanced AR Spatial Composer

3rdEye is a Reality Composer–class AR creation environment that fuses Unity 2023.2 LTS, AR Foundation 5.0, and an autonomous development agent. It focuses on persistent anchors, physics-rich interaction, rapid asset ingestion, and timeline-driven animation for ARKit and ARCore deployments.

## Core Pillars
- **Spatial reliability:** Persistent anchors, robust plane detection with boundary viz, occlusion, and depth-aware sorting.
- **Interactive creation:** Drag-and-drop placement, transform gizmos, timeline animation, undo/redo via command pattern, and hierarchical scene management.
- **High-fidelity rendering:** URP-based lighting, dynamic shadows, selection highlights, and AR-aware occlusion materials.
- **Asset fluency:** FBX/OBJ/GLTF/USD import with LODs, material conversion, and platform-aware texture compression.
- **Performance discipline:** Mobile-first budgets for draw calls, physics, memory, and UI frame time.

## Repository Contents
- `docs/ARCHITECTURE.md`: Autonomous AR development agent overview.
- `docs/3rdEye_TECH_SPEC.md`: Technical specification and delivery milestones for 3rdEye.
- `src/agent/`: Python skeleton for the planner/RAG/policy/tooling stack that will automate Unity workflows.

## Quick Start (Planning)
1. Read `docs/3rdEye_TECH_SPEC.md` for feature scope, stack, and milestones.
2. Use `docs/ARCHITECTURE.md` to align automation hooks with Unity build/test/export pipelines.
3. Extend `src/agent/` modules to orchestrate Unity CLI tasks (import, build, test, export) and to integrate RAG+RL policies.

## Roadmap Highlights
- Implement Unity project layout (Assets/ Scripts/ Prefabs/ Scenes/ Tests/) per the tech spec.
- Stand up AR session, plane detection, anchor management, and placement loop with physics and occlusion.
- Deliver timeline animation UI, undo/redo command stack, and asset import/export (USDZ/GLB) paths.
- Integrate autonomous agent loops for CI builds, validation, and knowledge-grounded assistance.
