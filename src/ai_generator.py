from transformers import LlamaForCausalLM, LlamaTokenizer
import torch

class AIContentGenerator:
    def __init__(self, model_name='meta-llama/Llama-2-7b-chat-hf'):
        self.tokenizer = LlamaTokenizer.from_pretrained(model_name)
        self.model = LlamaForCausalLM.from_pretrained(
            model_name,
            torch_dtype=torch.float16,
            device_map='auto'
        )

    def create_article(self, topic, keywords):
        prompt = f"""
Write an engaging 800-word article about {topic}.
Naturally include these keywords: {', '.join(keywords[:5])}.
Structure the article with an introduction, three main sections, and a conclusion.
Write in an informative and engaging style.
"""
        inputs = self.tokenizer(prompt, return_tensors='pt')
        outputs = self.model.generate(
            inputs.input_ids,
            max_length=1000,
            temperature=0.7,
            do_sample=True,
            pad_token_id=self.tokenizer.eos_token_id,
            eos_token_id=self.tokenizer.eos_token_id
        )
        article = self.tokenizer.decode(outputs[0], skip_special_tokens=True)
        return article
