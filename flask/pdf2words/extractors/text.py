import os
import numpy as np
from collections import defaultdict
from ..document import Document

__all__ = [
    'TextExtractor'
]


class TextExtractor():
    """
    TextExtractor
    """

    def __init__(self, document_or_path, merge_similar_y=True, merge_threshold_y=5.0):
        if isinstance(document_or_path, str):
            self._document = Document()
            self._document.load(document_or_path)
        elif isinstance(document_or_path, Document):
            self._document = document_or_path
        self._merge_similar_y = merge_similar_y
        self._merge_threshold_y = merge_threshold_y

    def _get_text(self,min_word_height=None):
        document_text = {}
        for page in self._document.get():
            text = self._make_text(page,min_word_height=min_word_height)
            document_text[page.number] = text
        return document_text

    def run(self):
        """
        Get document text
        """
        return self._get_text()

    def get_lines_with_words(self,min_word_height=None):
        """
        Get lines with individual words
        """
        document_text = {}
        for page in self._document.get():
            lines = self._make_text(page, with_words=True, min_word_height=min_word_height)
            document_text[page.number] = lines
        return document_text

    def _merge_lines(self, unique_y):
        threshold = self._merge_threshold_y
        y_keys = unique_y.keys()
        y_keys = sorted(y_keys, key=lambda x: x[0])

        merged_y = defaultdict(list)
        for key in y_keys:
            merged_keys = list(merged_y.keys())
            if not merged_keys:
                merged_y[key].extend(unique_y[key])
                continue
            y_0 = key[0]
            y_1 = key[1]
            diffs = [[np.abs(y_0 - ry[0]), np.abs(y_1 - ry[1])]
                     for ry in merged_keys]
            below_thresholds = [(d[0] <= threshold) and (
                d[1] <= threshold) for d in diffs]
            indices = list(np.where(below_thresholds)[0])
            if indices:
                m_key = merged_keys[indices[0]]
                merged_y[m_key].extend(unique_y[key])
            else:
                merged_y[key].extend(unique_y[key])
        return merged_y

    def _make_text(self, page, with_words=False, min_word_height=None):
        words = page.get()
        words = [w.get() for w in words]
        if min_word_height is not None:
            words = [w for w in words if w[2]-w[0]>= min_word_height]
        words = [[np.floor(w[0]), np.floor(w[1]), np.floor(
            w[2]), np.floor(w[3]), w[-1]] for w in words]
        unique_y = defaultdict(list)
        for word in words:
            unique_y[(word[1], word[3])].append(word)
        if self._merge_similar_y:
            unique_y = self._merge_lines(unique_y)
        y_keys = unique_y.keys()
        y_keys = sorted(y_keys, key=lambda x: x[0])
        lines = []
        for key in y_keys:
            words = unique_y[key]
            words = sorted(words, key=lambda x: x[0])
            if with_words:
                new_words = [[w[0], key[0], w[2], key[1], w[-1]] for w in words]
                lines.append(new_words)
            else:
                lines.append(' '.join([w[-1] for w in words]))
        if with_words:
            return lines
        return '\n'.join(lines)
