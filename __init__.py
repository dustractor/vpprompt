# ##### BEGIN GPL LICENSE BLOCK #####
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
# ##### END GPL LICENSE BLOCK #####

bl_info = {
        "name":        "Viewport Prompt",
        "author":      "Shams Kitz <dustractor@gmail.com>",
        "version":     (1,0),
        "tracker_url": "https://github.com/dustractor/vpprompt",
        "category":    "object"
    }

import bpy
import blf
import bgl


def display_callback(self,context):
    blf.position(0,*self._position,0)
    blf.size(0,self._fontsize,72)
    bgl.glColor4f(*self._color)
    blf.draw(0,self._prompt(str(self.tbuf)))

fix_evts = {
    "ONE":"1","TWO":"2","THREE":"3",
    "FOUR":"4","FIVE":"5","SIX":"6",
    "SEVEN":"7","EIGHT":"8","NINE":"9","ZERO":"0",
    "MINUS":"-",
    "PERIOD":".",
    "SPACE":" "
    }

FIX_EVTS = {"MINUS":"_"}


class VPPROMPT_OT_viewport_prompt(bpy.types.Operator):
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
            self._handle = bpy.types.SpaceView3D.draw_handler_add(display_callback, (self, context),"WINDOW", "POST_PIXEL")
            context.area.tag_redraw()
            return {"RUNNING_MODAL"}
        else:
            return {"CANCELLED"}

    def modal(self,context,event):
        exec_evt = {"LEFTMOUSE","RET","NUMPAD_ENTER"}
        quit_evt = {"RIGHTMOUSE","ESC"}
        if event.value == "PRESS":
            print("event.type:",event.type)
            if event.type in quit_evt.union(exec_evt):
                bpy.types.SpaceView3D.draw_handler_remove(self._handle,"WINDOW")
                context.area.tag_redraw()
                if event.type not in exec_evt:
                    return {"CANCELLED"}
                return self.execute(context)
            elif event.type in {"BACK_SPACE","DEL"}:
                plen = len(self.tbuf)
                if plen:
                    self.tbuf = self.tbuf[0:plen-1]
            nchar = ""
            if len(event.type) == 1:
                if event.shift:
                    nchar = event.type
                else:
                    nchar = event.type.lower()
            elif event.shift and event.type in FIX_EVTS:
                    nchar = FIX_EVTS.get(event.type)
            elif event.type in fix_evts:
                    nchar = fix_evts.get(event.type)
            self.tbuf += nchar
            context.area.tag_redraw()
        return {"RUNNING_MODAL"}

    def execute(self,context):
        if len(self.tbuf):
            newname = self.tbuf
            for ob in context.selected_objects:
                ob.name = newname
                if ob.data:
                    ob.data.name = newname
            return {"FINISHED"}
        else:
            return {"CANCELLED"}

#cu_n = 124
cu_n = 9474
class ViewportPromptPrefs(bpy.types.AddonPreferences):

    bl_idname = __name__

    position = bpy.props.IntVectorProperty(
            size=2,min=0,max=1024,default=(64,64))

    fontsize = bpy.props.IntProperty( min=8,max=256,default=48)

    color = bpy.props.FloatVectorProperty(
            subtype="COLOR", size=4,min=0,max=1,default=(0.4,0.7,0.9,0.8))

    map_to = bpy.props.StringProperty(default="SEMI_COLON")
    map_w_shift = bpy.props.BoolProperty(default=True)
    map_w_alt = bpy.props.BoolProperty(default=False)
    map_w_ctrl = bpy.props.BoolProperty(default=False)
    map_w_oskey = bpy.props.BoolProperty(default=False)
    prompt_format_string = bpy.props.StringProperty(default="{}"+chr(cu_n))


    def draw(self,context):
        layout = self.layout
        layout.prop(self,"color")
        layout.prop(self,"position")
        layout.prop(self,"fontsize")
        layout.separator()
        layout.prop(self,"map_to")
        layout.prop(self,"map_w_ctrl")
        layout.prop(self,"map_w_alt")
        layout.prop(self,"map_w_shift")
        layout.prop(self,"map_w_oskey")
        layout.separator()
        layout.prop(self,"prompt_format_string")

addon_keymaps = []

def register():
    bpy.utils.register_module(__name__)
    wm = bpy.context.window_manager
    addon_keyconfig = wm.keyconfigs.addon
    prefs = bpy.context.user_preferences.addons[__name__].preferences
    map_to = prefs.map_to
    if addon_keyconfig:
        keymaps = addon_keyconfig.keymaps
        if "3D View" not in keymaps:
            km = keymaps.new("3D View",space_type="VIEW_3D")
            kmi = km.keymap_items.new(
                    VPPROMPT_OT_viewport_prompt.bl_idname, map_to, "PRESS",
                    shift=prefs.map_w_shift, alt=prefs.map_w_alt,
                    ctrl=prefs.map_w_ctrl, oskey=prefs.map_w_oskey)
            addon_keymaps.append([km,kmi])

def unregister():
    bpy.utils.unregister_module(__name__)
    for km,kmi in addon_keymaps:
        km.keymap_items.remove(kmi)

