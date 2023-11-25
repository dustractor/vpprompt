# ##### BEGIN GPL LICENSE BLOCK #####{{{1
#
#  This program is free software; you can redistribute it and/or
#  modify it under the terms of the GNU General Public License
#  as published by the Free Software Foundation; either version 2
#  of the License, or (at your option) any later version.
#
#  This program is distributed in the hope that it will be useful,
#  but WITHOUT ANY WARRANTY; without even the implied warranty of
#  MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#  GNU General Public License for more details.
#
#  You should have received a copy of the GNU General Public License
#  along with this program; if not, write to the Free Software Foundation,
#  Inc., 51 Franklin Street, Fifth Floor, Boston, MA 02110 - 1301, USA.
#
# ##### END GPL LICENSE BLOCK #####}}}1
bl_info = {
        "name":        "Viewport Prompt",
        "description": "For naming objects, data, and bones.",
        "author":      "Shams Kitz <dustractor@gmail.com>",
        "version":     (1,2),
        "blender":     (2,80,0),
        "tracker_url": "https://github.com/dustractor/vpprompt",
        "category":    "Object"
    }

import bpy,bgl,blf

def _(c=None,r=[]):
    if c:
        r.append(c)
        return c
    return r


def display_callback(self,context):
    blf.position(0,*self._position,0)
    # blf.size(0,self._fontsize,72)
    blf.size(0,self._fontsize)
    blf.color(0,*self._color)
    blf.draw(0,self._prompt(str(self.txt_buffer)))

@_
class VPPROMPT_OT_vpprompt(bpy.types.Operator):
    bl_idname = "vpprompt.viewport_prompt"
    bl_label = "Viewport Prompt"
    bl_options = {"INTERNAL"}

    txt_buffer: bpy.props.StringProperty(default="")

    @classmethod
    def poll(self,context):
        return context.active_object

    def invoke(self,context,event):
        if context.area.type == "VIEW_3D":
            self.txt_buffer = ""
            prefs = context.preferences.addons[__name__].preferences
            self._color = prefs.color
            self._fontsize = prefs.fontsize
            self._position = prefs.position
            self._prompt = prefs.prompt_format_string.format
            context.window_manager.modal_handler_add(self)
            self._handle = bpy.types.SpaceView3D.draw_handler_add(
                    display_callback, (self, context),"WINDOW", "POST_PIXEL")
            context.area.tag_redraw()
            return {"RUNNING_MODAL"}
        else:
            return {"CANCELLED"}

    def modal(self,context,event):
        exec_evt = {"LEFTMOUSE","RET","NUMPAD_ENTER"}
        quit_evt = {"RIGHTMOUSE","ESC"}
        if event.value == "PRESS":
            if event.type in quit_evt.union(exec_evt):
                bpy.types.SpaceView3D.draw_handler_remove(
                        self._handle,"WINDOW")
                context.area.tag_redraw()
                if event.type not in exec_evt:
                    return {"CANCELLED"}
                return self.execute(context)
            elif event.type in {"BACK_SPACE","DEL"}:
                L = len(self.txt_buffer)
                if L:
                    self.txt_buffer = self.txt_buffer[0:L-1]
            elif event.unicode:
                self.txt_buffer += event.unicode
            context.area.tag_redraw()
        return {"RUNNING_MODAL"}

    def execute(self,context):
        prefs = context.preferences.addons[__name__].preferences
        if len(self.txt_buffer):
            if prefs.quit_with_q and self.txt_buffer == "q":
                bpy.ops.wm.quit_blender()
            newname = self.txt_buffer
            if (    prefs.rename_bones and
                    context.active_object.type == "ARMATURE" and
                    context.active_object.mode == "EDIT"):
                bpy.ops.object.mode_set(mode="OBJECT")
                bones = filter(lambda b:b.select,
                        context.active_object.data.bones)
                for bone in bones:
                    bone.name = newname
                bpy.ops.object.mode_set(mode="EDIT")
            else:
                for ob in context.selected_objects:
                    ob.name = newname
                    if ob.data and prefs.rename_data:
                        ob.data.name = newname
            return {"FINISHED"}
        else:
            return {"CANCELLED"}


