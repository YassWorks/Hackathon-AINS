from transformers import AutoTokenizer, AutoModelForCausalLM
import torch


model_id = "microsoft/phi-2"
tokenizer = AutoTokenizer.from_pretrained(model_id)
model = AutoModelForCausalLM.from_pretrained(model_id, torch_dtype=torch.float16, device_map="auto")


def explain(prompt):
    
    try:
        inputs = tokenizer(prompt, return_tensors="pt").to("cuda")
        outputs = model.generate(**inputs, max_new_tokens=150)
        
        result = tokenizer.decode(outputs[0], skip_special_tokens=True)
        return result
    
    except Exception as e:
        print("Error in explain function:", e)
        return "An error occurred while generating the explanation."