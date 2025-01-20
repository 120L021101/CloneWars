# Usage Instructions
Run the following command to view the documentation:

```bash
python util.py --help
```

Generally, it generates a new dataset with masked code and a json file tracks these masks

## Example Usage

python util.py --dataset ZujiZhou/ML4SE --cache /scratch/zujizhou/mask --output_dataset /scratch/zujizhou/mask_output/dataset --output /scratch/zujizhou/mask_output/output.json

the json will look like:

```json
{
    "git-cola_git-cola/test/core_test.py": {
        "0": "def test_core_decode():",
        "8": "    filename = helper.fixture('unicode.txt')",
        "11": "    assert expect == actual",
        "13": "    \"\"\"Ensure that decode(None) returns None\"\"\"",
        "15": "    actual = core.decode(None)",
        "17": "def test_decode_utf8():",
        "20": "    assert actual.encoding == 'utf-8'",
        "21": "def test_decode_non_utf8():",
        "22": "    filename = helper.fixture('cyrillic-cp1251.txt')",
        "31": "def test_guess_mimetype():",
        "32": "    value = '字龍.txt'",
        "33": "    expect = 'text/plain'"
    },
    "git-cola_git-cola/test/startup_test.py": {
        "10": "    assert actual.name == name",
        "11": "    assert actual.mode == startup.ICON_MODE",
        "13": "    assert actual.is_bookmark",
        "16": "def test_get_with_non_default_repo(app_context):",
        "24": "    builder = startup.BuildItem(app_context)",
        "27": "    assert actual.name == name",
        "30": "    assert actual.text() == name",
        "34": "    path = '/home/foo/git-cola'",
        "35": "    name = 'git-cola'",
        "37": "    is_bookmark = False",
        "47": "def test_get_with_list_mode(app_context):",
        "55": "    actual = builder.get(path, name, mode, is_bookmark)"
    }
}
```