@_
class ViewportPromptPrefs(bpy.types.AddonPreferences):

    bl_idname = __name__

    rename_data: bpy.props.BoolProperty(default=True)
    rename_bones: bpy.props.BoolProperty(default=True)
    position: bpy.props.IntVectorProperty(
            size=2,min=0,max=1024,default=(64,64))
    fontsize: bpy.props.IntProperty( min=8,max=256,default=48)
    color: bpy.props.FloatVectorProperty(
            subtype="COLOR", size=4,min=0,max=1,default=(0.125,0.75,0.75,0.75))
    map_to: bpy.props.StringProperty(default="S+SEMI_COLON")
    prompt_format_string: bpy.props.StringProperty(default=":{}|")
    quit_with_q: bpy.props.BoolProperty(default=False)

    def draw(self,context):
        layout = self.layout
        split = layout.split(factor=0.5)
        col1,col2 = split.column(),split.column()
        col1.label(text="prompt parameters")
        box = col1.box()
        box.prop(self,"fontsize")
        box.prop(self,"color")
        box.separator()
        box.label(text="The x and y position of the prompt")
        box.label(text="relative to bottom left of viewport:")
        box.prop(self,"position")
        box.separator()
        box.label(text="Format of the prompt display:")
        box.prop(self,"prompt_format_string")
        box.label(text="This must contain the pattern {} somewhere.")
        box.label(text="Before the {} is what shows as prompt")
        box.label(text="After the {} is what shows as cursor")

        box = col2.box()
        box.label(text="hotkey mapping")
        box.prop(self,"map_to")
        box.separator()
        box.label(text="Accepts shorthand syntax")
        box.label(text="for defining what key to map to:")
        box.separator()
        box.label(text="Single-letters used to denote modifier:")
        box.label(text="A = alt")
        box.label(text="C = ctrl")
        box.label(text="O = oskey")
        box.label(text="S = shift")
        box.label(text="Separated by plus sign from key event type.")
        box.label(text="See api docs for bpy.types.KeyMapItem")
        box.label(text="for list of possible key event types.")
        box.separator()
        box.label(text="Examples:")
        box.label(text="BACK_SLASH -> would bind to the unmodified \\ key.")
        box.label(text="S+QUOTE -> would bind to shifted single quote (\").")
        box.label(text="CA+N -> would bind to control+alt+N.")
        box.label(text="*restart is needed to take effect.*")


        layout.separator()
        layout.prop(self,"quit_with_q")
        layout.label(text="Check this box if you")
        layout.label(text="would like to use :q to exit blender")


addon_keymaps = []

def get_mapx_t(mapx):
    if "+" in mapx:
        modx,ign,mapt = mapx.partition("+")
    else:
        modx = ""
        mapt = mapx
    A,C,O,S = map(lambda _:_ in modx.upper(),"ACOS")
    return mapt.strip(),{"alt":A,"ctrl":C,"oskey":O,"shift":S}

menu_draw = lambda s,c:s.layout.operator(VPPROMPT_OT_vpprompt.bl_idname)

def register():
    list(map(bpy.utils.register_class,_()))
    bpy.types.VIEW3D_MT_object.append(menu_draw)
    addon = bpy.context.preferences.addons.get(__name__,None)
    if addon:
        prefs = addon.preferences
        if prefs.map_to:
            maptype,mods = get_mapx_t(prefs.map_to)
            wm = bpy.context.window_manager
            addon_keyconfig = wm.keyconfigs.addon
            if addon_keyconfig:
                keymaps = addon_keyconfig.keymaps
                km = keymaps.get("3D View",None)
                if not km:
                    km = keymaps.new("3D View",space_type="VIEW_3D")
                kmi = km.keymap_items.new(
                        VPPROMPT_OT_vpprompt.bl_idname,
                        maptype,
                        "PRESS",**mods)
                addon_keymaps.append([km,kmi])

def unregister():
    for km,kmi in addon_keymaps:
        km.keymap_items.remove(kmi)
    addon_keymaps.clear()
    bpy.types.VIEW3D_MT_object.remove(menu_draw)
    list(map(bpy.utils.unregister_class,_()))

