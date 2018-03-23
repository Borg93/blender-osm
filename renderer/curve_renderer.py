import bpy
from . import Renderer
from util.osm import assignTags


class CurveRenderer(Renderer):
    
    def __init__(self, app):
        super().__init__(app)
    
    def prepare(self):
        terrain = self.app.terrain
        if terrain:
            if not terrain.envelope:
                terrain.createEnvelope()

    def preRender(self, element):
        layer = element.l
        self.layer = layer
        
        if layer.singleObject:
            if not layer.obj:
                layer.obj = self.createBlenderObject(
                    layer.name,
                    layer.location,
                    self.parent
                )
            self.obj = layer.obj
        else:
            self.obj = self.createBlenderObject(
                self.getName(element),
                self.offsetZ or self.offset or layer.location,
                layer.getParent()
            )

    def renderLineString(self, element, data):
        self._renderLineString(element, element.getData(data), element.isClosed())

    def renderMultiLineString(self, element, data):
        for i,l in enumerate( element.getDataMulti(data) ):
            self._renderLineString(element, l, element.isClosed(i))
    
    def _renderLineString(self, element, coords, closed):
        spline = self.obj.data.splines.new('POLY')
        z = self.layer.meshZ
        for i,coord in enumerate(coords):
            if i:
                spline.points.add(1)
            spline.points[i].co = (coord[0], coord[1], z, 1.)
        if closed:
            spline.use_cyclic_u = True
    
    def postRender(self, element):
        layer = element.l
        
        if not layer.singleObject:
            obj = self.obj
            # assign OSM tags to the blender object
            assignTags(obj, element.tags)
            layer.finalizeBlenderObject(obj)

    @classmethod
    def createBlenderObject(self, name, location, parent):
        curve = bpy.data.curves.new(name, 'CURVE')
        curve.fill_mode = 'NONE'
        obj = bpy.data.objects.new(name, curve)
        if location:
            obj.location = location
        bpy.context.scene.objects.link(obj)
        if parent:
            # perform parenting
            obj.parent = parent
        return obj