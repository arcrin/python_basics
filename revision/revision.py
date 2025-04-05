"""
Revision Transition Requirements:   
1. The same product number needs to support both format.
    a. not sure how to tell the profile which format to expect.
    b. do we need to tell profile which format to expect? We use revision in data, display and MCU based products.
2. A SAPRevision is always greater than Revision.
    a. SAPRevision and Revision need to be comparable. Create a BaseRevision class
3. Code backward compatibility
    a. Leave the current Revision class unchanged, just add the BaseRevision as a base class
"""
from abc import ABC, abstractmethod
from functools import total_ordering
import re


@total_ordering
class BaseRevision(ABC):
    @abstractmethod
    def key(self) -> int:
        """
        Return a key used for comparison.
        """
        pass

    def __eq__(self, other: object) -> bool:
        if isinstance(self, Revision):
            other = Revision(other)
        elif isinstance(self, SAPRevision):
            other = SAPRevision(other)
        else:
            raise NotImplementedError
        return self._cmp_value(other) == 0 

    def __lt__(self, other: object):
        if isinstance(self, Revision):
            other = Revision(other)
        elif isinstance(self, SAPRevision):
            other = SAPRevision(other)
        else:
            raise NotImplementedError
        return self._cmp_value(other) < 0

    def _cmp_value(self, other: "Revision | SAPRevision") -> int:  
        if isinstance(self, SAPRevision) and isinstance(other, Revision):
            return 1
        elif isinstance(self, Revision) and isinstance(other, SAPRevision):
            return -1
        else:   # both self and other are of the same type
            return (self.key() > other.key()) - (self.key() < other.key())


class SAPRevision(BaseRevision):
    _sap_revision_regex = re.compile(r'^\d{2}$')

    def __init__(self, value: object):
        if value is None:   # type: ignore
            raise ValueError("SAPRevision can not be NULL.")
        if isinstance(value, (str, int, bytes)):
            if str(value).strip() == "":
                raise ValueError("SAPRevision can not empty")
            elif isinstance(value, bytes):
                self._value = value.decode("utf-8")
            else:
                self._value = str(value)
                
            format_match = self._sap_revision_regex.match(self._value)

            if not format_match:
                raise ValueError( f"{self._value} is not valid SAP Revision format.") 
        
        else:
            TypeError(f"Can not convert {type(value)} to SAPRevision")
      
    def __repr__(self) -> str:
        return self._value 
    
    def __str__(self) -> str:
        return self._value

    def key(self) -> int:
       return int(self._value) 


class Revision(BaseRevision):
    # updated regex: minor group should be mandatory and should support 2-digits (was 1-digit before)
    _revision_regex = re.compile(r'(?P<major>\d{1,2})\.(?P<minor>\d{1,2})(?P<alpha>[a-z])?(?:\.(?P<FA>[A-Z]))?')
    
    def __init__(self, rev: object):
        if rev is None:   # type: ignore
            raise ValueError("Revision can not be Null")
        if isinstance(rev, bytes):
            self._rev = str(rev.decode("utf-8"))
        self._rev: str = str(rev)
        if self._rev.strip() == "":
            raise ValueError("Revision can not be empty") 
        
        format_match = self._revision_regex.match(str(self._rev))
        if not format_match:
            raise ValueError(f'"{self._rev}" is invalid revision format. Please use format 1.2[a][.B]')
        
        self.major: int = int(format_match.group("major"))
        self.minor: int = int(0 if not format_match.group("minor") else format_match.group("minor") )
        self.alpha: str = "" if not format_match.group("alpha") else format_match.group("alpha") 
        self.fa: str = "" if not format_match.group("FA") else format_match.group("FA") 
        
    @property
    def _text(self):
        text = str(self.major) + "." + str(self.minor) + self.alpha 
        text += "." if self.fa != "" else ""
        text += self.fa
        return text  

    @property
    def _value(self) -> int:
        value = self.major * 100000
        value = self.minor * 10000
        value += int(0 if self.alpha == "" else "{:02d}".format(ord(self.alpha) - ord('a') + 1)) * 100 
        value += int(0 if self.fa == "" else "{:02d}".format(ord(self.fa) - ord('A') + 1)) 
        return value
    
    def __str__(self) -> str:
        return self._text

    def __repr__(self) -> str:
        return self._text

    def key(self) -> int:
        return self._value


        
if __name__ == "__main__":
    # SAPRevision
    # print(SAPRevision("11"))        
    # print(SAPRevision(b"11"))
    # print(SAPRevision(11))
    # try:
    #     print(SAPRevision("1A"))
    # except ValueError as e:
    #     print(e) 
        
    # try:
    #     print(SAPRevision("AA"))
    # except ValueError as e:
    #     print(e)

    # try:
    #     print(SAPRevision("A1"))
    # except ValueError as e:
    #     print(e)
    
    # print(SAPRevision("11") > SAPRevision("09"))
    # print(SAPRevision("09") < SAPRevision("11"))

    # Revision
    # rev1 = Revision("1.2a.B")
    # rev2 = Revision("1.2a.A")

    # sap_rev1 = SAPRevision(11)
    # sap_rev2 = SAPRevision("00")
    
    rev = Revision("1.1")
    print("1.0" < rev)
