### Example on `CombineFn`



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