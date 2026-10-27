# Faia Blender Tools

A Blender add-on with production tools for game studios, developed by [Faia Studio](https://github.com/faia-studio).

---

## Requirements

- Blender 5.2.2 LTS (or compatible version)
- FBX add-on enabled in Blender (enabled by default)

---

## Installation

1. Download `faia_blender_tools.zip` from the [latest release](https://github.com/alandlb92/faia-blender-tools/releases/latest).
2. Open Blender → **Edit → Preferences → Add-ons → Install from Disk**.
3. Select the `.zip` file and click **Install Add-on**.
4. Enable the add-on by checking the checkbox next to **Faia Blender Tools**.

After installation, a **FAIA** menu appears in Blender's top application menu bar.

### Building locally

Run `build.bat` at the project root to generate `faia_blender_tools.zip` for local testing.

---

## Tools

### Export Collection to FBX

Exports every compatible object inside a Collection to a separate `.fbx` file.

- Select a Collection and a destination folder.
- Each Mesh, Curve, and Armature is exported individually.
- Objects are temporarily moved to the world origin for export — the original scene is never modified.
- Files are named after the object (`SM_Wall` → `SM_Wall.fbx`). Existing files are overwritten silently.
- **Live preview** in the dialog shows which files will be overwritten and which are new before confirming.
- If an object fails to export, the rest continue normally.

**Access:** FAIA → Export Collection to FBX

---

### Transform Checker

A table-based inspector for reviewing and fixing Rotation and Scale on objects in a Collection.

- Shows each object's vertex count, local scale, and local rotation.
- Objects with non-standard transforms (scale ≠ 1 or rotation ≠ 0°) are highlighted in red.
- Apply Scale or Rotation per object, or use **Apply Scale for All** / **Apply Rotation for All**.
- **Revert Last Apply** restores the previous transforms directly (no Ctrl+Z dependency).

**Access:** FAIA → Transform Checker

---

### Asset Checker

Validates that all mesh objects in the scene follow the studio's asset organisation pattern.

- **Assets** — objects marked as assets (`obj.asset_data` set).
- **Linked Copies** — objects sharing the data block of a marked asset (created with Ctrl+D).
- **Unexpected** — objects that are neither an asset nor a linked copy; shown with a warning.
- Each entry has a **Select** button to jump to that object in the viewport without closing the dialog.

**Access:** FAIA → Asset Checker

---

### Export Scene to JSON

Exports a Blender scene layout as a JSON file to be imported by the companion Unreal Engine plugin. Eliminates the need to manually recreate level layouts in Unreal after assembling them in Blender.

**Workflow:**
1. Keep all base assets in an **Assets Collection** (objects marked as assets in Blender, named exactly as the corresponding Unreal assets — e.g. `SM_Wall_01`).
2. Build the level layout in a **Scene Collection** using Alt+D instances from the Assets Collection. Organise sub-collections freely — each sub-collection becomes a sub-folder in Unreal.
3. Run **Export Scene to JSON** and pick the Scene Collection, Assets Collection, and output `.json` path.

**What the operator does:**
- Validates that every object in the Scene Collection is an instance of a known asset. Cancels with an error if any object is unrecognised.
- Renames instances to stable unique actor names: `SM_Wall_01_1`, `SM_Wall_01_2`, etc. These names persist in the `.blend` and serve as IDs for re-import matching in Unreal.
- Converts all transforms from Blender space (metres, Z-up/Y-forward) to Unreal space (centimetres, Z-up/X-forward).

**JSON structure:**
```json
{
  "version": "1.0.0",
  "assets": ["SM_Floor", "SM_Pillar", "SM_Wall_01"],
  "objects": [
    {
      "actor_name": "SM_Wall_01_1",
      "asset":      "SM_Wall_01",
      "folder":     "Level_Mausoleum/Walls",
      "location":   [0.0, 400.0, 0.0],
      "rotation":   [0.0, 90.0, 0.0],
      "scale":      [1.0, 1.0, 1.0]
    }
  ]
}
```

- `assets` — all Unreal assets the importer needs to resolve before spawning actors.
- `actor_name` — unique stable name; Unreal uses this to update existing actors on re-import instead of spawning duplicates.
- `folder` — full collection path from the scene root, used as the Unreal sub-folder/layer name.
- `location` — Unreal centimetres, X-forward.
- `rotation` — Euler degrees (Pitch, Yaw, Roll) in Unreal convention.

**Access:** FAIA → Export Scene to JSON

---

### UV: Faia Unwrap Size Based

Unwraps **selected faces** and scales UVs so that one UV tile represents a defined real-world size. Designed for tiling textures — no margin is added between islands.

- Select the faces to unwrap in Edit Mode, then run the operator.
- Set the texture world size in meters (e.g. `4.0` means 1 UV tile = 4 m × 4 m).
- Scale is computed from the actual 3D surface area of the selected faces — works correctly for planar, curved, and multi-orientation selections (e.g. two opposite walls).
- Objects larger than the tile size extend beyond UV space, which is correct for tiling textures.

**Access:** FAIA → UV → Faia Unwrap Size Based  
Also available via `U` shortcut in the 3D Viewport (Edit Mode) and in the UV Editor.

---

## Known Limitations

| # | Limitation |
|---|------------|
| 1 | The FBX exporter is labeled "Legacy" in Blender 5.2 — functionality is unchanged but parameters may shift in future versions. |
| 2 | UV rotation display in Transform Checker uses Euler angles regardless of the object's rotation mode. Apply Rotation works correctly for all rotation modes. |
| 3 | Vertex count shows the base mesh vertex count (before modifiers). |
| 4 | Revert (Transform Checker) does not recover objects that were renamed between Apply and Revert. |
| 5 | Object types not supported by FBX (LIGHT, CAMERA, METABALL, GPENCIL, etc.) are silently skipped with a console message. |
| 6 | UV Unwrap Size Based acts only on the active object in Edit Mode. Requires at least one face selected. |
| 7 | Asset Checker checks the current scene only; does not filter by collection. |

---

## License

MIT License — see [LICENSE](LICENSE) for details.
