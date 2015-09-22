#====================== BEGIN GPL LICENSE BLOCK ======================
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
#  Inc., 51 Franklin Street, Fifth Floor, Boston, MA 02110-1301, USA.
#
#======================= END GPL LICENSE BLOCK ========================

# <pep8 compliant>

# ########################################
# Render Cube Map
#
# Dalai Felinto
#
# dalaifelinto.com
# Rio de Janeiro, September 2015
#
# ########################################

bl_info = {
    "name": "Cube Map",
    "author": "Dalai Felinto",
    "version": (1, 0),
    "blender": (2, 7, 5),
    "location": "Render Panel",
    "description": "",
    "warning": "",
    "wiki_url": "https://github.com/dfelinto/render_cube_map",
    "tracker_url": "",
    "category": "Render"}


import bpy
from bpy.app.handlers import persistent

TODO = True


# ############################################################
# Callbacks
# ############################################################

@persistent
def cube_map_render_init(context):
    print('cube_map_render_init')
    TODO


@persistent
def cube_map_render_pre(context):
    print('cube_map_render_pre')
    TODO


@persistent
def cube_map_render_post(context):
    print('cube_map_render_post')
    TODO


@persistent
def cube_map_render_cancel(context):
    print('cube_map_render_cancel')
    TODO


@persistent
def cube_map_render_complete(context):
    print('cube_map_render_complete')
    TODO


# ############################################################
# User Interface
# ############################################################

def RENDER_PT_cube_map(self, context):
    self.layout.prop(context.scene, "use_cube_map")


# ############################################################
# Un/Registration
# ############################################################

def register():
    bpy.types.Scene.use_cube_map = bpy.props.BoolProperty(
            name="Cube Map",
            default=False,
            )

    bpy.app.handlers.render_init.append(cube_map_render_init)
    bpy.app.handlers.render_pre.append(cube_map_render_pre)
    bpy.app.handlers.render_post.append(cube_map_render_post)
    bpy.app.handlers.render_cancel.append(cube_map_render_cancel)
    bpy.app.handlers.render_complete.append(cube_map_render_complete)

    bpy.types.RENDER_PT_render.append(RENDER_PT_cube_map)


def unregister():
    bpy.types.RENDER_PT_render.remove(RENDER_PT_cube_map)
    del bpy.types.Scene.user_cube_map

    bpy.app.handlers.render_init.remove(cube_map_render_init)
    bpy.app.handlers.render_pre.remove(cube_map_render_pre)
    bpy.app.handlers.render_post.remove(cube_map_render_post)
    bpy.app.handlers.render_cancel.remove(cube_map_render_cancel)
    bpy.app.handlers.render_complete.remove(cube_map_render_complete)


if __name__ == '__main__':
    register()
