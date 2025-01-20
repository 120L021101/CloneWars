from datasets import load_dataset, load_from_disk

dataset = load_from_disk("/scratch/zujizhou/deduped_data/ML4SE")

print(dataset)

# print(len(dataset['train']))
# for item in dataset['train']:
#     print(item)
dataset.push_to_hub("ZujiZhou/ML4SE")
