# Render Cube Map
Addon to automatically render cube maps from Blender

How to Use
==========
* Install and enable the [Addon](render_cube_map.py)
* Turn the Cube Map option in the ``Cube Map`` tab in the ``Render`` panel.
* Render your frame or animation, as you would normally

![Cube Map Addon](http://dalaifelinto.com/images/cube_map.png)

Each face of the cube map is saved separately in your output folder.

Scene Setup
===========
If you need to save the cubemap setup within the .blend file you can use this option.
This is useful to send the file for renderfarms. Once your scene is setup you no longer
need the "Cube Map" option enabled nor this addon.

Advanced Mode
=============
If you need to (re-)render only some of the cube-map views you can turn
the ``Advanced`` option and select the views to render.

If ``Advanced`` is disabled all the views are rendered.

What is happening under the hood?
=================================
The addon automatize the following tasks:
* Create 6 linked scenes (``NORTH``, ``WEST``, ``EAST``, ``SOUTH``, ``ZENITH``, ``NADIR``)
* Create a nodetree with a ``Render Layer`` node per scene, all connected to a ``File Output`` node
* Create a unique camera for each new scene, with a field of view of 90 degrees, and facing a different direction
* Render your frame/animation
* Delete everything created by the Addon

Design Limitations
==================
Since this was originally designed to generated VR Cube Maps (with the [Spherical Stereo](http://www.dalaifelinto.com/?p=1009) Blender branch), the cube map is always upward.

In other words, the Z rotation of the camera is taken into consideration, but the ``NORTH``, ``WEST``, ``EAST``, ``SOUTH`` faces are all upward oriented.

Besides that, the composite nodes are not taken into consideration at the moment.
