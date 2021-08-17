# Luna
Component-based rigging system that allows to create rigs via Python or node based editor.
[Samples files](https://github.com/S0nic014/luna_sample_files) - Python and graph based rig builds.

---
## Installation
1. Clone repository using command
``` git clone --recurse-submodules -j8```
2. Create **luna.mod** in *documents/maya/modules*
3. Add the following lines to it:

```python
+ luna 0.2.1 YourPathHere/luna
scripts: YourPathHere/luna
```
4. Load plugin via Maya's plug-in manager
   

   

### Rig Builder
---
![Luna builder](docs/luna_builder.png)

### Plugin Menu
---
![Luna menu](docs/luna_menu.png)
### Selection based marking menu
---
![Luna marking menu](docs/luna_marking_menu.png)

---
