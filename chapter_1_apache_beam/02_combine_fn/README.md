### Example on `CombineFn`

This example shows how to use the Transform `CombineFn`. To work with this code, it is necessary to create an initial log files with `generate_data.py` script.

### Run the example:

Generate the data

```bash
python generate_data.py
```

Run the combine pipeline

```bash
DATE=$(date + %Y%m%d)
python combine --input-file -log_entries_large.txt --output-file output-word-count-${DATE}.txt
```