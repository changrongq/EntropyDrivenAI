import unittest
from m1_entropy_tracker.entropy_tracker import EntropyTracker

class TestEntropyTracker(unittest.TestCase):
    
    def setUp(self):
        self.config = {'model_name': 'gpt2', 'output_file': 'test_entropy_trace.json'}
        self.tracker = EntropyTracker(self.config)
        self.dialogue = ["你好，我想问...", "这是个好问题..."]

    def test_entropy_trace_format(self):
        trace = self.tracker.track_entropy(self.dialogue)
        self.assertEqual(len(trace), 2)
        self.assertEqual(trace[0].keys(), {'turn', 'utterance', 'entropy'})

    def test_json_output(self):
        import os
        trace = self.tracker.track_entropy(self.dialogue)
        self.assertTrue(os.path.exists(self.config['output_file']))

if __name__ == "__main__":
    unittest.main()