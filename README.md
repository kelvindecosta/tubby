# Tubby

<p align=center>

  <img src="https://raw.githubusercontent.com/kelvindecosta/tubby/master/assets/logo.png" height="200px"/>

  <br>
  <span>A utility for the <a href="https://genshin-impact.fandom.com/wiki/Housing">Genshin Impact Housing system</a>.</span>
  <br>
  <img alt="PyPI - Status" src="https://img.shields.io/pypi/status/tubby">
  <a target="_blank" href="https://pypi.python.org/pypi/tubby/"><img alt="pypi package" src="https://img.shields.io/pypi/v/tubby?color=light%20green"></a>
  <a target="_blank" href="https://github.com/kelvindecosta/tubby/blob/master/LICENSE" title="License: MIT"><img alt="GitHub" src="https://img.shields.io/github/license/kelvindecosta/tubby"></a>
</p>

<p align="center">
  <a href="#installation">Installation</a>
  &nbsp;&nbsp;&nbsp;|&nbsp;&nbsp;&nbsp;
  <a href="#usage">Usage</a>
  &nbsp;&nbsp;&nbsp;|&nbsp;&nbsp;&nbsp;
  <a href="#workflow">Workflow</a>
  &nbsp;&nbsp;&nbsp;|&nbsp;&nbsp;&nbsp;
  <a href="https://github.com/kelvindecosta/tubby/blob/master/CONTRIBUTING.md">Contributing</a>
</p>

## Installation

```bash
pip install tubby
```

> ### Verification
>
> To verify that Tubby is installed, run:
>
> ```bash
> python -c "import tubby"
> ```

## Usage

Run the following command to display a helpful message:

```bash
tubby -h
```

```
Usage: tubby [options] <command> [Args]

  A utility for the Genshin Impact Housing system

Options:
  -h, --help  Show this message and exit.

Commands:
  analyze   Performs analysis on inventory
  backup    Creates or loads inventory backup
  download  Downloads housing metadata
  info      Displays package information
  manage    Manages inventory
  reset     Resets inventory
```

## Workflow

### `download` metadata from the Genshin Impact Wiki

Tubby scrapes the [Wiki](https://genshin-impact.fandom.com/wiki/Genshin_Impact_Wiki) and collects relevant metadata for the housing sets and furnishings.

```bash
tubby download
```

```
Refreshing sources...

Gathering 342 Furnishings...
100%|█████████████████████████████████████████████████████████████████████████████| 342/342 [01:56<00:00,  2.93page/s]

Gathering 45 Sets...
100%|███████████████████████████████████████████████████████████████████████████████| 45/45 [00:16<00:00,  2.72page/s]

Housing metadata updated!
```

---

### `manage` your inventory

Start tracking your in-game inventory of characters, materials, furnishings and sets.

```bash
tubby manage
```

![Manage menu](https://raw.githubusercontent.com/kelvindecosta/tubby/master/assets/manage.png)

<details>

<summary>Companions</summary>

![Manage companions menu](https://raw.githubusercontent.com/kelvindecosta/tubby/master/assets/manage-companions.png)

</details>

<details>

<summary>Materials</summary>

![Manage materials menu](https://raw.githubusercontent.com/kelvindecosta/tubby/master/assets/manage-materials.png)

</details>

<details>

<summary>Furnishings</summary>

![Manage furnishings menu](https://raw.githubusercontent.com/kelvindecosta/tubby/master/assets/manage-furnishings.png)

![Manage furnishing menu](https://raw.githubusercontent.com/kelvindecosta/tubby/master/assets/manage-furnishing.png)

</details>

<details>

<summary>Sets</summary>

![Manage sets menu](https://raw.githubusercontent.com/kelvindecosta/tubby/master/assets/manage-sets.png)

![Manage set menu](https://raw.githubusercontent.com/kelvindecosta/tubby/master/assets/manage-set.png)

</details>

> To navigate between the menus, use:
>
> - <kbd>Enter</kbd> to select an option,
> - <kbd>↑</kbd> & <kbd>↓</kbd> to cycle through the options,
> - <kbd>/</kbd> to open a search prompt, and
> - <kbd>Esc</kbd> to return to the previous menu/ quit.

---

### `analyze` your inventory

Find out how many of which resources (materials, currency, missing furnishings, etc.) are required to meet certain milestones.

```bash
tubby analyze
```

![Analyze menu](https://raw.githubusercontent.com/kelvindecosta/tubby/master/assets/analyze.png)

<details>

<summary>Materials</summary>

![Analyze materials menu](https://raw.githubusercontent.com/kelvindecosta/tubby/master/assets/analyze-materials.png)

</details>

<details>

<summary>Currency</summary>

![Analyze currency menu](https://raw.githubusercontent.com/kelvindecosta/tubby/master/assets/analyze-currency.png)

</details>

<details>

<summary>Furnishings</summary>

![Analyze furnishings menu](https://raw.githubusercontent.com/kelvindecosta/tubby/master/assets/analyze-furnishings.png)

![Analyze furnishing menu](https://raw.githubusercontent.com/kelvindecosta/tubby/master/assets/analyze-furnishing.png)

</details>

<details>

<summary>Sets</summary>

![Analyze sets menu](https://raw.githubusercontent.com/kelvindecosta/tubby/master/assets/analyze-sets.png)

![Analyze set menu](https://raw.githubusercontent.com/kelvindecosta/tubby/master/assets/analyze-set.png)

</details>

---

### import / export `backup` inventory data

Create backups of the information saved with Tubby and export them later.

<details>

<summary>Import backup from file</summary>

```bash
tubby backup -i backup/my_inventory.json
```

```
Are you sure you want to import inventory from 'backup/my_inventory.json'? [y/N]: y
Imported backup!
```

</details>

<details>

<summary>Export backup to file</summary>

```bash
tubby backup -e backup/my_inventory.json
```

```
Are you sure you want to export inventory to 'backup/my_inventory.json'? [y/N]: y
Exported backup!
```

</details>

> Tubby uses `.json` files for storing data.

---

### `reset` data

Deletes information loaded into Tubby.

```bash
tubby reset
```

```
Are you sure you want to delete your inventory? [y/N]: y
Deleted inventory!
```

> This resets only the inventory data.
> Metadata is not deleted.

## Contributing

Do you have a feature request, bug report, or patch? Great! Check out the [contributing guidelines](https://github.com/kelvindecosta/tubby/blob/master/CONTRIBUTING.md)!

## License

Copyright (c) 2021 Kelvin DeCosta. Released under the MIT License. See [LICENSE](https://github.com/kelvindecosta/tubby/blob/master/LICENSE) for details.

This project is not affiliated with or endorsed by miHoYo.
Genshin Impact and miHoYo are trademarks or registered trademarks of miHoYo.
Genshin Impact © miHoYo.
