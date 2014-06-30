# -*- coding: utf-8 -*-
# Copyright (c) 2014, Vispy Development Team.
# Distributed under the (new) BSD License. See LICENSE.txt for more info.

from __future__ import division

from ..gloo import gl
from .. import app
from .subscene import SubScene
from .transforms import STTransform
from .events import SceneDrawEvent, SceneMouseEvent
from ..util import logger


class SceneCanvas(app.Canvas):
    """ SceneCanvas provides a Canvas that automatically draws the contents
    of a scene.

    """

    def __init__(self, *args, **kwargs):

        app.Canvas.__init__(self, *args, **kwargs)
        self.events.mouse_press.connect(self._process_mouse_event)
        self.events.mouse_move.connect(self._process_mouse_event)
        self.events.mouse_release.connect(self._process_mouse_event)

        self._scene = None
        self.scene = SubScene()

    @property
    def scene(self):
        """ The SubScene object that represents the root entity of the
        scene graph to be displayed.
        """
        return self._scene

    @scene.setter
    def scene(self, e):
        if self._scene is not None:
            self._scene.events.update.disconnect(self._scene_update)
        self._scene = e
        self._scene.events.update.connect(self._scene_update)
        #self._update_document()

    def _scene_update(self, event):
        self.update()

#     def _update_document(self):
#         # 1. Set scaling on document such that its local coordinate system
#         #    represents pixels in the canvas.
#         self.scene.transform.scale = (2. / self.size[0], 2. / self.size[1])
#         self.scene.transform.translate = (-1, -1)
#
#         # 2. Set size of document to match the area of the canvas
#         self.scene.size = (1.0, 1.0)  # root viewbox is in NDC
# AK: no need to set size, we set the size explicitly when drawing.
# actually, we can have a root viewbox that has children, we should not
# touch its transform at all.

    def on_resize(self, event):
        pass
        #self._update_document()
        # Right now viewbox resolution is only available
        # via the event object, which may be sufficient!

    def on_draw(self, event):
        gl.glClearColor(0, 0, 0, 1)
        gl.glClear(gl.GL_COLOR_BUFFER_BIT | gl.GL_DEPTH_BUFFER_BIT)

        if self._scene is None:
            return  # Can happen on initialization
        logger.debug('Canvas draw')
        # Create draw event, which keeps track of the path of transforms
        self._process_entity_count = 0  # for debugging
        scene_event = SceneDrawEvent(canvas=self, event=event)
        self._scene.draw(scene_event)

    def _process_mouse_event(self, event):
        scene_event = SceneMouseEvent(canvas=self, event=event)
        self._scene._process_mouse_event(scene_event)
        
        # If something in the scene handled the scene_event, then we mark
        # the original event accordingly.
        event.handled = scene_event.handled

    def nd_transform(self):
        """
        Return the transform that maps from ND coordinates to pixel coordinates
        on the Canvas.
        """
        s = (self.size[0]/2., -self.size[1]/2.)
        t = (self.size[0]/2., self.size[1]/2.)
        return STTransform(scale=s, translate=t)
