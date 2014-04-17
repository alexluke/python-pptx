# encoding: utf-8

"""
Placeholder object.
"""

from pptx.spec import PH_TYPE_TBL
from pptx.oxml.graphfrm import CT_GraphicalObjectFrame
from pptx.oxml.ns import namespaces
from pptx.oxml.core import SubElement, child, Element
from pptx.shapes.table import Table
from pptx.spec import PH_ORIENT_HORZ, PH_SZ_FULL, PH_TYPE_OBJ, PH_TYPE_TBL


# default namespace map for use in lxml calls
_nsmap = namespaces('a', 'r', 'p')


class Placeholder(object):
    """
    Decorator (pattern) class for adding placeholder properties to a shape
    that contains a placeholder element, e.g. ``<p:ph>``.
    """
    def __new__(cls, shape):
        cls = type('PlaceholderDecorator', (Placeholder, shape.__class__), {})
        return object.__new__(cls)

    def __init__(self, shape):
        self._decorated = shape
        xpath = './*[1]/p:nvPr/p:ph'
        self._ph = self._element.xpath(xpath, namespaces=_nsmap)[0]

    def __getattr__(self, name):
        """
        Called when *name* is not found in ``self`` or in class tree. In this
        case, delegate attribute lookup to decorated (it's probably in its
        instance namespace).
        """
        return getattr(self._decorated, name)

    @property
    def is_table_shape(self):
        """
        True if this shape is a placeholder of type "table".
        """
        return self.type == PH_TYPE_TBL

    @property
    def type(self):
        """Placeholder type, e.g. PH_TYPE_CTRTITLE"""
        return self._ph.get('type', PH_TYPE_OBJ)

    @property
    def orient(self):
        """Placeholder 'orient' attribute, e.g. PH_ORIENT_HORZ"""
        return self._ph.get('orient', PH_ORIENT_HORZ)

    @property
    def sz(self):
        """Placeholder 'sz' attribute, e.g. PH_SZ_FULL"""
        return self._ph.get('sz', PH_SZ_FULL)

    @property
    def idx(self):
        """Placeholder 'idx' attribute, e.g. '0'"""
        return int(self._ph.get('idx', 0))

    @property
    def _layout_placeholder(self):
        """
        The slide layout placeholder that this placeholder shape inherits from
        """
        slide = self._decorated.part
        slide_layout = slide.slidelayout
        for ph in slide_layout.shapes.placeholders:
            if ph.idx == self.idx:
                return ph
        raise KeyError['No matching placeholder shape found in slide_layout']

    def insert_table(self, rows, cols, left=None, top=None, width=None, height=None):
        """
        Replace an existing Table placeholder shape with an actual table. See also add_table in the ShapeCollection.
        """
        if not self.is_table_shape:
            raise TypeError("cannot insert table in a non-table shape/placeholder")

        layout_ph = self._layout_placeholder
        # Use placeholder size and location if not supplied.
        if left == None:
            left = layout_ph.left
        if top == None:
            top = layout_ph.top
        if width == None:
            width = layout_ph.width
        if height == None:
            height = layout_ph.height

        shape_idx = self.id - 1
        name = 'Table %d' % (shape_idx)
        graphicFrame = CT_GraphicalObjectFrame.new_table(
            shape_idx, name, rows, cols, left, top, width, height)

        underlying_shape = self._decorated
        shapetree = underlying_shape._parent
        # See: http://lxml.de/api/lxml.etree._Element-class.html
        shapetree._spTree.replace(self._element, graphicFrame)
        ## Make sure we set the related placeholder element in the new GraphicFrame
        ## This could probably be done more sanely by passing an idx or ph
        ## to the new_table call.
        nvPr = graphicFrame.nvGraphicFramePr.nvPr
        ph = Element('p:ph')
        nvPr.insert(0, ph)
        ph.set('type', 'tbl')
        ph.set('idx', str(self.idx))

        table = Table(graphicFrame, self._parent)
        this_shape_index = shapetree.index(underlying_shape)
        shapetree._shapes[this_shape_index] = table
        return table
