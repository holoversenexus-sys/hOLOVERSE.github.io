# 3rdEye Technical Specification

3rdEye is a Reality Composer alternative focused on persistent AR creation with Unity 2023.2 LTS, AR Foundation 5.0, and URP. This document condenses the primary objectives, architecture, and phased delivery plan.

## Objectives
- **Anchors & tracking:** Persistent world anchors, plane detection with boundary visualization, anchor-based hierarchy attachment, and depth-aware occlusion.
- **Interaction & physics:** Drag-and-drop placement, transform gizmos, physics simulation with collision dynamics and constraints, and robust undo/redo.
- **Animation & timeline:** Timeline editor with keyframes, multiple tracks, playback controls, and animation baking/export.
- **Asset pipeline:** Import FBX/OBJ/GLTF/USD (and USDZ/GLB export), automatic LODs, URP material conversion, platform-aware texture compression, and metadata logging.
- **Rendering:** Dynamic lighting with shadows, selection outlines, occlusion shaders, and URP budgets for mobile.
- **Cross-platform delivery:** ARKit/ARCore export paths, Addressables for runtime loading, and Mirror-backed collaboration hooks.

## Stack & Integrations
- **Engine:** Unity 2023.2 LTS + URP + AR Foundation 5.0.
- **Platform extensions:** ARCore Extensions, ARKit Face Tracking, XR Interaction Toolkit, Addressables, Mirror (networking), Havok physics fallback.
- **Patterns:** ECS for hot paths, Observer for UI updates, Command for undo/redo, ScriptableObjects for configuration, Addressables for assets.
- **Input:** Unity Input System with touch gestures (tap, long-press, drag, pinch, rotate, three-finger undo/redo) and keyboard shortcuts for editor use.

## Subsystems
- **Session & tracking:** ARSessionManager, PlaneDetectionManager (horizontal/vertical, merge distance 0.3m), AnchorManager (persistent IDs, attachment, cleanup), OcclusionRenderer.
- **Placement & interaction:** HitTestManager, PlacementIndicator, SelectionManager, TransformGizmos (move/rotate/scale, snap), ObjectInspector (transform, physics, material, animation), grouping and duplication.
- **Physics:** PhysicsManager (timestep 0.02s, CCD for fast movers), collider generation, PhysicsMaterialLibrary (wood/metal/rubber/glass/plastic), constraints (fixed/hinge/spring), physics LOD tiers.
- **Animation:** TimelineEditor UI, KeyframeRecorder (auto/manual), AnimationPlayer (looping, speed, easing), curve editor, baking to AnimationClip, presets (rotate, bounce, fade, orbit).
- **Assets:** AssetImporter framework with validators, mesh optimization (weld, degenerate removal, cache-friendly reordering), LOD generator (100/60/30/15 at 0/5/10/20m), texture processing (ASTC/ETC2, mipmaps, 2048 cap), URP material mapping, metadata JSON per import.
- **Export:** USDZ exporter (iOS) and GLB exporter (Android) with options for compression, texture quality, animation inclusion, and anchor metadata.
- **Scene persistence:** JSON scene schema (versioned), backups before save, auto-save rotation, migration hooks for forward compatibility.
- **UI/UX:** Mobile-first layout with safe-area handling, toolbar (select/move/rotate/scale/delete/undo/redo/settings), hierarchy drawer, inspector panel, timeline, context menus, haptic/audio feedback, accessibility (contrast, touch targets, screen reader labels).
- **Analytics:** Opt-in metrics for performance, feature usage, and error tracking; privacy-first consent flow.
- **Build & CI:** Git-based flow (main/develop/feature), Unity CLI builds, GitHub Actions/Unity Cloud Build, automated tests (unit/integration/performance), symbol packaging, staged rollouts.

## Delivery Phases (30-Day Outline)
- **Phase 1 (Days 1-3):** Environment setup; Unity project scaffold per directory tree; core managers (ARSession, Scene, Input, UI); object pooling; “Hello World” plane placement.
- **Phase 2 (Days 4-7):** AR session robustness, plane detection + visualizers, hit testing, placement indicator, anchor lifecycle and persistence hooks.
- **Phase 3 (Days 8-12):** Physics system with colliders, materials, forces, constraints, and performance guards (sleeping, LOD); stress testing to 50+ dynamic objects at 60 FPS.
- **Phase 4 (Days 13-17):** Scene hierarchy UI, selection/transform gizmos, inspector, duplication/deletion/grouping, undo/redo command stack.
- **Phase 5 (Days 18-22):** Timeline editor, keyframe recording, playback, curve editing, baking/presets, multi-object tracks.
- **Phase 6 (Days 23-27):** Asset import (FBX/OBJ/GLTF/USD), optimization, asset library UI, USDZ/GLB export with validation and metadata.
- **Phase 7 (Days 28-30):** Performance polish, bug triage, accessibility sweep, onboarding, documentation, final builds, release checklist.

## Acceptance & Performance Targets
- 60 FPS target with <35 draw calls and UI frame cost <2ms.
- Physics stable with 50 dynamic objects; CCD for fast movers; anchor updates batched.
- Assets validated under 50k tris per mesh, 2048x2048 textures max, import <10s per asset.
- Undo/redo history up to 50 commands with memory guard; scene save/load includes anchors and animations.
- Exports validated in AR Quick Look (USDZ) and ARCore Scene Viewer (GLB) with correct materials and anchors.
