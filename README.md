# cronscope

> Visualizer and validator for cron expressions with next-run previews and timezone awareness

---

## Installation

```bash
pip install cronscope
```

---

## Usage

```python
from cronscope import CronScope

cs = CronScope("0 9 * * MON-FRI", timezone="America/New_York")

# Validate the expression
print(cs.is_valid())  # True

# Preview the next 5 scheduled runs
for run in cs.next_runs(5):
    print(run)

# 2024-05-06 09:00:00-04:00
# 2024-05-07 09:00:00-04:00
# 2024-05-08 09:00:00-04:00
# 2024-05-09 09:00:00-04:00
# 2024-05-10 09:00:00-04:00
```

You can also use the CLI:

```bash
cronscope "*/15 * * * *" --tz UTC --next 3
```

```
Next 3 runs for: */15 * * * *  [UTC]
  1. 2024-05-06 14:15:00+00:00
  2. 2024-05-06 14:30:00+00:00
  3. 2024-05-06 14:45:00+00:00
```

---

## Features

- ✅ Full cron expression validation with human-readable error messages
- 🕐 Next-run previews for any number of upcoming executions
- 🌍 Timezone-aware scheduling via `zoneinfo` / `pytz`
- 💻 Simple Python API and CLI interface

---

## License

This project is licensed under the [MIT License](LICENSE).