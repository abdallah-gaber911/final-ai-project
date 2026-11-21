"""
Unit tests for Video Player logic and file utilities.
These tests are completely headless (display-free) and verify:
- Supported video format discovery (.mp4, .avi, .mov, .mkv, .webm)
- Case-insensitivity and exclusion of non-video files
- Random selection avoiding immediate repeats
- Outcome folder resolution for Computer and Human victories
"""

import os
import sys
import shutil
import tempfile
import unittest

# Ensure project root is in sys.path
project_root = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
if project_root not in sys.path:
    sys.path.insert(0, project_root)

from video_player import (
    get_video_files,
    pick_random_video,
    find_outcome_folder,
    SUPPORTED_VIDEO_EXTENSIONS,
    HAS_VIDEO_LIBS
)


class TestVideoPlayerLogic(unittest.TestCase):
    """Test suite for headless video player utilities."""

    def setUp(self):
        self.test_dir = tempfile.mkdtemp(prefix="c4_test_video_")

    def tearDown(self):
        if os.path.exists(self.test_dir):
            shutil.rmtree(self.test_dir, ignore_errors=True)

    def test_get_video_files_empty_and_nonexistent(self):
        """Non-existent directories and empty directories must return empty list."""
        self.assertEqual(get_video_files("non_existent_folder_xyz_123"), [])
        self.assertEqual(get_video_files(""), [])
        self.assertEqual(get_video_files(None), [])
        self.assertEqual(get_video_files(self.test_dir), [])

    def test_get_video_files_filtering_and_case(self):
        """Must discover supported video files and ignore non-video files or folders."""
        valid_files = ["clip1.mp4", "clip2.AVI", "clip3.MOV", "clip4.mkv", "clip5.webm"]
        ignored_files = ["notes.txt", "thumbnail.png", ".gitkeep", "data.json"]

        for fname in valid_files + ignored_files:
            open(os.path.join(self.test_dir, fname), "w").close()

        # Create a subfolder with a video inside; only top-level files in test_dir should be picked
        sub_dir = os.path.join(self.test_dir, "sub")
        os.makedirs(sub_dir)
        open(os.path.join(sub_dir, "nested.mp4"), "w").close()

        discovered = get_video_files(self.test_dir)
        discovered_names = [os.path.basename(f) for f in discovered]

        self.assertEqual(len(discovered_names), len(valid_files))
        for v in valid_files:
            self.assertIn(v, discovered_names)
        for ign in ignored_files:
            self.assertNotIn(ign, discovered_names)

    def test_pick_random_video_empty(self):
        """Empty video list returns None."""
        self.assertIsNone(pick_random_video([]))
        self.assertIsNone(pick_random_video([], last_video="some_clip.mp4"))

    def test_pick_random_video_single_item(self):
        """Single item video list always returns the only item."""
        single = ["videos/win.mp4"]
        self.assertEqual(pick_random_video(single), "videos/win.mp4")
        self.assertEqual(pick_random_video(single, last_video="videos/win.mp4"), "videos/win.mp4")

    def test_pick_random_video_avoids_immediate_repeat(self):
        """When multiple videos are available, never pick the same video twice in a row."""
        videos = ["v1.mp4", "v2.mp4", "v3.mp4", "v4.mp4"]
        last_played = "v2.mp4"

        # Over 100 trials, last_played should never be selected
        for _ in range(100):
            picked = pick_random_video(videos, last_video=last_played)
            self.assertNotEqual(picked, last_played)
            self.assertIn(picked, videos)

    def test_pick_random_video_two_videos_alternates(self):
        """With exactly two videos, the other video must always be picked."""
        videos = ["clip_a.mp4", "clip_b.mp4"]
        self.assertEqual(pick_random_video(videos, last_video="clip_a.mp4"), "clip_b.mp4")
        self.assertEqual(pick_random_video(videos, last_video="clip_b.mp4"), "clip_a.mp4")

    def test_find_outcome_folder_resolution(self):
        """find_outcome_folder correctly finds candidate folders in search roots."""
        # Create simulated directory structure
        ai_folder = os.path.join(self.test_dir, "computer win")
        human_folder = os.path.join(self.test_dir, "user win")
        os.makedirs(ai_folder)
        os.makedirs(human_folder)

        open(os.path.join(ai_folder, "win_ai.mp4"), "w").close()
        open(os.path.join(human_folder, "win_user.mp4"), "w").close()

        resolved_ai, ai_vids = find_outcome_folder("computer", search_roots=[self.test_dir])
        resolved_human, human_vids = find_outcome_folder("human", search_roots=[self.test_dir])

        self.assertEqual(os.path.abspath(resolved_ai), os.path.abspath(ai_folder))
        self.assertEqual(len(ai_vids), 1)
        self.assertEqual(os.path.abspath(resolved_human), os.path.abspath(human_folder))
        self.assertEqual(len(human_vids), 1)


if __name__ == "__main__":
    unittest.main()
