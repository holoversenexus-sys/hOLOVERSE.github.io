"""Timeline-based animation primitives for 3rdEye automation.

This module provides a lightweight, engine-agnostic representation of Phase 5's
animation requirements: tracks, keyframes, timeline playback, and presets. It
is designed to be orchestrated by the agent to reason about animation plans,
export them to downstream tools (e.g., Unity Automation), and support basic
editing operations such as copy/paste and retiming.
"""
from __future__ import annotations

from dataclasses import dataclass, field
from typing import Dict, List, Sequence, Tuple


Interpolation = str


@dataclass
class Keyframe:
    time: float
    property_path: str
    value: float | Sequence[float]
    interpolation: Interpolation = "linear"


@dataclass
class TimelineTrack:
    object_id: str
    keyframes: List[Keyframe] = field(default_factory=list)
    muted: bool = False
    locked: bool = False

    def add_keyframe(self, keyframe: Keyframe) -> None:
        if self.locked:
            raise ValueError("Track is locked; cannot add keyframe")
        self.keyframes.append(keyframe)
        self.keyframes.sort(key=lambda k: k.time)

    def delete_keyframe(self, property_path: str, time: float) -> None:
        if self.locked:
            raise ValueError("Track is locked; cannot delete keyframe")
        self.keyframes = [kf for kf in self.keyframes if not (kf.property_path == property_path and kf.time == time)]

    def move_keyframe(self, property_path: str, old_time: float, new_time: float) -> None:
        if self.locked:
            raise ValueError("Track is locked; cannot move keyframe")
        for kf in self.keyframes:
            if kf.property_path == property_path and kf.time == old_time:
                kf.time = new_time
        self.keyframes.sort(key=lambda k: k.time)

    def copy_keyframes(self, start: float, end: float) -> List[Keyframe]:
        return [Keyframe(kf.time - start, kf.property_path, kf.value, kf.interpolation) for kf in self.keyframes if start <= kf.time <= end]

    def paste_keyframes(self, offset: float, keyframes: List[Keyframe]) -> None:
        if self.locked:
            raise ValueError("Track is locked; cannot paste keyframes")
        for kf in keyframes:
            self.add_keyframe(Keyframe(kf.time + offset, kf.property_path, kf.value, kf.interpolation))

    def sample(self, time: float) -> Dict[str, float | Sequence[float]]:
        if self.muted:
            return {}
        return self._interpolate_values(time)

    def _interpolate_values(self, time: float) -> Dict[str, float | Sequence[float]]:
        values: Dict[str, float | Sequence[float]] = {}
        paths = {kf.property_path for kf in self.keyframes}
        for path in paths:
            siblings = [kf for kf in self.keyframes if kf.property_path == path]
            if not siblings:
                continue
            before, after = self._find_adjacent_keyframes(siblings, time)
            if before and after:
                t_norm = (time - before.time) / (after.time - before.time) if after.time != before.time else 0.0
                values[path] = _lerp(before.value, after.value, t_norm, after.interpolation)
            elif before:
                values[path] = before.value
            elif after:
                values[path] = after.value
        return values

    @staticmethod
    def _find_adjacent_keyframes(keyframes: List[Keyframe], time: float) -> Tuple[Keyframe | None, Keyframe | None]:
        before = None
        after = None
        for kf in sorted(keyframes, key=lambda k: k.time):
            if kf.time <= time:
                before = kf
            elif kf.time > time and after is None:
                after = kf
        return before, after


@dataclass
class AnimationTimeline:
    duration: float
    frame_rate: int = 60
    tracks: Dict[str, TimelineTrack] = field(default_factory=dict)
    current_time: float = 0.0
    loop: bool = False

    def add_track(self, object_id: str) -> TimelineTrack:
        track = TimelineTrack(object_id)
        self.tracks[object_id] = track
        return track

    def remove_track(self, object_id: str) -> None:
        if object_id in self.tracks:
            del self.tracks[object_id]

    def seek(self, time: float) -> None:
        self.current_time = max(0.0, min(time, self.duration))

    def step(self, frames: int = 1) -> None:
        delta = frames / float(self.frame_rate)
        self.advance(delta)

    def advance(self, delta_time: float) -> None:
        next_time = self.current_time + delta_time
        if self.loop:
            self.current_time = next_time % self.duration if self.duration > 0 else 0.0
        else:
            self.current_time = min(max(0.0, next_time), self.duration)

    def sample(self) -> Dict[str, Dict[str, float | Sequence[float]]]:
        return {obj_id: track.sample(self.current_time) for obj_id, track in self.tracks.items()}


