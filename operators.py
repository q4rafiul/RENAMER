import bpy
from .utils import mirror_name, apply_case, generate_sequence


# ─────────── Populate Table ───────────
def populate_items(props, context):
    sel_objs = context.selected_objects
    if not sel_objs:
        props.has_valid_items = False
        return

    ptype = props.property_type
    added = False

    # Preserve previous checkbox states
    prev_state = {
        (i.obj_name, i.current_name): {
            "selected": i.selected,
            "mirror": i.mirror,
            "new_name": i.new_name
        }
        for i in props.items
    }

    def add_item(obj, name, source):
        key = (obj.name, name)
        if any(i.obj_name == obj.name and i.current_name == name for i in props.items):
            return
        item = props.items.add()
        item.current_name = name
        item.new_name = name
        item.obj_name = obj.name
        item.source_type = source
        if key in prev_state:
            state = prev_state[key]
            item.selected = state["selected"]
            item.mirror = state["mirror"]
            item.new_name = state["new_name"]  # preserve manually edited names
        else:
            item.selected = True
            item.mirror = False

    # Clear collection before repopulating
    props.items.clear()

    # Multi-selection → just show object names
    if len(sel_objs) > 1 or ptype == "OBJECTS":
        for obj in sel_objs:
            add_item(obj, obj.name, "objects")
            added = True
        props.has_valid_items = True
        return

    # Single object → other property types
    obj = sel_objs[0]
    if obj.type == "MESH":
        if ptype == "VERTEX_GROUPS":
            for vg in obj.vertex_groups: add_item(obj, vg.name, "vertex_groups"); added=True
        elif ptype == "SHAPE_KEYS" and obj.data.shape_keys:
            for sk in obj.data.shape_keys.key_blocks: add_item(obj, sk.name, "shape_keys"); added=True
        elif ptype == "UV_MAPS":
            for uv in obj.data.uv_layers: add_item(obj, uv.name, "uv_maps"); added=True
        elif ptype == "MATERIALS":
            for slot in obj.material_slots:
                if slot.material: add_item(obj, slot.material.name, "materials"); added=True
    
    elif obj.type == "ARMATURE" and ptype == "BONES":
        arm = obj
        # Detect selected bones depending on mode
        selected_bones = []
        mode = bpy.context.mode
        if mode == 'POSE':
            selected_bones = [b.name for b in arm.pose.bones if b.bone.select]
        elif mode == 'EDIT_ARMATURE':
            selected_bones = [b.name for b in arm.data.edit_bones if b.select]

        if selected_bones:
            # Only add selected ones
            for bone_name in selected_bones:
                add_item(arm, bone_name, "bones")
                added = True
        else:
            # If nothing selected → show all
            for bone in arm.data.bones:
                add_item(arm, bone.name, "bones")
                added = True

    if ptype == "ACTIONS" and obj.animation_data and obj.animation_data.action:
        add_item(obj, obj.animation_data.action.name, "actions"); added=True

    props.has_valid_items = added


