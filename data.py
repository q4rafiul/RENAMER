import bpy
from bpy.props import StringProperty, BoolProperty, CollectionProperty, PointerProperty, EnumProperty, IntProperty


# ─────────── Manage Itemss ───────────
class RENAMER_Item(bpy.types.PropertyGroup):
    current_name: StringProperty()
    new_name: StringProperty()
    selected: BoolProperty(default=True)
    mirror: BoolProperty(default=False)
    obj_name: StringProperty(default="")
    source_type: StringProperty(default="")


# ─────────── Calling Populate from Operator.py to register ───────────
def property_type_update(self, context):
    from .operators import populate_items_operator
    populate_items_operator(context)


# ─────────── Manage Properties ───────────
class RENAMER_Properties(bpy.types.PropertyGroup):
    items: CollectionProperty(type=RENAMER_Item)
    
    # ─────────── For Prefix | Suffix | Sequence
    prefix_text: StringProperty(name="Prefix", default="")
    suffix_text: StringProperty(name="Suffix", default="")
    
    seq_base: StringProperty(name="Seq Name", default="")
    seq_start: StringProperty(name="Seq Num", default="1")
    seq_last: StringProperty(name="Seq Last", default="")
    
    case_mode: StringProperty(default="NONE")

    # ─────────── For Property Dropdown
    property_type: EnumProperty(
        name="Property Type",
        items=[
            ("VERTEX_GROUPS", "Vertex Groups", ""),
            ("SHAPE_KEYS", "Shape Keys", ""),
            ("UV_MAPS", "UV Maps", ""),
            ("MATERIALS", "Materials", ""),
            ("BONES", "Bones", ""),
            ("ACTIONS", "Actions", ""),
            ("OBJECTS", "Objects", ""),
        ],
        default='OBJECTS',
        update=property_type_update
    )

    # ─────────── For Prefix | Suffix | Sequence UI box
    show_extras: BoolProperty(default=False)
    show_prefix: BoolProperty(default=False)
    show_suffix: BoolProperty(default=False)
    show_sequence: BoolProperty(default=False)

    last_sel_count: IntProperty(default=0)
    has_valid_items: BoolProperty(default=False)


# ─────────── Register/UnRegister ───────────
def register():
    bpy.utils.register_class(RENAMER_Item)
    bpy.utils.register_class(RENAMER_Properties)
    bpy.types.Scene.renamer_props = PointerProperty(type=RENAMER_Properties)

def unregister():
    del bpy.types.Scene.renamer_props
    bpy.utils.unregister_class(RENAMER_Properties)
    bpy.utils.unregister_class(RENAMER_Item)