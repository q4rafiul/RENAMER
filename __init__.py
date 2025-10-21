# ─────────── Addon Info ───────────
bl_info = {
    "name": "RENAMER",
    "author": "q4rafiul",
    "version": (0, 4, 2, 9),
    "blender": (3, 0, 0),
    "location": "View3D > N-panel > RENAMER",
    "description": "A clean, no-nonsense renaming tool for Blender. Rename objects, bones, shape keys, materials, vertex groups, UV maps — fast, safe, and fun.",
    "category": "Object"
}

import bpy
from . import data, operators, ui


# ─────────── Register/UnRegister ───────────
def register():
    data.register()
    operators.register()
    ui.register()
    print("RENAMER loaded!")

def unregister():
    ui.unregister()
    operators.unregister()
    data.unregister()
    print("RENAMER unloaded!")

if __name__ == "__main__":
    register()