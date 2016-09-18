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
bl_info = { #{{{1
        "name":        "Viewport Prompt",
        "description": "For naming objects, data, and bones.",
        "author":      "Shams Kitz <dustractor@gmail.com>",
        "version":     (1,1),
        "tracker_url": "https://github.com/dustractor/vpprompt",
        "category":    "Object"
    } #}}}1

import bpy,bgl,blf


def display_callback(self,context):
    blf.position(0,*self._position,0)
    blf.size(0,self._fontsize,72)
    bgl.glColor4f(*self._color)
    blf.draw(0,self._prompt(str(self.tbuf)))

class VPPROMPT_OT_vpprompt(bpy.types.Operator):
    bl_idname = "vpprompt.viewport_prompt"
    bl_label = "Viewport Prompt"
    bl_options = {"INTERNAL"}

    tbuf = bpy.props.StringProperty(default="")

    @classmethod
    def poll(self,context):
        return context.active_object

    def invoke(self,context,event):
        if context.area.type == "VIEW_3D":
            prefs = context.user_preferences.addons[__name__].preferences
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
                plen = len(self.tbuf)
                if plen:
                    self.tbuf = self.tbuf[0:plen-1]
            elif event.unicode:
                self.tbuf += event.unicode
            context.area.tag_redraw()
        return {"RUNNING_MODAL"}

    def execute(self,context):
        prefs = context.user_preferences.addons[__name__].preferences
        if len(self.tbuf):
            if prefs.quit_with_q and self.tbuf == "q":
                bpy.ops.wm.quit_blender()
            newname = self.tbuf
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


class ViewportPromptPrefs(bpy.types.AddonPreferences):

    bl_idname = __name__

    rename_data = bpy.props.BoolProperty(default=True)
    rename_bones = bpy.props.BoolProperty(default=True)
    position = bpy.props.IntVectorProperty(
            size=2,min=0,max=1024,default=(64,64))
    fontsize = bpy.props.IntProperty( min=8,max=256,default=48)
    color = bpy.props.FloatVectorProperty(
            subtype="COLOR", size=4,min=0,max=1,default=(0.125,0.75,0.75,0.75))
    map_to = bpy.props.StringProperty(default="S+SEMI_COLON")
    prompt_format_string = bpy.props.StringProperty(default=":{}|")
    quit_with_q = bpy.props.BoolProperty(default=False)

    def draw(self,context):
        layout = self.layout
        split = layout.split(percentage=0.5)
        col1,col2 = split.column(),split.column()
        col1.label("prompt parameters")
        box = col1.box()
        box.prop(self,"fontsize")
        box.prop(self,"color")
        box.separator()
        box.label("The x and y position of the prompt")
        box.label("relative to bottom left of viewport:")
        box.prop(self,"position")
        box.separator()
        box.label("Format of the prompt display:")
        box.prop(self,"prompt_format_string")
        box.label("This must contain the pattern {} somewhere.")
        box.label("Before the {} is what shows as prompt")
        box.label("After the {} is what shows as cursor")

        box = col2.box()
        box.label("hotkey mapping")
        box.prop(self,"map_to")
        box.separator()
        box.label("Accepts shorthand syntax")
        box.label("for defining what key to map to:")
        box.separator()
        box.label("Single-letters used to denote modifier:")
        box.label("A = alt")
        box.label("C = ctrl")
        box.label("O = oskey")
        box.label("S = shift")
        box.label("Separated by plus sign from key event type.")
        box.label("See api docs for bpy.types.KeyMapItem")
        box.label("for list of possible key event types.")
        box.separator()
        box.label("Examples:")
        box.label("BACK_SLASH -> would bind to the unmodified \\ key.")
        box.label("S+QUOTE -> would bind to shifted single quote (\").")
        box.label("CA+N -> would bind to control+alt+N.")
        box.label("*restart is needed to take effect.*")


        layout.separator()
        layout.prop(self,"quit_with_q")
        layout.label("Check this box if you are a user of vim")
        layout.label("and would like to use :q to exit blender")



addon_keymaps = []

def get_mapx_t(mapx):
    if "+" in mapx:
        modx,ign,mapt = mapx.partition("+")
    else:
        modx = ""
        mapt = mapx
    A,C,O,S = map(lambda _:_ in modx.upper(),"ACOS")
    return mapt.strip(),{"alt":A,"ctrl":C,"oskey":O,"shift":S}

def register():
    bpy.utils.register_module(__name__)
    prefs = bpy.context.user_preferences.addons[__name__].preferences
    if prefs.map_to:
        maptype,mods = get_mapx_t(prefs.map_to)
        wm = bpy.context.window_manager
        addon_keyconfig = wm.keyconfigs.addon
        if addon_keyconfig:
            keymaps = addon_keyconfig.keymaps
            if "3D View" not in keymaps:
                km = keymaps.new("3D View",space_type="VIEW_3D")
                kmi = km.keymap_items.new(
                        VPPROMPT_OT_vpprompt.bl_idname,
                        maptype,
                        "PRESS",**mods)
                addon_keymaps.append([km,kmi])

def unregister():
    bpy.utils.unregister_module(__name__)
    for km,kmi in addon_keymaps:
        km.keymap_items.remove(kmi)
    addon_keymaps.clear()

