"""
Classes & Methods
"""

import jsonpickle
from shapely.geometry import Polygon
import json


class Document():
    """
    Document
    """

    def __init__(self, name=None):
        self._document = {
            'pages': [],
            'name': name
        }

    @property
    def name(self):
        """
        Name

        Returns:
            [str] -- [Name of the document]
        """
        return self._document['name']

    @property
    def num_pages(self):
        """
        Number of pages

        Returns:
            [int] -- [Number of pages]
        """
        return len(self._document['pages'])

    def add(self, page):
        """
        Add new page

        Arguments:
            page {[Page]} -- [Page instance]
        """
        self._document['pages'].append(page)

    def get(self):
        """
        Get all pages in a document

        Returns:
            [list] -- [Page instances]
        """
        return self._document['pages']

    def load(self, filepath=None, json_object=None):
        """
        Load document from file

        Arguments:
            path {[str]} -- [Path to file]
        """
        if filepath is not None:
            self._document = jsonpickle.decode(open(filepath, 'r').read())
        elif json_object is not None:
            self._document = jsonpickle.decode(json.dumps(json_object))

    def save(self, path):
        """
        Save document to file

        Arguments:
            path {[str]} -- [Path to file]
        """
        json_string = jsonpickle.encode(self._document)
        open(path, 'w').write(json_string)


class Page():
    """
    Page
    """

    def __init__(self, number, width, height):
        self._number = number
        self._width = width
        self._height = height

    @property
    def number(self):
        """
        Page number

        Returns:
            [int] -- [Page number]
        """
        return self._number

    @property
    def width(self):
        """
        Page width

        Returns:
            [float] -- [Page width]
        """
        return self._width

    @property
    def height(self):
        """
        Page height

        Returns:
            [float] -- [Page height]
        """
        return self._height

    def add(self, item):
        """
        Add item (abstract method)

        Raises:
            NotImplementedError
        """
        raise NotImplementedError()

    def get(self):
        """
        Get items (abstract method)

        Raises:
            NotImplementedError
        """
        raise NotImplementedError()


class WordsPage(Page):
    """
    WordsPage
    """

    def __init__(self, number, width, height):
        self._words = []
        super().__init__(number, width, height)

    def add(self, item):
        """
        Add new word

        Arguments:
            word {[Word]} -- [Word instance]
        """
        if isinstance(item, Word):
            self._words.append(item)
        else:
            raise TypeError()

    def get(self,min_word_height=None):
        """
        All words

        Returns:
            [list] -- [Word instances]
        """
        if min_word_height is not None:
            self._words = [w for w in self._words if w._x1-w._x0>= min_word_height]
        return self._words
    
    def filter(self,bbox,mode="exact",min_dist=5):
        """
        Filter to obtain words located in or near a bounding box. Bounding box is a dict with keys hmin,hmax,wmin,wmax
        
        Returns:
            [list] -- [Word instances]
        """
        p1 = Polygon([(bbox["hmin"],bbox["wmin"]),(bbox["hmin"],bbox["wmax"]),(bbox["hmax"],bbox["wmax"]),(bbox["hmax"],bbox["wmin"])])
        ret_words = []
        for w in self._words:
            # print((w._x0,w._y0),(w._x0,w._y1),(w._x1,w._y1),(w._x1,w._y0))
            p2 = Polygon([(w._y0,w._x0),(w._y0,w._x1),(w._y1,w._x1),(w._y1,w._x0)])
            if mode == "exact":
                if p1.contains(p2):
                    ret_words.append(w)
            elif mode == "intersects":
                if p1.intersects(p2):
                    ret_words.append(w)
            elif mode == "approximate":
                if p1.distance(p2)<min_dist:
                    ret_words.append(w)
        return ret_words


class Word():
    """
    Word

    Returns:
        [type] -- [description]
    """

    def __init__(self, x0, y0, x1, y1, text):
        self._x0 = x0
        self._y0 = y0
        self._x1 = x1
        self._y1 = y1
        self._text = text

    @property
    def coords(self):
        """
        Coordinates: x0, y0, x1, y1

        Returns:
            [list] -- [coordinates]
        """
        return [self._x0, self._y0, self._x1, self._y1]

    @property
    def text(self):
        """
        Text

        Returns:
            [str] -- [text]
        """
        return self._text

    def get(self):
        """
        Get word (coords + text)

        Returns:
            [list] -- [coords + text]
        """
        return self.coords + [self.text]


