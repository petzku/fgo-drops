# Fate/Grand Order drop efficiency calculator

Fairly simple pair of scripts I made to optimize my material farming in FGO.

Calculates the APD (average AP per drop) for each material based on the best node considering only that material, and a total AP efficiency for each node based on its material drop rates and their APD values.

## Usage

Needs python 3 to run. Version 3.6 or newer definitely works, older ones might too.

To use, first run `get_drop_data.py` to fetch the drop data from Gamepress, then run `drop_efficiency.py` to get the results:

```sh
$ python3 get_drop_data.py

Found title: Fuyuki
Found title: Orleans
Found title: Septem
Found title: Okeanos
...
starting: Gotterdammerung
done: Gotterdammerung
exporting json... done

$ python3 drop_efficiency.py

# Aurora Steel
  Gotterdammerung -- Clone Shelter                   -- 1.62  82.4
  Gotterdammerung -- Armory of the Fallen            -- 1.49  87.1
  Gotterdammerung -- Frost Breathing Mountains       -- 1.23  85.0
  Gotterdammerung -- Closed Shelter                  -- 1.14  84.0
  Gotterdammerung -- Viaduct of Ice                  -- 1.00  54.0
```

The latter script outputs some data to the console (specified in the `OUTPUT` list in `config.py`). The default list at the time of writing is the non-gold materials required for maxing Skadi.

The script outputs all the data into some JSON files. The most interesting one of these is probably `locations_efficiency.json`. It contains data like the following (reformatted):

```json
"Stake of Wailing Night": [
  [ "Salem -- Crow's Nest", 1.6093342981186687, 49.87531172069825 ],
  [ "Salem -- Commons View", 1.308101881108203, 52.10918114143921 ],
  [ "Salem -- Purity Domain", 1.1573554132116468, 51.34474327628362 ],
  [ "Salem -- Seven Gables", 1.1483366040286123, 52.10918114143921 ],
  [ "Salem -- Execution Site", 1.0, 30.39073806078148 ]
],
```

That is, for each material, a list of the places that drop it, the AP efficiency of that node, and the material's APD at that node. The list is sorted in order of AP efficiency (higher is better). Nodes with lower than 1.0 efficiency are left out, as these should be obviously worse than any other option. A notable exception is Evil Bones: X-G is only slightly less efficient than X-C, but much faster to farm.
