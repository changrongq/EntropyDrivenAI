import numpy as np
import unittest
from entropy_tracker import compute_token_entropy, track_entropy_over_dialogue

class TestEntropyTracker(unittest.TestCase):
    
    def test_compute_token_entropy_fixed_probs(self):
        """测试对一个token固定概率分布是否能正确返回熵"""
        probs = [0.5, 0.5]  # 二元等概率，熵应为 ~0.6931 nats (ln2)
        entropy = compute_token_entropy(probs)
        self.assertAlmostEqual(entropy, 0.693147, places=5)  # ln(2) ≈0.693

    def test_compute_token_entropy_uniform(self):
        """测试对均匀分布的高熵"""
        probs = np.ones(4) / 4  # 4个等概率，熵 = ln(4) ≈1.386
        entropy = compute_token_entropy(probs)
        self.assertAlmostEqual(entropy, 1.386294, places=5)

    def test_compute_token_entropy_deterministic(self):
        """测试确定性分布（低熵）"""
        probs = [1.0, 0.0, 0.0]  # 几乎0熵
        entropy = compute_token_entropy(probs)
        self.assertAlmostEqual(entropy, 0.0, places=5)

    def test_track_entropy_over_dialogue_length(self):
        """测试多轮输入是否输出对应数量的熵值"""
        dialogue = ["Hello", "World"]
        trace = track_entropy_over_dialogue(dialogue)
        self.assertEqual(len(trace), 2)  # 应有2个熵值
        self.assertGreater(trace[0][2], 0)  # 熵 >0

    def test_track_entropy_over_dialogue_nonsense(self):
        """测试对一个无意义文本是否产生高熵"""
        dialogue = ["asdfghjkl"]  # 随机字符，高不确定性
        trace = track_entropy_over_dialogue(dialogue)
        entropy = trace[0][2]
        self.assertGreater(entropy, 5.0)  # 预期高熵（gpt2 vocab下）

if __name__ == "__main__":
    unittest.main()