# vpprompt


###Purpose of this addon

Simplest and most ideal method for renaming selected objects:

* begin by pressing a hotkey  
* type the name you wish to give  
* finish by pressing enter (or cancel by pressing escape).

One should not have to click with a mouse or worry whether a such-and-such panel is open to even have a place to click.

Wouldn't it be also nice if the name of the outer and inner did match ( object and data)?  I thought so too.

---

##Preferences

In the User Preferences for this addon,  You may change the color, fontsize, and position of the Viewport Prompt display, as well as which key to bind it to.

The key which the operator is bound to can be is customisable by entering the name of a keypress event type in the ``map_to`` property.

See here for a list of other acceptable values: [bpy.types.KeyMapItem](https://www.blender.org/api/blender_python_api_2_78_0/bpy.types.KeyMapItem.html#bpy.types.KeyMapItem.type)



#Misc Info

vpprompt was originally an addon 'shiftsemi' bound to a different key but that key became ( at present b. is v2.78 ) unmappable due to an event refactor and since the name of the addon was the same as the keybind, it seemed sensible to remake as a new addon 'vpprompt'.  I hope to eventually be able to map to the shift+semi-colon ``:`` so the prompt is like vi, but for now, this addon binds it's operator to ``;`` by default, although ``BACK_SLASH`` seemed like another good candidate for a default value of ``map_to``.