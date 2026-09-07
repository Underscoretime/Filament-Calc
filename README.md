# Filament Cost Calculator

Desktop app for calculating 3D printing costs based on filament usage and electricity consumption.

## Features

- Track filament inventory with color, material, weight, and stock
- Calculate print cost from filament weight and print time
- Convert between 53 currencies
- Filter and sort filament list by material
- Persistent storage via `filaments.json`

## Requirements

- Python 3.8+
- `tkinter` (included with standard Python on most systems)

## Usage

```bash
python main.py
```

## How it works

**Left panel** -- add/edit filaments with name, weight, cost per kg, material, color, and optional stock tracking.

**Right panel** -- select a filament, enter grams used and print time, set your electricity rate (default $0.025/hr), and hit Calculate.

All filament data is saved to `filaments.json` in the same directory as the script.

## Currency

Exchange rates are hardcoded and centered on USD. 53 currencies supported across Europe, Americas, Asia, Middle East, and Africa. Rates are approximate -- edit `BASE_RATES` in `main.py` to update them.

## License

None.
