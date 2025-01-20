import click
from datasets import load_dataset, Dataset
import pickle
import os
import hashlib
import sys
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))
from exact_dedup_function import extract
import nltk
from nltk.tokenize import word_tokenize
from nltk.util import ngrams
from datasketch import MinHash, MinHashLSH, LeanMinHash

def main():
    return True

if __name__ == "__main__":
    # Setup to download the dataset and allow us to make use of it
    nltk.download('punkt_tab')
    dataset = load_dataset("Razvan27/ML4SE-Python", cache_dir="/scratch/aimanabdulwaha/team-14")

    # Loop through all functions and check for near-duplicates
    deduped_code = []
    lean_minhashes_and_func_defs = []

    train_size = len(dataset['train'])
    i = 0
    file_index = 0
    num_perm = 50

    while i < train_size:
        try:
            if i == 1000: break
            item = dataset['train'][i]
            content = item['content']

            # Setup to allow us to deduplicate the dataset, but is hardcoded for this specific dataset.
            file_name, file_path, language = item['file_name'], item['file_path'], item['language']

            # Just logs progress
            if i % 100 == 0:
                print(f"Processing item {i + 1}/{train_size} ({(i + 1) / train_size * 100:.2f}%)")
            # tokenises the incoming function and sets ngrams
            tokens = nltk.word_tokenize(content)
            ngrams_list = list(ngrams(tokens, 5))
            ngrams_set = set([' '.join(ngram) for ngram in ngrams_list])

            # create leanminhash object and update it
            minhash = MinHash(num_perm=num_perm)
            for shingle in ngrams_set:
                minhash.update(shingle.encode('utf8'))
            lean_minhash = LeanMinHash(minhash)
            lean_minhashes_and_func_defs.append(
                    (lean_minhash, content, file_name, file_path, language, item['repo_stars']))

            # Make a small log every 100,000 iterations just so if something interrupts it we have partial data
            if len(lean_minhashes_and_func_defs) >= 100000:
                file_index += 1
                file_path = f"/scratch/aimanabdulwaha/deduped_file/team-14/ML4SE-func-{file_index}.pkl"
                with open(file_path, 'wb') as f:
                    pickle.dump(lean_minhashes_and_func_defs, f)
                lean_minhashes_and_func_defs = []
            i += 1
        except:
            # If something happens we just go next
            i += 1
            pass

    # Just makes sure that the last instance that was run is also saved properly.
    if len(lean_minhashes_and_func_defs) != 0:
        file_index += 1
        file_path = f"/scratch/aimanabdulwaha/deduped_file/team-14/ML4SE-func-{file_index}.pkl"
        with open(file_path, 'wb') as f:
            pickle.dump(lean_minhashes_and_func_defs, f)
        lean_minhashes_and_func_defs = []

    # Load all data and flatten it
    all_data = []
    for i in range(1, file_index + 1):
        file_path = f"/scratch/aimanabdulwaha/deduped_file/team-14/ML4SE-func-{i}.pkl"
        with open(file_path, 'rb') as f:
            # Extend the flattened list directly
            all_data.extend(pickle.load(f))

    # Sort the flattened list in descending order based on 'repo_stars'
    all_data = sorted(all_data, key=lambda x: int(x[5]), reverse=True)

    # Create LSH index. This is also where we set the threshold
    lsh = MinHashLSH(num_perm=num_perm, threshold=0.65)

    id = 0
    # Process the sorted data
    for lean_minhash, content, file_name, file_path, language, repo_stars in all_data:
        # Query the LSH to find similar functions
        similar_functions = lsh.query(lean_minhash)

        if similar_functions:
            # If there are similar functions, we skip adding the duplicate
            print(f"Function {id} is similar to: {similar_functions}")
        else:
            # Insert into LSH and append to deduped_code
            lsh.insert(id, lean_minhash)
            deduped_code.append((file_name, file_path, content, language, repo_stars))
            id += 1

    print("Deduplication complete.")
    print("length is: ", len(deduped_code))

    # Prepare to save data to disk
    deduped_dataset = Dataset.from_dict({
        'file_name': [data[0] for data in deduped_code],
        'file_path': [data[1] for data in deduped_code],
        'content': [data[2] for data in deduped_code],
        'language': [data[3] for data in deduped_code],
        'repo_stars': [data[4] for data in deduped_code]
    })

    deduped_dataset.save_to_disk(f"/scratch/aimanabdulwaha/final_deduped_file")

    # deduped_dataset.push_to_hub(f"aimanabdulwaha/Test2")
