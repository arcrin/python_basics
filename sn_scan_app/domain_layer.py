from datetime import datetime, timezone
from abc import ABC, abstractmethod 
from interface.gpLookup import querySN  # type: ignore
from typing import List, Any, Dict
from dataclasses import dataclass
import os


class Product:
    def __init__(self, part_number: str, serial_number: str, work_order: str, date_stamp: datetime, employee: str, parent_product_id: int | None = None):
        self.part_number =  part_number
        self.serial_number = serial_number  
        self.work_order = work_order
        self.date_stamp = date_stamp
        self.employee = employee
        self.parent_product_id = parent_product_id        
        

@dataclass
class ProductDisplayInfo:
    description: str
    part_number: str
    revision: str
    serial_number: str


class IProductRepository(ABC):
    @abstractmethod
    def query_product(self, serial_number: str) -> Product | None:
        """Retrieve a product by its serial number."""
        pass
    
    @abstractmethod
    def add_product(self, product: Product) -> int:
        """Save a product to the database"""
        pass

    # @abstractmethod
    # def get_children(self, parent_id: int):
    #     """Retrieve all child products of a give parent product ID."""
    #     pass 
    

class IProductService(ABC):
    @abstractmethod
    def add_product(self, serial_number: str, parent_product_id: int | None, work_order: str) -> int:
        """
        Add product entry. Allow duplicate serial number. User will only provide the serial number of the product.
        It is this method's responsibility to look up the rest of the information.
        :param: serial number  
        :return: an unique ID for the product entry 
        """

    @abstractmethod
    def query_product_info(self, serial_number: str) -> ProductDisplayInfo | None:
        """
        Query product info based on given serial number. Return a product object information such as description, part number. 
        :param: serial_number
        :return: product object
        """

    @abstractmethod
    def validate_serial_number(self, serial_number: str) -> bool: 
        """
        Validates the given serial number
        :param serial_number: The serial number to validate.
        :return: A list of validation errors, or an empty list if valid
        """
        pass


    # @abstractmethod
    # def get_children(self, parent_serial: str) -> List[Product]:
    #     """
    #     Retrieves all children of a parent product by serial number
    #     :param parent_serial
    #     :return: A list of child products.
    #     """
    #     pass
    
    # @abstractmethod
    # def find_number_of_children(self, parent_serial: str) -> int:
    #     """
    #     Return the number of children associated with the parent_serial 
    #     """
    #     pass

    @abstractmethod
    def query_product_config(self, work_order: str) -> List[str]:
        """
        Return all assemblies associated with the config mo 
        """
        pass
    

class ProductService(IProductService):
    def __init__(self, repository: IProductRepository) -> None:
        self.repository = repository       
        
    def add_product(self, serial_number: str, parent_product_id: int | None, work_order: str) -> int:
        part_number = querySN(serial_number)['ProductNumber']   # type: ignore
        user = os.getlogin()
        new_product = Product(part_number, serial_number, work_order, datetime.now(timezone.utc), user, parent_product_id) # type: ignore
        return self.repository.add_product(new_product)
        
    def query_product_config(self, work_order: str) -> List[str]:
        return [item['Description'] for item in list(querySN(work_order)['SubAssemblies'].values())]    # type: ignore
    
    def validate_serial_number(self, serial_number: str) -> bool:
        if querySN(serial_number):
            return True
        else:
            return False
    
    def query_product_info(self, serial_number: str) -> ProductDisplayInfo | None:
        product_info = querySN(serial_number)
        if product_info:
            return ProductDisplayInfo(description=str(product_info["Description"]),
                                      part_number=str(product_info['ProductNumber']),
                                      revision=str(product_info["Revision"]),
                                      serial_number=str(int(product_info['SerialNumber'])))   
        else: 
            return None