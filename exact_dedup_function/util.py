import hashlib

import extract
from datasets import Dataset, load_dataset
from huggingface_hub import HfApi


if __name__ == "__main__":
    dataset = load_dataset(
        "Razvan27/ML4SE-Python", cache_dir="/scratch/zujizhou/ML4SE-Python"
    )

    # Just variable setup
    seen_hashes = set()
    deduped_dataset = []
    train_size = len(dataset["train"])
    i = 0

    # print(dataset["train"])

    while i < train_size:
        try:
            # Gather the content from the datasets
            item = dataset["train"][i]
            file_name, file_path, content, language = (
                item["file_name"],
                item["file_path"],
                item["content"],
                item["language"],
            )

            # Skip any instance with content which is longer than 30,000 characters long
            if len(item["content"]) >= 30000:
                i += 1
                continue

            # Just log progress
            if i % 100 == 0:
                print(
                    f"progress: {i} / {train_size}, {100 * i / train_size}%", flush=True
                )

            deduped_funcs = []

            for func_name, func_definition in extract.extract_functions(
                item["content"]
            ):
                # Hash the object and check if it has been seen before. If not, we save it. If it has been seen before, we ignore it.
                hash_object = hashlib.sha256(func_definition.encode())
                hex_digest = hash_object.hexdigest()
                if hex_digest not in seen_hashes:
                    seen_hashes.add(hex_digest)
                    deduped_funcs.append(func_definition)


            if len(deduped_funcs) != 0:
                deduped_dataset.append(
                    (file_name, file_path, "\n\n".join(deduped_funcs), language)
                )

        except:
            pass
        i += 1

    # print(deduped_dataset[:2])

    # Setup and save to huggingface
    deduped_dataset = Dataset.from_dict(
        {
            "file_name": [data[0] for data in deduped_dataset],
            "file_path": [data[1] for data in deduped_dataset],
            "content": [data[2] for data in deduped_dataset],
            "language": [data[3] for data in deduped_dataset],
        }
    )


    print("done")
    # deduped_dataset.push_to_hub("ZujiZhou/Exact_Func")
    api = HfApi(token="your_token_here")
    deduped_dataset.push_to_hub("{HF_account_name}/Exact-dedup_Func", token=api.token)


    # deduped_dataset.save_to_disk(f"/scratch/zujizhou/deduped_data/ML4SE/ML4SE-func-{i}")
    print(deduped_dataset)
    print("Deduplicated dataset saved!")
