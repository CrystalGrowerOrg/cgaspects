# Site Highlighting

Open the Site Highlighting dialog with **View → Highlight Sites** (`Ctrl+Shift+S`).

Site highlighting lets you colour-code specific lattice sites while showing the rest of the crystal in a uniform background colour. This is useful for identifying particular crystallographic positions, comparing sites from different analysis groups, or marking sites of interest.

---

## Background Colour

The **Background Colour** controls how non-highlighted sites appear:

| Option | Behaviour |
|--------|---------|
| Colour picker | All non-highlighted points use this colour |
| None (Use Existing) | Non-highlighted points keep their current colouring |

---

## Highlight Groups

Each group assigns a colour to a set of site numbers. You can define any number of groups simultaneously.

### Adding a Group

1. Enter site numbers in the input field using any combination of the formats below
2. Pick a colour for the group
3. Click **Add**

### Site Number Syntax

| Format | Example | Meaning |
|--------|---------|---------|
| Single | `5` | Site number 5 |
| List | `1,2,3` | Sites 1, 2, and 3 |
| Range | `10-20` | Sites 10 through 20 inclusive |
| Mixed | `1,5-10,15` | Sites 1, 5 through 10, and 15 |

### Managing Groups

- **Edit** — modify the site numbers or colour for a selected group
- **Remove** — delete the selected group
- **Clear All** — remove all highlight groups

---

## Applying Changes

- **Apply All** — update the viewport with all current group definitions
- **OK** — apply and close the dialog
- **Cancel** — discard changes and close

---

## Use Cases

- **Compare faces**: Highlight (100) face sites vs (010) face sites in different colours
- **Mark crystallization order**: Highlight sites that crystallized first vs last
- **Quality control**: Check that site numbers from analysis match the expected crystal positions

---

## Notes

- Site numbers correspond to the `site_number` column in the XYZ data (column 7 if present)
- If a site number does not exist in the loaded crystal, it is silently ignored
- Highlighted groups are cleared when a new XYZ file is loaded
