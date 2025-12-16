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
- **Phase 5 (Days 18-22):** Timeline editor, keyframe recording, playback, curve editing, baking/presets, multi-object tracks. See the “Phase 5 Animation Implementation Guide” below for concrete UI layout, data structures, and workflows.
- **Phase 6 (Days 23-27):** Asset import (FBX/OBJ/GLTF/USD), optimization, asset library UI, USDZ/GLB export with validation and metadata.
- **Phase 7 (Days 28-30):** Performance polish, bug triage, accessibility sweep, onboarding, documentation, final builds, release checklist.

## Acceptance & Performance Targets
- 60 FPS target with <35 draw calls and UI frame cost <2ms.
- Physics stable with 50 dynamic objects; CCD for fast movers; anchor updates batched.
- Assets validated under 50k tris per mesh, 2048x2048 textures max, import <10s per asset.
- Undo/redo history up to 50 commands with memory guard; scene save/load includes anchors and animations.
- Exports validated in AR Quick Look (USDZ) and ARCore Scene Viewer (GLB) with correct materials and anchors.

## Platform-Specific Requirements

### iOS Configuration
- **Info.plist:**
  ```xml
  <key>NSCameraUsageDescription</key>
  <string>ARComposerPro needs camera access to create augmented reality experiences</string>

  <key>NSPhotoLibraryUsageDescription</key>
  <string>ARComposerPro needs photo library access to import textures and save screenshots</string>

  <key>NSPhotoLibraryAddUsageDescription</key>
  <string>ARComposerPro needs permission to save your AR creations to the photo library</string>

  <key>UIRequiredDeviceCapabilities</key>
  <array>
      <string>arkit</string>
      <string>metal</string>
  </array>

  <key>UIRequiresFullScreen</key>
  <true/>

  <key>UIStatusBarHidden</key>
  <true/>

  <key>UIViewControllerBasedStatusBarAppearance</key>
  <false/>
  ```
- **Entitlements:** ARKit capability on; FileProvider enabled for sharing; iCloud if cloud sync ships.
- **Build Settings:** iOS 14.0+ target, ARM64-only, Bitcode disabled, engine code stripping enabled, managed stripping level set to Medium.

### Android Configuration
- **Manifest:**
  ```xml
  <manifest>
      <!-- ARCore requirement -->
      <uses-permission android:name="android.permission.CAMERA" />
      <uses-feature android:name="android.hardware.camera.ar" android:required="true" />

      <!-- Storage for scene files -->
      <uses-permission android:name="android.permission.WRITE_EXTERNAL_STORAGE" 
                       android:maxSdkVersion="28" />
      <uses-permission android:name="android.permission.READ_EXTERNAL_STORAGE" />

      <!-- Internet for future cloud features -->
      <uses-permission android:name="android.permission.INTERNET" />

      <application>
          <!-- ARCore metadata -->
          <meta-data android:name="com.google.ar.core" 
                     android:value="required" />

          <!-- FileProvider for sharing -->
          <provider
              android:name="androidx.core.content.FileProvider"
              android:authorities="${applicationId}.fileprovider"
              android:exported="false"
              android:grantUriPermissions="true">
              <meta-data
                  android:name="android.support.FILE_PROVIDER_PATHS"
                  android:resource="@xml/file_paths" />
          </provider>
      </application>
  </manifest>
  ```
- **Gradle:**
  ```gradle
  android {
      compileSdkVersion 33
      defaultConfig {
          minSdkVersion 26
          targetSdkVersion 33
          versionCode 1
          versionName "0.1.0"
      }
      
      buildTypes {
          release {
              minifyEnabled true
              proguardFiles getDefaultProguardFile('proguard-android-optimize.txt')
              signingConfig signingConfigs.release
          }
      }
  }
  ```
- **App Signing:** iOS uses automatic dev signing and manual distribution certificates; Android keeps release keystores out of repo, with alias `arcomposerpro-release` and passwords sourced from env/secret store.
- **Optimizations:** Metal Performance Shaders and thermal throttling awareness on iOS; Vulkan/ASTC/ETC2 and Adaptive Performance on Android; early-Z and reduced overdraw on mobile GPUs.
- **Capability Detection & Degradation:** `DeviceCapabilities` class queries ARCore/ARKit, depth/LiDAR, texture limits, Vulkan/Metal, and memory; features degrade gracefully (disable advanced effects, lower LOD, or notify user) on unsupported or low-end hardware.