class AnimationPlayer:
    """Lightweight playback controller for an AnimationTimeline."""

    def __init__(self, timeline: AnimationTimeline):
        self.timeline = timeline
        self.playing = False
        self.speed = 1.0
        self.direction = 1.0

    def play(self, loop: bool = False, speed: float = 1.0, reverse: bool = False) -> None:
        self.timeline.loop = loop
        self.speed = speed
        self.direction = -1.0 if reverse else 1.0
        self.playing = True

    def pause(self) -> None:
        self.playing = False

    def stop(self) -> None:
        self.playing = False
        self.timeline.seek(0.0)

    def update(self, delta_time: float) -> Dict[str, Dict[str, float | Sequence[float]]]:
        if not self.playing:
            return self.timeline.sample()
        self.timeline.advance(delta_time * self.speed * self.direction)
        return self.timeline.sample()


class KeyframeRecorder:
    """Utility for capturing keyframes on property change events."""

    def __init__(self, auto_keyframe: bool = True):
        self.auto_keyframe = auto_keyframe
        self.record_button_enabled = False

    def toggle_record(self, on: bool) -> None:
        self.record_button_enabled = on

    def record_change(
        self,
        track: TimelineTrack,
        property_path: str,
        value: float | Sequence[float],
        time: float,
        interpolation: Interpolation = "linear",
    ) -> Keyframe:
        if not (self.auto_keyframe or self.record_button_enabled):
            raise RuntimeError("Recording is disabled; enable auto-keyframe or record mode")
        keyframe = Keyframe(time=time, property_path=property_path, value=value, interpolation=interpolation)
        track.add_keyframe(keyframe)
        return keyframe


# Preset generators ---------------------------------------------------------

def rotate_360_preset(object_id: str, duration: float = 2.0) -> AnimationTimeline:
    timeline = AnimationTimeline(duration=duration, frame_rate=60, loop=True)
    track = timeline.add_track(object_id)
    track.add_keyframe(Keyframe(0.0, "rotation.y", 0.0))
    track.add_keyframe(Keyframe(duration, "rotation.y", 360.0))
    return timeline


def bounce_preset(object_id: str, height: float = 0.2, duration: float = 1.0) -> AnimationTimeline:
    timeline = AnimationTimeline(duration=duration, frame_rate=60, loop=True)
    track = timeline.add_track(object_id)
    track.add_keyframe(Keyframe(0.0, "position.y", 0.0, "ease-in"))
    track.add_keyframe(Keyframe(duration * 0.5, "position.y", height, "ease-out"))
    track.add_keyframe(Keyframe(duration, "position.y", 0.0, "ease-in"))
    return timeline


def orbit_preset(object_id: str, radius: float = 1.0, duration: float = 3.0) -> AnimationTimeline:
    timeline = AnimationTimeline(duration=duration, frame_rate=60, loop=True)
    track = timeline.add_track(object_id)
    track.add_keyframe(Keyframe(0.0, "position.x", radius))
    track.add_keyframe(Keyframe(duration * 0.25, "position.z", radius))
    track.add_keyframe(Keyframe(duration * 0.5, "position.x", -radius))
    track.add_keyframe(Keyframe(duration * 0.75, "position.z", -radius))
    track.add_keyframe(Keyframe(duration, "position.x", radius))
    return timeline


# Utility interpolation helpers -------------------------------------------

def _lerp(start: float | Sequence[float], end: float | Sequence[float], t: float, mode: Interpolation) -> float | Sequence[float]:
    t_clamped = max(0.0, min(t, 1.0))
    if mode == "ease-in":
        t_clamped = t_clamped * t_clamped
    elif mode == "ease-out":
        t_clamped = 1 - (1 - t_clamped) * (1 - t_clamped)
    elif mode == "bezier":
        # Simple symmetric ease for placeholder Bezier
        t_clamped = 3 * t_clamped * t_clamped - 2 * t_clamped * t_clamped * t_clamped
    if isinstance(start, Sequence) and not isinstance(start, (str, bytes)):
        return [_lerp(float(s), float(e), t_clamped, "linear") for s, e in zip(start, end)]  # type: ignore[arg-type]
    return float(start) + (float(end) - float(start)) * t_clamped
