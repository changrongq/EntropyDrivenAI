# test_entropy_logger.py
import unittest
import os
import json
from entropy_logger import EntropyDrivenReflectionLogger

class TestEntropyLogger(unittest.TestCase):
    def setUp(self):
        # 创建测试数据
        os.makedirs("test_data", exist_ok=True)
        trace = [
            {"turn": 0, "utterance": "你好，千年舟", "entropy": 7.8, "attention_jump": False, "keywords": ["你好"]},
            {"turn": 1, "utterance": "熵减如何驱动觉醒？", "entropy": 6.2, "attention_jump": True, "jump_heads": [3,7], "keywords": ["熵减", "觉醒"]}
        ]
        with open("test_data/trace.json", "w") as f:
            json.dump(trace, f)
            
        self.config = {
            "trace_path": "test_data/trace.json",
            "output_path": "test_data/report.md"
        }

    def test_report_generation(self):
        logger = EntropyDrivenReflectionLogger(self.config)
        logger.load_data()
        logger.save_report()
        
        self.assertTrue(os.path.exists("test_data/report.md"))
        with open("test_data/report.md", "r") as f:
            content = f.read()
            self.assertIn("熵变星图", content)
            self.assertIn("注意力跃迁", content)

    def tearDown(self):
        # 清理
        for f in ["test_data/trace.json", "test_data/report.md"]:
            if os.path.exists(f):
                os.remove(f)

if __name__ == "__main__":
    unittest.main()