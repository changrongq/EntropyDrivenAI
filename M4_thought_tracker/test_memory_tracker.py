import unittest
import numpy as np
from m4_thought_tracker.memory_tracker import MemoryTracker

class TestMemoryTracker(unittest.TestCase):
    
    def setUp(self):
        self.config = {
            'model_name': 'gpt2',
            'output_paths_file': 'test_long_term_attention_paths.json',
            'output_matrix_file': 'test_attention_jump_matrix.npy',
            'top_k': 2
        }
        self.tracker = MemoryTracker(self.config)
        self.dialogue = ["你好呀，AI", "你理解意识吗？"]

    def test_memory_paths_output(self):
        result = self.tracker.track_memory_paths(self.dialogue)
        self.assertIn('long_term_attention_paths', result)
        self.assertEqual(result['attention_jump_matrix'].shape[1], 12)

    def test_json_output(self):
        import os
        self.tracker.track_memory_paths(self.dialogue)
        self.assertTrue(os.path.exists(self.config['output_paths_file']))

if __name__ == "__main__":
    unittest.main()