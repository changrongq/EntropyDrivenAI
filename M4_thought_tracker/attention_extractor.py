import torch
from transformers import GPT2Tokenizer, GPT2LMHeadModel

def extract_attention(dialogue):
    """
    提取每轮对话最后一层注意力分布（last token attn per head）。
    参数:
        dialogue (List[str]): 多轮对话
    返回:
        attn_paths (dict): {"turn_i": {"head_h": [attn_values]}}
    """
    tokenizer = GPT2Tokenizer.from_pretrained("gpt2")
    model = GPT2LMHeadModel.from_pretrained("gpt2", output_attentions=True)
    model.eval()

    attn_paths = {}

    for i, utterance in enumerate(dialogue):
        inputs = tokenizer(utterance, return_tensors="pt")
        with torch.no_grad():
            outputs = model(**inputs)
            last_layer_attn = outputs.attentions[-1][0]  # [num_heads, seq_len, seq_len]
            last_token_attn = last_layer_attn[:, -1, :]  # [num_heads, key_len]
            attn_paths[f"turn_{i}"] = {}
            for h in range(last_token_attn.shape[0]):
                attn_paths[f"turn_{i}"][f"head_{h}"] = last_token_attn[h].numpy().tolist()

    return attn_paths