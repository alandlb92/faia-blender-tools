# Faia Blender Tools

A Blender add-on with production tools for game studios, developed by [Faia Studio](https://github.com/faia-studio).

---

## Requirements

- Blender 5.2.2 LTS (or compatible version)
- FBX add-on enabled in Blender (enabled by default)

---

## Installation

1. Download or clone this repository.
2. Zip the `faia_blender_tools/` folder.
3. Open Blender → **Edit → Preferences → Add-ons → Install from Disk**.
4. Select the `.zip` file and click **Install Add-on**.
5. Enable the add-on by checking the checkbox next to **Faia Blender Tools**.

After installation, a **FAIA** menu appears in Blender's top application menu bar.

---

## Tools

### Export Collection to FBX

Exports every compatible object inside a Collection to a separate `.fbx` file.

- Select a Collection and a destination folder.
- Each Mesh, Curve, and Armature is exported individually.
- Objects are temporarily moved to the world origin for export — the original scene is never modified.
- Files are named after the object (`SM_Wall` → `SM_Wall.fbx`). Existing files are overwritten silently.
- If an object fails to export, the rest continue normally.

**Access:** FAIA → Export Collection to FBX

---

### Check Destination Files

Compares the objects in a Collection against the `.fbx` files already present in a folder.

- Reports which objects already have a corresponding FBX and which are missing.
- Case-insensitive comparison.
- Does not export, modify, or delete anything.
- Result is shown in Blender's Info bar and system console.

**Access:** FAIA → Check Destination Files

---

### Transform Checker

A table-based inspector for reviewing and fixing Rotation and Scale on objects in a Collection.

- Shows each object's vertex count, local scale, and local rotation.
- Objects with non-standard transforms (scale ≠ 1 or rotation ≠ 0°) are highlighted in red.
- Apply Scale or Rotation per object, or use **Apply Scale for All** / **Apply Rotation for All**.
- **Revert Last Apply** restores the previous transforms directly (no Ctrl+Z dependency).

**Access:** FAIA → Transform Checker

---

## Known Limitations

| # | Limitation |
|---|------------|
| 1 | The FBX exporter is labeled "Legacy" in Blender 5.2 — functionality is unchanged but parameters may shift in future versions. |
| 2 | Rotation display in Transform Checker uses Euler angles regardless of the object's rotation mode. Apply Rotation works correctly for all rotation modes. |
| 3 | Vertex count shows the base mesh vertex count (before modifiers). |
| 4 | Revert does not recover objects that were renamed between Apply and Revert. |
| 5 | Object types not supported by FBX (LIGHT, CAMERA, METABALL, GPENCIL, etc.) are silently skipped with a console message. |
| 6 | The Transform Checker popup closes if you click outside it — reopen it from the FAIA menu. |

---

## License

MIT License — see [LICENSE](LICENSE) for details.
