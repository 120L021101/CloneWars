import argparse


def arg_parser():
    parser = argparse.ArgumentParser(
        description="Process a dataset for code completion tasks."
    )

    parser.add_argument(
        "--dataset", type=str, required=True, help="The name of the dataset to process."
    )

    parser.add_argument(
        "--cache",
        type=str,
        required=False,
        help="if you've already downloaded the dataset, specify the cache dir if you specified when downloading",
    )

    parser.add_argument(
        "--mask_p",
        type=float,
        required=False,
        default=0.2,
        help="the mask possibilty of a line, e.g. set to 0.3, then 3 out of 10 will be masked",
    )

    parser.add_argument(
        "--output",
        type=str,
        required=False,
        default="./mask.json",
        help="the output json file path, default value is ./mask.json",
    )

    parser.add_argument(
        "--output_dataset",
        type=str,
        required=True,
        help="the output path of the masked dataset",
    )

    args = parser.parse_args()

    dataset_name = args.dataset
    print(f"Processing dataset: {dataset_name}")

    cache_dir = args.cache
    print(f"Processed dataset is in: {cache_dir}")

    return args
