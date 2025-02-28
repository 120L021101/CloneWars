import hashlib
import extract
from datasets import Dataset, load_dataset
from huggingface_hub import HfApi

if __name__ == "__main__":
    # Load dataset
    dataset = load_dataset("Razvan27/ML4SE-Python", cache_dir="/scratch/zujizhou/ML4SE-Python")
    
    seen_hashes = set()
    deduped_dataset = []
    train_data = dataset["train"]
    train_size = len(train_data)

    print(f"Processing {train_size} files...")

    for i, item in enumerate(train_data):
        try:
            file_name, file_path, content, language = (
                item["file_name"],
                item["file_path"],
                item["content"],
                item["language"],
            )

            # Skip files with overly long content
            if len(content) >= 30000:
                continue

            if i % 100 == 0:
                print(f"Progress: {i}/{train_size} ({100 * i / train_size:.2f}%)", flush=True)

            deduped_funcs = [
                func_def for _, func_def in extract.extract_functions(content)
                if (hash_digest := hashlib.sha256(func_def.encode()).hexdigest()) not in seen_hashes
                and not seen_hashes.add(hash_digest)
            ]

            if deduped_funcs:
                deduped_dataset.append((file_name, file_path, "\n\n".join(deduped_funcs), language))

        except Exception as e:
            print(f"Error processing file {i}: {e}")

    # Convert to Hugging Face dataset
    deduped_dataset = Dataset.from_dict({
        "file_name": [data[0] for data in deduped_dataset],
        "file_path": [data[1] for data in deduped_dataset],
        "content": [data[2] for data in deduped_dataset],
        "language": [data[3] for data in deduped_dataset],
    })

    print("Pushing deduplicated dataset to Hugging Face...")

    # Push to Hugging Face
    api = HfApi(token="your_token_here")
    deduped_dataset.push_to_hub("{HF_account_name}/Exact-dedup_Func", token=api.token)

    print("Deduplication complete!")
