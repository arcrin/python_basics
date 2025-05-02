from __future__ import annotations
from abc import ABC, abstractmethod
from functools import total_ordering
from time import sleep
import re


@total_ordering
class BaseRevision(ABC):
    @abstractmethod
    def _key(self) -> int:
        """
        Return a key used for comparison
        :return:
        """
        raise NotImplementedError

    @staticmethod
    def from_value(rev_value: str | int | float | bytes | Revision | SAPRevision) -> Revision | SAPRevision:
        if not isinstance(rev_value, (str, int, float, bytes, Revision, SAPRevision)):
            raise TypeError(f"Does not support converting {type(rev_value)} to BaseRevision")
        try:
            return SAPRevision(rev_value)
        except (ValueError, TypeError):
            return Revision(rev_value)

    def __eq__(self, other: object) -> bool:
        if isinstance(other, (Revision, SAPRevision)):
            return self._cmp_value(other) == 0
        else:
            raise TypeError(f"Can not compare {type(self)} with {type(other)}")

    def __lt__(self, other: object) -> bool:
        if isinstance(other, (Revision, SAPRevision)):
            return self._cmp_value(other) < 0
        else:
            raise TypeError(f"Can not compare {type(self)} with {type(other)}")

    def _cmp_value(self, other: Revision | SAPRevision) -> int:
        if isinstance(self, SAPRevision) and isinstance(other, Revision):
            return 1
        elif isinstance(self, Revision) and isinstance(other, SAPRevision):
            return -1
        else:
            return (self._key() > other._key()) - (self._key() < other._key())


class Revision(BaseRevision):
    # updated regex: minor group should be mandatory and should support 2-digits (was 1-digit before)
    _reRev = re.compile(r'^(?P<major>\d{1,2})\.(?P<minor>\d{1,2})(?P<alpha>[a-z])?(?:\.(?P<FA>[A-Z]))?$')

    def __init__(self, rev: str | float | bytes | Revision | None=None):

        if isinstance(rev, bytes):
            rev = str(rev.decode("utf-8"))

        if rev is None or not str(rev).strip():
            raise ValueError("DCI Revision does not support NULL or empty string")

        m = self._reRev.match(str(rev))
        if not m:
            raise ValueError('Invalid revision number. Please use format 1.2[a][.B]')
        self.MAJOR = int(m.group('major'))
        self.MINOR = 0 if not m.group('minor') else int(m.group('minor'))
        self.ALPHA = None if not m.group('alpha') else m.group('alpha')
        self.FA = None if not m.group('FA') else m.group('FA')

        if self.FA and not self.ALPHA:
            raise ValueError("FA field can only appear if alpha group is present")

    @property
    def _text(self) -> str:
        rslt = str(self.MAJOR) + '.'
        rslt += str(self.MINOR)
        rslt += '' if (self.ALPHA is None) else self.ALPHA # Only append if needed
        rslt += '' if (self.FA is None) else '.' + self.FA # Only append if needed
        return rslt

    @property
    def _value(self) -> int:
        alpha_val = 0 if not self.ALPHA else (ord(self.ALPHA) - ord('a') + 1) * 100
        fa_val = 0 if not self.FA else (ord(self.FA) - ord('A') + 1)
        value = (
            self.MAJOR * 100000 +
            self.MINOR * 10000 +
            alpha_val +
            fa_val
        )
        return value

    def __repr__(self) -> str:
        return self._text

    def __str__(self) -> str:
        return self._text

    def _key(self) -> int:
        return self._value

class SAPRevision(BaseRevision):
    _sap_revision_regex = re.compile(r'^\d{2}$')

    def __init__(self, rev: str | int | bytes | SAPRevision | None=None):
        self._value: str = ""
        if rev is None:
            raise ValueError("SAPRevision can not be NULL.")
        if isinstance(rev, bytes):
            rev = rev.decode()
        if isinstance(rev, (str, int, SAPRevision)):
            if str(rev).strip() == "":
                raise ValueError("SAPRevision can not empty")
            else:
                self._value = str(rev)

            format_match = self._sap_revision_regex.match(self._value)

            if not format_match:
                raise ValueError( f"{self._value} is not valid SAP Revision format.")

        else:
            raise TypeError(f"Can not convert {type(rev)} to SAPRevision")

    def __repr__(self) -> str:
        return self._value

    def __str__(self) -> str:
        return self._value

    def _key(self) -> int:
        return int(self._value)

