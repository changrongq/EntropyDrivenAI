import unittest
from m3_reflection_executor.reflection_executor import ReflectionExecutor

class TestReflectionExecutor(unittest.TestCase):
    
    def setUp(self):
        self.config = {
            'model_name': 'gpt2',
            'output_file': 'test_reflection_response.json',
            'lora_rank': 8,
            'lora_alpha': 16,
            'lora_dropout': 0.1
        }
        self.executor = ReflectionExecutor(self.config)
        self.signal = {
            'turn': 2,
            'trigger': True,
            'confidence': 0.83,
            'target_layer': -1,
            'reason': 'significant_entropy_drop_and_attention_jump',
            'awakening_log': ['Initial signal']
        }
        self.dialogue = ["你好", "你理解意识吗？", "意识和熵的关系"]

    def test_execute_reflection_triggered(self):
        result = self.executor.execute_reflection(self.signal, self.dialogue)
        self.assertEqual(result['status'], 'tuned')
        self.assertIn('awakening_log', result)

    def test_no_trigger(self):
        signal = self.signal.copy()
        signal['trigger'] = False
        result = self.executor.execute_reflection(signal, self.dialogue)
        self.assertEqual(result['status'], 'skipped')

    def test_json_output(self):
        import os
        self.executor.execute_reflection(self.signal, self.dialogue)
        self.assertTrue(os.path.exists(self.config['output_file']))

if __name__ == "__main__":
    unittest.main()