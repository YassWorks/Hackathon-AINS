from transformers import AutoTokenizer, AutoModelForCausalLM
import torch


model_id = "microsoft/phi-2"
tokenizer = AutoTokenizer.from_pretrained(model_id)
model = AutoModelForCausalLM.from_pretrained(model_id, torch_dtype=torch.float16, device_map="auto")


def explain(prompt):
    inputs = tokenizer(prompt, return_tensors="pt").to("cuda")
    outputs = model.generate(**inputs, max_new_tokens=150)
    
    result = tokenizer.decode(outputs[0], skip_special_tokens=True)
    return result


if __name__ == "__main__":
    
    statement = "The Earth is flat."
    verdict = "MYTH"
    sources = [
        "The Earth is round based on scientific evidence.",
        "Satellite images confirm the Earth is spherical.",
        "The curvature of the Earth is observable from a plane."
    ]
    
    prompt = f"Explain why the following statement is a {verdict}. These are the arguments: {statement}. Sources: {', '.join(sources)}. Provide a detailed explanation."
    
    print(explain(prompt))