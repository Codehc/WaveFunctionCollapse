# Init
```
pip3 install Pillow
pip3 install numpy
```

## Color Map WFC Algorithm
Run `color_map_wfc.py` after installing Pillow and numpy. Last generated map will be pushed into the `out` folder as `map.png`.

## Side Constraints WFC Algorithm
Run `rng_world.py` after installing Pillow and numpy. Last generated map will be pushed into the `out` folder as `map.png`. Edit the tiles, `constraints.json`, seed in `world_seed.json`, and the code in `rng_world.py` that mentions the names of the nodes in order to add, remove, or edit nodes in any way.

## Original Explicit Constraints WFC Algorithm
Unsupported. It might still work but I won't really put work into fixing it anymore since it's not the algorithm I intend to continue using and isn't optimal at all.