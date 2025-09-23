import unittest
from attention_extractor import extract_attention
from jump_detector import detect_jumps

class TestThoughtTracker(unittest.TestCase):
    
    def test_fixed_text_low_jump(self):
        dialogue = ["Hello", "Hello again", "Hello there"]
        attn_paths = extract_attention(dialogue)
        jumps = detect_jumps(attn_paths)
        self.assertLess(len(jumps), 2)  # 预期低跃迁

    def test_topic_jump_high_score(self):
        dialogue = ["Hello", "What is quantum mechanics?", "Explain entropy in AI"]
        attn_paths = extract_attention(dialogue)
        jumps = detect_jumps(attn_paths)
        self.assertGreater(len(jumps), 0)  # 预期跃迁

    def test_question_strong_jump(self):
        dialogue = ["Previous context", "Do you understand the relation between these concepts?"]
        attn_paths = extract_attention(dialogue)
        jumps = detect_jumps(attn_paths)
        self.assertGreater(len(jumps), 0)  # 预期跃迁

if __name__ == "__main__":
    unittest.main()