## Undo/Redo System
- **Interface:**
  ```csharp
  public interface ICommand
  {
      string Description { get; }
      void Execute();
      void Undo();
      bool CanExecute();
      int MemoryFootprint { get; }
  }
  ```
- **Command Types:** Placement, transform (position/rotation/scale), deletion with serialized state, material edits, hierarchy reparenting, animation keyframes. Non-undoable: scene load/save, settings, import operations, AR session init, non-persistent camera moves.
- **History Management:** `CommandHistory` keeps undo/redo stacks (max 50 items, 100MB memory guard), clears redo on new commands, and prunes oldest entries beyond limits.
- **Serialization:** Optionally persist last 10 commands with the scene file; clear on new scene creation.
- **UI Integration:** Enable/disable undo/redo buttons by stack count, show descriptions in tooltips/history panel.

## Analytics & Telemetry
- **Frameworks:** Unity Analytics (built-in) with optional Firebase Analytics; privacy-first with explicit opt-in before tracking.
- **Metrics:** Performance (FPS, frame-time histogram, memory peaks, battery, thermal events), usage (session duration, feature frequency, object counts, import/saves, undo/redo), errors (crashes, import/export failures, tracking loss), and user flow (time to first placement, tutorial completion, drop-off points).
- **Events:** Custom events such as `object_placed`, `scene_exported`, and `error_occurred` carry context (types, counts, file sizes, messages).
- **Privacy:** No PII; hashed device IDs, country-only location; GDPR/CCPA compliant opt-in/out and data deletion; no tracking before consent.
- **Retention:** 90d performance, 1y crash reports, 6m usage patterns; anonymized aggregates retained longer. Dashboard monitors crashes, performance, feature adoption, and A/B tests.

## Localization & Internationalization
- **Languages:** English (US) initially; architecture prepared for Spanish, French, German, Japanese, Simplified Chinese.
- **Implementation:** Unity Localization package with string tables (UI/Errors/Tooltips) under `Assets/Localization`, locale assets, and `[Category].[Context].[Element]` keys.
- **Workflow:** Add English strings, export to CSV/XLIFF, translate, re-import, and test with pseudo-localization for overflow detection. Automatic device-language selection with manual override; fallback to English.
- **Accessibility:** Future RTL layout mirroring, icon flipping, culture-aware number/date formatting via `CultureInfo`.

## Build Pipeline & CI/CD
- **Triggers:** On-demand, on push to `develop/main`, nightly (2:00 AM UTC), and version tags.
- **Stages:** Validation (compile, tests, static analysis, asset checks) → Build (Unity batch build, auto-increment build number) → Test (UI/perf/memory, build size) → Package (signed APK/IPA, symbols, artifacts) → Deploy (TestFlight/Play Internal Testing) with notifications.
- **Configs:** Unity Cloud Build manifest with iOS/Android targets using `Assets/Scenes/Main.unity`; GitHub Actions using `game-ci` builders/test runner with Unity 2023.2.20f1; Slack notifications on status.
- **Pre/Post Build:** Pre-build increments bundle codes, updates version strings, clears console, validates scenes, stamps build info. Post-build emits reports, computes build size, copies symbols, and scaffolds release notes.
- **Versioning:** SemVer Major.Minor.Patch (Build) with automatic build increments; patch for fixes, minor for features, major for releases.
- **Release Checklist:** Tests passing, performance budgets met, critical bugs cleared, notes and store metadata ready, assets (screenshots/videos) prepared, privacy/legal verified, symbols uploaded, staged rollout monitored with rollback plan.

## Phase 5 Animation Implementation Guide (Days 18-22)

### Day 18: Timeline Editor Foundation
- **Layout:** Bottom-docked panel, 120pt height, resizable via drag handle. Separate canvases for static chrome (background, rulers) and dynamic overlays (playhead, keyframes) to minimize rebuilds.
- **Controls:** Play/Pause/Stop buttons, loop toggle, fit/zoom-in/zoom-out, current time and duration labels (`mm:ss.ms`). Keyboard: Space toggles play/pause; click timeline to jump; scroll to zoom around cursor.
- **Timeline Data:**
  ```csharp
  public class AnimationTimeline
  {
      public float Duration { get; set; } // seconds
      public int FrameRate { get; set; } // 30 or 60
      public float CurrentTime { get; set; }
      public List<AnimationTrack> Tracks { get; } = new();
  }

  public class AnimationTrack
  {
      public string TrackId; // GUID
      public string ObjectId; // matches scene object
      public List<KeyframeData> Keyframes = new();
      public bool Muted;
      public bool Locked;
  }
  ```