# ─────────── Operators ───────────
# ─────────── Manage Delete
class RENAMER_OT_DeleteItem(bpy.types.Operator):
    bl_idname = "renamer.delete_item"
    bl_label = "Delete Item"
    index: bpy.props.IntProperty(default=-1)

    def execute(self, context):
        props = context.scene.renamer_props
        sel_objs = context.selected_objects

        # Collect indices first to avoid messing up collection while removing
        remove_indices = []
        for idx, item in enumerate(props.items):
            if not item.selected:
                continue
            if self.index >= 0 and idx != self.index:
                continue
            remove_indices.append(idx)

        for idx in reversed(remove_indices):
            item = props.items[idx]
            obj = bpy.data.objects.get(item.obj_name)
            stype = item.source_type
            try:
                if stype == "objects" and obj:
                    bpy.data.objects.remove(obj, do_unlink=True)
                elif stype == "vertex_groups" and obj:
                    vg = obj.vertex_groups.get(item.current_name)
                    if vg: obj.vertex_groups.remove(vg)
                elif stype == "shape_keys" and obj.type == "MESH":
                    if obj.data.shape_keys:
                        kb = obj.data.shape_keys.key_blocks.get(item.current_name)
                        if kb and kb.name != "Basis":
                            obj.shape_key_remove(kb)
                elif stype == "uv_maps" and obj.type == "MESH":
                    uv = obj.data.uv_layers.get(item.current_name)
                    if uv:
                        obj.data.uv_layers.remove(uv)
                elif stype == "materials" and obj:
                    for slot in obj.material_slots:
                        if slot.material and slot.material.name == item.current_name:
                            slot.material = None
                elif stype == "bones" and obj.type == "ARMATURE":
                    bpy.context.view_layer.objects.active = obj
                    prev_mode = bpy.context.mode
                    bpy.ops.object.mode_set(mode='EDIT')
                    edit_bone = obj.data.edit_bones.get(item.current_name)
                    if edit_bone: obj.data.edit_bones.remove(edit_bone)
                    bpy.ops.object.mode_set(mode=prev_mode)
                elif stype == "actions":
                    act = bpy.data.actions.get(item.current_name)
                    if act: bpy.data.actions.remove(act)
                props.items.remove(idx)
            except Exception as e:
                self.report({'WARNING'}, f"Delete failed for {item.current_name}: {e}")
        return {'FINISHED'}

# ─────────── Manage Prefix
class RENAMER_OT_ApplyPrefix(bpy.types.Operator):
    bl_idname = "renamer.apply_prefix"
    bl_label = "Apply Prefix"

    def execute(self, context):
        props = context.scene.renamer_props
        for item in props.items:
            if item.selected and props.prefix_text:
                item.new_name = f"{props.prefix_text}{item.current_name}"
        # Clear the input field after applying
        props.prefix_text = ""
        return {'FINISHED'}

# ─────────── Manage Suffix
class RENAMER_OT_ApplySuffix(bpy.types.Operator):
    bl_idname = "renamer.apply_suffix"
    bl_label = "Apply Suffix"

    def execute(self, context):
        props = context.scene.renamer_props
        for item in props.items:
            if item.selected and props.suffix_text:
                item.new_name = f"{item.current_name}{props.suffix_text}"
        # Clear the input field after applying
        props.suffix_text = ""
        return {'FINISHED'}

# ─────────── Manage Sequence
class RENAMER_OT_ApplySequence(bpy.types.Operator):
    bl_idname = "renamer.apply_sequence"
    bl_label = "Apply Sequence"
    bl_description = "Apply sequential names to selected items"
    direction: bpy.props.EnumProperty(
        items=[("DOWN", "↓", ""), ("UP", "↑", "")],
        default="DOWN"
    )

    def execute(self, context):
        props = context.scene.renamer_props
        selected_items = [i for i in props.items if i.selected]

        if not selected_items:
            self.report({'INFO'}, "No items selected for sequencing.")
            return {'CANCELLED'}

        if self.direction == "UP":
            selected_items.reverse()

        base = props.seq_base.strip() if props.seq_base else ""
        start = props.seq_start.strip() if props.seq_start else ""
        last = props.seq_last.strip() if props.seq_last else ""

        for idx, item in enumerate(selected_items):
            item.new_name = generate_sequence(base, start, idx, last)

        # Optionally clear fields after applying
        props.seq_base = ""
        props.seq_start = ""
        props.seq_last = ""
        return {'FINISHED'}

# ─────────── Manage Mirror
class RENAMER_OT_Mirror(bpy.types.Operator):
    bl_idname = "renamer.mirror"
    bl_label = "Mirror"
    index: bpy.props.IntProperty()

    def execute(self, context):
        props = context.scene.renamer_props
        item = props.items[self.index]

        # Toggle mirror behavior
        # If mirroring the current new_name gives us the current_name → revert
        if mirror_name(item.new_name) == item.current_name:
            item.new_name = item.current_name
        else:
            item.new_name = mirror_name(item.current_name)
        return {'FINISHED'}

# ─────────── Manage Case Convertion
class RENAMER_OT_CaseConversion(bpy.types.Operator):
    bl_idname = "renamer.case_conversion"
    bl_label = "Case Conversion"
    mode: bpy.props.StringProperty()

    def execute(self, context):
        props = context.scene.renamer_props
        for item in props.items:
            if item.selected:
                item.new_name = apply_case(item.current_name, self.mode)
        return {'FINISHED'}

