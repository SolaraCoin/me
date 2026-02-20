# Tools

## countdown_alert.py

External countdown watcher (no browser automation).

It alerts when remaining time is below a threshold (default: `54`).

### Mode 1: stdin (manual input)

```bash
python3 tools/countdown_alert.py --threshold 54 --source stdin
```

### Mode 2: file watcher (external feed)

If another tool writes remaining timer values into a file (e.g. OCR pipeline), this tool can watch it:

```bash
python3 tools/countdown_alert.py --source file --file /tmp/countdown.txt --threshold 54
```

Then update the file from anywhere:

```bash
echo "00:53" > /tmp/countdown.txt
```

### Options

- `--threshold`: alert under this number of seconds (default `54`)
- `--once`: exit after first alert
- `--poll-ms`: polling interval (default `250`)
- `--source`: `stdin` or `file`
- `--file`: path to watched file for file mode

### Safety notes

- No browser automation.
- No auto-clicking.
- No stealth/evasion behavior.
