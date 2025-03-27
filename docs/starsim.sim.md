

## Simulation Parameters

This function sets up the parameters for a simulation. While it's usually used internally, you can explore or modify parameters by creating a simulation and accessing `.pars`:

```python
sim = ss.Sim()
print(sim.pars)
```

### Parameters

- **`label`** (`str`):  
  A name or label for the simulation.

- **`n_agents`** (`int` or `float`, default = `10_000`):  
  Number of agents to include in the simulation.

- **`total_pop`** (`int` or `float`, optional):  
  If provided, the agent population will be scaled to represent this effective total population size.

- **`pop_scale`** (`float`, optional):  
  An alternative to `total_pop`. Defines a scaling factor between agents and population:  
  `total_pop = n_agents * pop_scale`.

- **`unit`** (`str`, default = `'year'`):  
  Time unit for the simulation. Options include:
  - `'day'`
  - `'week'`
  - `'month'`
  - `'year'` (default)

- **`start`** (`float`, `str`, or `date`, default = `2000`):  
  Starting point of the simulation. Can be a numeric year (e.g. `2000`), a date string, or a `date` object.

- **`stop`** (`float`, `str`, or `date`, optional):  
  Ending point of the simulation. If not provided, duration (`dur`) will be used instead.

- **`dur`** (`int`, default = `50`):  
  Number of time steps to simulate (used if `stop` is not set).

- **`dt`** (`float`, default = `1.0`):  
  Time step size in units of `unit`.

- **`rand_seed`** (`int`, optional):  
  Random seed for reproducibility. Used to initialize all module-specific random number generators.

- **`birth_rate`** (`float`, optional):  
  If provided, adds births at this rate (per 1000 people per year).

- **`death_rate`** (`float`, optional):  
  If provided, adds deaths at this rate (per 1000 people per year).

- **`use_aging`** (`bool`, optional):  
  Whether agents should age during the simulation. By default, agents age if births and/or deaths are included.

- **`people`** (`People`, optional):  
  A pre-existing `People` object to use. If supplied, `n_agents` will be ignored.

- **`networks`** (`str`, `list`, or `Module`):  
  Network module(s) used in the simulation. Can be a string name, a module object, or a list of modules.

- **`demographics`**, **`diseases`**, **`connectors`**, **`interventions`**, **`analyzers`** (`str`, `list`, or `Module`):  
  Same format as `networks`. Define different modules to model demographic structure, disease transmission, logic connectors, interventions, or custom data analysis.

- **`verbose`** (`float`, optional):  
  Controls simulation output. For example:
  - `1.0` = print every time step  
  - `0.1` = print every 10 steps  
  - `0` = silent mode  

