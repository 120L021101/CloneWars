# pip install transformers
from transformers import AutoModelForCausalLM, AutoTokenizer

checkpoint = "HuggingFaceTB/SmolLM-360M"
device = "cpu"  # for GPU usage or "cpu" for CPU usage
tokenizer = AutoTokenizer.from_pretrained(
    checkpoint, cache_dir="/scratch/zujizhou/model"
)
# for multiple GPUs install accelerate and do `model = AutoModelForCausalLM.from_pretrained(checkpoint, device_map="auto")`
model = AutoModelForCausalLM.from_pretrained(
    checkpoint, cache_dir="/scratch/zujizhou/model"
).to(device)
inputs = tokenizer.encode(
    """def main():
    parser = argparse.ArgumentParser(usage=__doc__, formatter_class=argparse.ArgumentDefaultsHelpFormatter, description='Generate keyword specific features.')
    parser.add_argument('kwdefinition', help='Keyword definition file.')
    parser.add_argument('transcript', help='Training transcript.')
    parser.add_argument('--codec', '-c', default='utf-8', help='Codec used for ' + 'the input and output.')""",
    return_tensors="pt",
).to(device)
outputs = model.generate(inputs)
print(tokenizer.decode(outputs[0]))
