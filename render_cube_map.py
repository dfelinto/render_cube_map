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

class View:
    def __init__(self, name):
        self._name = name
        self._scene = None
        self._node = None
        self._camera = None

    def setScene(self, scene):
        scene.name = self._name
        self._scene = scene

    def setNode(self, node, links, node_output):
        node.name = self._name
        node.label = self._name
        node.scene = self._scene
        self._node = node

        # connect to output
        _input = node_output.layer_slots.new(self._name)
        links.new(node.outputs[0], _input)

    @property
    def scene(self):
        return self._scene


@persistent
def cube_map_render_init(scene):
    print('cube_map_render_init')

    if not scene.cube_map.use_cube_map:
        return

    main_scene = scene
    hashes = [hash(scene) for scene in bpy.data.scenes]

    views = [
            View('NORTH'),
            View('SOUTH'),
            View('WEST'),
            View('EAST'),
            View('ZENITH'),
            View('NADIR'),
            ]

    # create cameras
    TODO

    for view in views:
        # create a scene per view
        bpy.ops.scene.new(type='LINK_OBJECTS')
        scene = [scene for scene in bpy.data.scenes if hash(scene) not in hashes][0]

        # mark the scene to remove it afterwards
        scene.cube_map.is_temporary = True

        hashes.append(hash(scene))
        view.setScene(scene)

    # create a scene from scratch
    cubemap_scene = bpy.data.scenes.new('Cube Map')
    cubemap_scene.cube_map.is_temporary = True

    # created the necessary nodetrees there
    cubemap_scene.use_nodes = True
    node_tree = cubemap_scene.node_tree

    # remove all nodes
    for node in node_tree.nodes:
        node_tree.nodes.remove(node)

    # output node
    node_output = node_tree.nodes.new('CompositorNodeOutputFile')
    node_output.inputs.clear()

    for view in views:
        node = node_tree.nodes.new('CompositorNodeRLayers')
        view.setNode(node, node_tree.links, node_output)


@persistent
def cube_map_render_cancel(scene):
    print('cube_map_render_cancel')
    cube_map_cleanup(scene)


@persistent
def cube_map_render_complete(scene):
    print('cube_map_render_complete')
    cube_map_cleanup(scene)


def cube_map_cleanup(scene):
    TODO


# ############################################################
# User Interface
# ############################################################

def RENDER_PT_cube_map(self, context):
    self.layout.prop(context.scene.cube_map, "use_cube_map")


# ############################################################
# Scene Properties
# ############################################################

class CubeMapInfo(bpy.types.PropertyGroup):
    use_cube_map = bpy.props.BoolProperty(
            name="Cube Map",
            default=False,
            )

    is_temporary = bpy.props.BoolProperty(
            name="Temporary",
            default=False,
            )


# ############################################################
# Un/Registration
# ############################################################

def register():
    bpy.utils.register_class(CubeMapInfo)

    bpy.types.Scene.cube_map = bpy.props.PointerProperty(
            name="cube_map",
            type=CubeMapInfo,
            options={'HIDDEN'},
            )

    bpy.app.handlers.render_init.append(cube_map_render_init)
    bpy.app.handlers.render_cancel.append(cube_map_render_cancel)
    bpy.app.handlers.render_complete.append(cube_map_render_complete)

    bpy.types.RENDER_PT_render.append(RENDER_PT_cube_map)


def unregister():
    bpy.types.RENDER_PT_render.remove(RENDER_PT_cube_map)

    del bpy.types.Scene.cube_map
    bpy.utils.unregister_class(CubeMapInfo)
    bpy.utils.unregister_class(HashInfo)

    bpy.app.handlers.render_init.remove(cube_map_render_init)
    bpy.app.handlers.render_cancel.remove(cube_map_render_cancel)
    bpy.app.handlers.render_complete.remove(cube_map_render_complete)


if __name__ == '__main__':
    register()
