import json
import random

from arg_parser import arg_parser
from datasets import Dataset, load_dataset


def generate_key(args, item):
    return item["file_path"]


def should_mask(args, item):
    if len(item["content"]) <= 2:
        return False
    flag = random.random()
    return flag <= args.mask_p


def main():
    args = arg_parser()

    # open dataset
    dataset = load_dataset(args.dataset, cache_dir=args.cache)

    # open output file
    output_json = open(file=args.output, mode="w", encoding="utf-8")

    mask_records = {}

    output_dataset = {col: [] for col in dataset["train"].column_names}
    print(output_dataset)

    for idx, item in enumerate(dataset["train"]):
        if idx == 20:
            break
        code_content = item["content"]  # specify the key if not compatible
        masked_lines = []
        key = generate_key(args, item)

        for line_idx, line_content in enumerate(code_content.split("\n")):
            if should_mask(args, item):
                mask_records.setdefault(key, {})
                mask_records[key][line_idx] = line_content
                line_content = "<MASK>"

            masked_lines.append(line_content)

        masked_line = "\n".join(masked_lines)
        item["content"] = masked_line
        for col in output_dataset:
            output_dataset[col].append(item[col])

    json.dump(mask_records, output_json, ensure_ascii=False)
    output_dataset = Dataset.from_dict(output_dataset)
    output_dataset.save_to_disk(args.output_dataset)
    output_dataset.push_to_hub("ZujiZhou/Exact_Dedup_MASK")


if __name__ == "__main__":
    main()