# ─────────── Manage Clear
class RENAMER_OT_Clear(bpy.types.Operator):
    bl_idname = "renamer.clear"
    bl_label = "Clear New Names"

    def execute(self, context):
        props = context.scene.renamer_props
        for item in props.items:
            item.new_name = ""
        self.report({'INFO'}, "Cleared all new names.")
        return {'FINISHED'}

# ─────────── Manage Invert Selection
class RENAMER_OT_InvertSelection(bpy.types.Operator):
    bl_idname = "renamer.invert_selection"
    bl_label = "Invert Selection"

    def execute(self, context):
        props = context.scene.renamer_props
        if not props.items:
            self.report({'INFO'}, "No items to invert.")
            return {'CANCELLED'}

        for item in props.items:
            item.selected = not item.selected

        return {'FINISHED'}

# ─────────── Manage Execute
class RENAMER_OT_Execute(bpy.types.Operator):
    bl_idname = "renamer.execute"
    bl_label = "Execute Rename"
    
    def execute(self, context):
        props = context.scene.renamer_props
        for item in props.items:
            if not item.selected or not item.new_name: continue
            obj = bpy.data.objects.get(item.obj_name)
            stype = item.source_type
            try:
                if stype == "objects" and obj: obj.name = item.new_name
                elif stype == "vertex_groups" and obj:
                    vg = obj.vertex_groups.get(item.current_name)
                    if vg: vg.name = item.new_name
                elif stype == "shape_keys" and obj.data.shape_keys:
                    kb = obj.data.shape_keys.key_blocks.get(item.current_name)
                    if kb: kb.name = item.new_name
                elif stype == "uv_maps" and obj:
                    uv = obj.data.uv_layers.get(item.current_name)
                    if uv: uv.name = item.new_name
                elif stype == "materials" and obj:
                    for slot in obj.material_slots:
                        if slot.material and slot.material.name == item.current_name:
                            slot.material.name = item.new_name; break
                elif stype == "bones" and obj and obj.type=="ARMATURE":
                    bone = obj.data.bones.get(item.current_name)
                    if bone: bone.name = item.new_name
                elif stype == "actions":
                    act = bpy.data.actions.get(item.current_name)
                    if act: act.name = item.new_name
                item.current_name = item.new_name
            except Exception as e: self.report({'WARNING'}, f"Rename failed for {item.current_name}: {e}")
        return {'FINISHED'}


# ─────────── Refresh ON selection / property change ───────────
def refresh_table(scene):
    props = scene.renamer_props
    sel_objs = list(bpy.context.selected_objects)
    sel_names = [obj.name for obj in sel_objs]

    # Determine if selection or property_type changed
    selection_changed = sel_names != getattr(props, "last_sel_names", [])
    property_changed = getattr(props, "last_property_type", "") != props.property_type

    # Only refresh if selection changed or property type changed
    if selection_changed or property_changed:
        # Update stored state
        props.last_sel_names = sel_names
        props.last_property_type = props.property_type

        # Automatically set property_type for multi-selection
        if len(sel_objs) > 1:
            props.property_type = 'OBJECTS'

        # Populate the table
        populate_items(props, bpy.context)


# ─────────── Register/UnRegister ───────────
classes = [
    RENAMER_OT_DeleteItem, RENAMER_OT_ApplyPrefix, RENAMER_OT_ApplySuffix,
    RENAMER_OT_ApplySequence, RENAMER_OT_Mirror, RENAMER_OT_CaseConversion,
    RENAMER_OT_Execute, RENAMER_OT_Clear, RENAMER_OT_InvertSelection
]

def register():
    for cls in classes: bpy.utils.register_class(cls)
    bpy.app.handlers.depsgraph_update_post.append(refresh_table)

def unregister():
    for cls in reversed(classes): bpy.utils.unregister_class(cls)
    if refresh_table in bpy.app.handlers.depsgraph_update_post:
        bpy.app.handlers.depsgraph_update_post.remove(refresh_table)