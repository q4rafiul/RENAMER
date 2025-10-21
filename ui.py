import bpy
from bpy.types import Panel


# ─────────── External Links ───────────
GITHUB_URL = "https://github.com/q4rafiul/RENAMER"
GUMROAD_URL = "https://q4rafiul.gumroad.com"


# ─────────── Draw UI ───────────
class RENAMER_PT_Panel(Panel):
    bl_label = "RENΔMER"
    bl_idname = "RENAMER_PT_panel"
    bl_space_type = "VIEW_3D"
    bl_region_type = "UI"
    bl_category = "RENAMER"

    def draw(self, context):
        layout = self.layout
        props = context.scene.renamer_props
        sel_objs = context.selected_objects

        # ─────────── Top Row: Title + Help Icon ───────────
        banner_box = layout.box()
        header_row = banner_box.row(align=True)
        header_row.label(text="RENΔMER")
        header_row.operator("wm.url_open", text="", icon="HELP").url = GITHUB_URL

        # Tagline inside the same box
        inner_col = banner_box.column(align=True)
        inner_col.label(text="“Every name tells a story, let’s kill it💀”")

        layout.separator()
        # ─────────── Object Info
        if len(sel_objs) == 1:
            obj = sel_objs[0]
            layout.prop(props, "property_type", text="Property")
            layout.label(text=f"Selected: {obj.name} ({obj.type.title()})")
        else:
            layout.prop(props, "property_type", text="Property")
            layout.label(text=f"{len(sel_objs)} objects selected — showing names")

        layout.separator()
        # ─────────── Extras Section
        box = layout.box()
        row = box.row(align=True)
        row.prop(props, "show_extras", text="", icon="TRIA_DOWN" if props.show_extras else "TRIA_RIGHT", emboss=False)
        row.label(text="Extras")

        if props.show_extras:
            # ─────────── Prefix
            prefix_box = box.box()
            row = prefix_box.row(align=True)
            row.prop(props, "show_prefix", text="", icon="TRIA_DOWN" if props.show_prefix else "TRIA_RIGHT", emboss=False)
            row.label(text="Prefix")
            if props.show_prefix:
                col = prefix_box.column(align=True)
                col.prop(props, "prefix_text", text="Text")
                col.separator()
                col.operator("renamer.apply_prefix", text="Apply Prefix")

            # ─────────── Suffix
            suffix_box = box.box()
            row = suffix_box.row(align=True)
            row.prop(props, "show_suffix", text="", icon="TRIA_DOWN" if props.show_suffix else "TRIA_RIGHT", emboss=False)
            row.label(text="Suffix")
            if props.show_suffix:
                col = suffix_box.column(align=True)
                col.prop(props, "suffix_text", text="Text")
                col.separator()
                col.operator("renamer.apply_suffix", text="Apply Suffix")

            # ─────────── Sequence
            seq_box = box.box()
            row = seq_box.row(align=True)
            row.prop(props, "show_sequence", text="", icon="TRIA_DOWN" if props.show_sequence else "TRIA_RIGHT", emboss=False)
            row.label(text="Sequence")
            if props.show_sequence:
                col = seq_box.column(align=True)
                col.prop(props, "seq_base", text="Base")
                col.separator()
                col.prop(props, "seq_start", text="Start")
                col.separator()
                col.prop(props, "seq_last", text="Last")

                col.separator()
                row = col.row(align=True)
                row.operator("renamer.apply_sequence", text="Apply ↓").direction = "DOWN"
                row.separator()
                row.operator("renamer.apply_sequence", text="Apply ↑").direction = "UP"

            # ─────────── Case Convertion
            row = layout.row(align=True)
            row.operator("renamer.case_conversion", text="UPPER").mode = "UPPER"
            row.separator()
            row.operator("renamer.case_conversion", text="lower").mode = "LOWER"
            row.separator()
            row.operator("renamer.case_conversion", text="Title").mode = "TITLE"

        # ─────────── Invert Selection
        inv_box = box.box()
        inv_box.operator("renamer.invert_selection", text="Invert Selection", icon="ARROW_LEFTRIGHT")

        layout.separator()
        # ─────────── Table
        if props.has_valid_items and len(props.items) > 0:
            header = layout.row()
            header.label(text="Current Name")
            header.label(text="New Name")
            for idx, item in enumerate(props.items):
                row = layout.row(align=True)
                row.prop(item, "selected", text="")
                row.label(text=item.current_name)
                row.prop(item, "new_name", text="")
                row.operator("renamer.mirror", text="", icon="ARROW_LEFTRIGHT").index = idx
                row.operator("renamer.delete_item", text="", icon="X").index = idx
        else:
            layout.label(text="No properties for this type")

        layout.separator()
        # ─────────── Bottom Buttons
        row = layout.row(align=True)
        row.operator("renamer.execute", text="Execute", icon="CHECKMARK")
        row.separator()
        row.operator("renamer.clear", text="Clear", icon="TRASH")
        col = layout.column(align=True)
        col.operator("renamer.delete_item", text="Delete Selected", icon="X").index = -1

        layout.separator()
        # ─────────── Support Section ───────────
        layout.separator()
        support_box = layout.box()
        support_box.label(text="❤️ Enjoying RENΔMER? Want to support us?")
        support_box.operator("wm.url_open", text="Donate on Gumroad", icon="HEART").url = GUMROAD_URL


# ─────────── Register/UnRegister ───────────
def register():
    bpy.utils.register_class(RENAMER_PT_Panel)

def unregister():
    bpy.utils.unregister_class(RENAMER_PT_Panel)