class LayoutPage(Page):
    """
    LayoutPage
    """

    def __init__(self, number, width, height):
        self._blocks = []
        super().__init__(number, width, height)

    def add(self, item):
        """
        Add block

        Arguments:
            item {[Block]} -- [Block instance]
        """
        if isinstance(item, Block):
            self._blocks.append(item)
        else:
            raise TypeError()

    def get(self):
        """
        Get blocks

        Returns:
            [list] -- [Block instances]
        """
        return self._blocks

class Block():
    """
    Block (Abstract Class)
    """

    def __init__(self, x0, y0, x1, y1):
        self._x0 = x0
        self._y0 = y0
        self._x1 = x1
        self._y1 = y1

    @property
    def coords(self):
        """
        Coordinates: x0, y0, x1, y1

        Returns:
            [list] -- [block coordinates]
        """
        return [self._x0, self._y0, self._x1, self._y1]

    def add(self, item):
        """
        Add item

        Raises:
            NotImplementedError
        """
        raise NotImplementedError()

    def get(self):
        """
        Get items

        Raises:
            NotImplementedError
        """
        raise NotImplementedError()

class Paragraph(Block):
    """
    Paragraph
    """

    def __init__(self, x0, y0, x1, y1):
        self._text = None
        self._words = []
        super().__init__(x0, y0, x1, y1)

    @property
    def text(self):
        """
        Paragraph text

        Returns:
            [str] -- [text]
        """
        return self._text

    def set_text(self, text):
        """
        Set paragraph text

        Arguments:
            text {[str]} -- [text]
        """
        self._text = text

    def add(self, item):
        """
        Add word

        Arguments:
            item {[Word]} -- [Word instance]
        """
        if isinstance(item, Word):
            self._words.append(item)
        else:
            raise TypeError()

    def get(self):
        """
        Get words

        Returns:
            [list] -- [Word instances]
        """
        return self._words


class Table(Block):
    """
    Table
    """

    def __init__(self, x0, y0, x1, y1):
        self._cells = []
        super().__init__(x0, y0, x1, y1)

    @property
    def num_rows(self):
        """
        Number of rows

        Returns:
            [int] -- [Number of rows]
        """
        return max([c.row for c in self._cells])

    @property
    def num_columns(self):
        """
        Number of columns

        Returns:
            [int] -- [Number of columns]
        """
        return max([c.column for c in self._cells])

    def add(self, item):
        """
        Add table cell

        Arguments:
            item {[TableCell]} -- [TableCell instance]
        """
        if isinstance(item, TableCell):
            self._cells.append(item)
        else:
            raise TypeError()

    def get(self):
        """
        Get cells

        Returns:
            [list] -- [TableCell instances]
        """
        return self._cells


class TableCell():
    """
    TableCell
    """

    def __init__(self, row_index, column_index, is_header):
        self._words = []
        self._row_index = row_index
        self._column_index = column_index
        self._is_header = is_header
        self._text = None

    @property
    def row(self):
        """
        Row index (starts at 1)

        Returns:
            [int] -- [Row index]
        """
        return self._row_index

    @property
    def column(self):
        """
        Column index (starts at 1)

        Returns:
            [int] -- [Column index]
        """
        return self._column_index

    @property
    def is_header(self):
        """
        Is this cell a table header?

        Returns:
            [bool] -- [Header or not]
        """
        return self._is_header

    @property
    def text(self):
        """
        Cell text

        Returns:
            [str] -- [text]
        """
        return self._text

    def set_text(self, text):
        """
        Set cell text

        Arguments:
            text {[str]} -- [text]
        """
        self._text = text

    def add(self, item):
        """
        Add word to cell

        Arguments:
            item {[Word]} -- [Word instance]
        """
        if isinstance(item, Word):
            self._words.append(item)
        else:
            raise TypeError()

    def get(self):
        """
        Get words

        Returns:
            [list] -- [Word instances]
        """
        return self._words

class BoxPage(Page):
    """
    BoxPage
    """

    def __init__(self, number, width, height):
        self._boxes = []
        super().__init__(number, width, height)

    def add(self, item):
        """
        Add box to page

        Arguments:
            item {[Box]} -- [Box instance]
        """

        if isinstance(item, Box):
            self._boxes.append(item)
        else:
            raise TypeError()

    def get(self):
        """
        Get boxes

        Returns:
            [list] -- [Box instances]
        """
        return self._boxes


class Box():
    """
    Box
    """

    def __init__(self, x0, y0, x1, y1):
        self._x0 = x0
        self._y0 = y0
        self._x1 = x1
        self._y1 = y1

    @property
    def coords(self):
        """
        Coordinates: x0, y0, x1, y1

        Returns:
            [list] -- [coordinates]
        """
        return [self._x0, self._y0, self._x1, self._y1]