- **Rendering:** Time ruler with 1s major ticks and 0.2s minor ticks; vertical playhead line; per-track lanes with color-coded bands; diamond keyframes aligned to ticks; selection highlight state.
- **Navigation:** Drag the scrubber (playhead handle) to seek; click anywhere to reposition; maintain snapped increments to frame boundaries (frame = 1/FrameRate) to prevent jitter.

### Day 19: Keyframe Recording
- **Recorder UI:** Record (red) button, Auto-keyframe toggle, manual insert shortcut (K). Status indicator shows armed vs idle.
- **Keyframe Schema:**
  ```csharp
  public class KeyframeData
  {
      public float Time; // seconds
      public string PropertyPath; // e.g., "transform.position.x"
      public SerializedValue Value; // float/Vector3/Quaternion/Color
      public InterpolationMode Interp; // Linear, SmoothStep, Bezier
  }
  ```
- **Capture Rules:**
  - Transform: sample Position (Vector3), Rotation (Quaternion stored as Euler for UI), Scale (Vector3).
  - Material: BaseColor (Color), Metallic (float), Smoothness (float), optional Emission (Color).
  - Auto-keyframe: on property change, insert/update keyframe on the active track at the current time; merge within 1 frame tolerance to avoid duplicates.
- **Storage:** Sparse keyframes only; keep tracks sorted by time; binary search for playback lookup. Deduplicate keys on the same frame.

### Day 20: Animation Playback
- **Player:** Play from current time, Pause holds state, Stop resets to 0; loop toggle; speed multipliers (0.5x/1x/2x) and reverse playback flag.
- **Interpolation:**
  - Linear (default) for scalars/vectors, SmoothStep for eased UI curves, Bezier control points for custom easing, Quaternion SLERP for rotations.
  - Cache previous/next keyframe pairs per track to minimize per-frame searches.
- **Update Loop:** Fixed timestep at 60 Hz; advance time by `delta * speed * direction`; clamp or wrap if looping. Apply interpolated values per property and batch updates per object to reduce SetComponent churn.
- **Optimization:** Skip tracks with no keys in the current view; cull off-screen objects; coalesce material updates; limit GC by reusing buffers.

### Day 21: Timeline Editing
- **Keyframe Editing:** Click to select, drag horizontally to retime (snap to frame or user-defined snap increment), Delete key removes, copy/paste via Ctrl/Cmd+C/V preserves property path and interpolation.
- **Curve Editor:** Graph view per property with pan/zoom; Bezier handles with tangent modes (Auto/Linear/Constant); box-select multiple keys and scale timing relative to pivot.
- **Track Operations:** Add/Remove track, Mute/Solo, Lock to prevent edits. Multi-object support via stacked tracks with distinct colors; group animations by pinning related tracks.
- **Bulk Actions:** Multi-select diamonds, move them together, and scale timing (compress/expand) for pacing adjustments. Undo/redo hooks wrap all edits.

### Day 22: Animation Export & Polish
- **Baking:** Convert timeline to `AnimationClip` at target frame rate (30/60). Reduce redundant keys (tolerance: 0.001 for floats, 0.1 degrees for rotations) and ensure first/last key alignment for seamless loops.
- **Presets:**
  - Rotate360 (2s default, Y-axis),
  - Bounce (scale 0.9→1.05 + Y offset),
  - Fade (material alpha),
  - Orbit (circular motion around anchor).
- **Looping Modes:** None, Loop, Ping-Pong (auto-reverse). Loop count optional; infinite uses loop flag.
- **Export:**
  - Include baked animation in scene JSON under `animations.timeline.tracks` and per-object `animations` blocks.
  - Platform exports: USDZ/GLB carry baked curves (sampled) with material references intact.
- **Performance Testing:** 10 objects with 5s clips, 60 FPS target, animation memory <50MB. Profile update costs and confirm culling works when timeline closed.
