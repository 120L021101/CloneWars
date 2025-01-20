import os

from datasets import Dataset, load_dataset, load_from_disk

# print(os.listdir('/scratch/zujizhou/deduped_data/codeparrot-base'))

for dir in os.listdir("/scratch/zujizhou/deduped_data/ML4SE"):
    print(
        """{
    "filename": \""""
        + f"{dir}/"
        + """data-00000-of-00001.arrow"
},"""
    )

deduped_dataset = load_from_disk("/scratch/zujizhou/deduped_data/ML4SE")

print(len(deduped_dataset))
print(deduped_dataset["content"][:10])
