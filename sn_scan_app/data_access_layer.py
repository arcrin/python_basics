from sqlalchemy import create_engine, Column, Integer, String, DateTime, ForeignKey
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import relationship, sessionmaker, joinedload
from datetime import datetime, timezone
from typing import Optional, Any, Dict
from domain_layer import IProductRepository, Product
import pyodbc

Base = declarative_base()

class ProductHierarchy(Base):
    __tablename__ = "mfgProductHierarchy"

    ProductID = Column(Integer, primary_key=True, autoincrement=True)
    PartNumber = Column(String(20), nullable=False)
    SerialNumber = Column(String(20), nullable=False)
    WorkOrder = Column(String(10), nullable=False)
    DateStamp = Column(DateTime, default=datetime.now(timezone.utc), nullable=False)
    Employee = Column(String(20), nullable=False)
    ParentProductID = Column(Integer, ForeignKey("mfgProductHierarchy.ProductID"), nullable=True)
    
    parent = relationship("ProductHierarchy", remote_side=[ProductID], backref="children")
    
    def __repr__(self):
        return (
            f"ProductHierarchy(ProductID={self.ProductID}, "
            f"PartNumber='{self.PartNumber}', SerialNumber='{self.SerialNumber}', "
            f"ParentProductID={self.ParentProductID}), "
            f"DateStamp={self.DateStamp}, "
            f"Employee={self.Employee}"
        )
        
    @property
    def product_id(self) -> int:
        return self.ProductID

    @property
    def part_number(self) -> str:
        return self.PartNumber

    @property
    def serial_number(self) -> str:
        return self.SerialNumber

    @property
    def work_order(self) -> str:
        return self.WorkOrder

    @property
    def date_stamp(self) -> datetime:
        return self.DateStamp

    @property
    def employee(self) -> str:
        return self.Employee

    @property
    def parent_product_id(self) -> int | None:
        return self.ParentProductID


class SqlProductRepository(IProductRepository):
    def __init__(self, connection_string: str):
        engine = create_engine(connection_string)
        Session = sessionmaker(engine)
        self.session = Session()
        
    def add_product(self, product: Product) -> int:
        new_product = ProductHierarchy(
            PartNumber=product.part_number,
            SerialNumber = product.serial_number,
            WorkOrder=product.work_order,
            DateStamp=product.date_stamp,
            Employee=product.employee,
            ParentProductID=product.parent_product_id 
        ) 
        
        self.session.add(new_product)
        self.session.commit()
        
        return new_product.product_id
        
    def query_product(self, serial_number: str) -> Product | None:
        product_entry = self.session.query(ProductHierarchy).filter_by(SerialNumber=serial_number).order_by(ProductHierarchy.DateStamp.desc()).first()
        if product_entry:
            return Product(product_entry.part_number, product_entry.serial_number, product_entry.work_order, product_entry.date_stamp, product_entry.employee, product_entry.parent_product_id) 
        else:
            return None
        

if __name__ == '__main__':
    server = 'localhost\\SQLEXPRESS'
    database = 'DCIERP'
    driver = 'ODBC Driver 17 for SQL Server'
    connection_string = f'DRIVER={{{driver}}};SERVER={server};DATABASE={database};Trusted_Connection=yes;'

    DATABASE_URL = "mssql+pyodbc://@localhost\\SQLEXPRESS/DCIERP?driver=ODBC+Driver+17+for+SQL+Server"

    engine = create_engine(DATABASE_URL)
    Session = sessionmaker(bind=engine)
    session = Session()

    # Base.metadata.create_all(engine)

    # Example usage
    # new_product = ProductHierarchy(
    #     PartNumber="PN001",
    #     SerialNumber="SN001",
    #     WorkOrder="WO001",
    #     Employee="wb",
    #     DateStamp=datetime.now(timezone.utc),
    #     ParentProductID=None
    # )
    # session.add(new_product)
    # session.commit()
    # print("Product added:", new_product)
    # product = session.query(ProductHierarchy).filter_by(SerialNumber="4014749999").order_by(ProductHierarchy.DateStamp.desc()).first()
    # if product:
    #     product_object = Product(product.part_number, product.serial_number, product.work_order, product.date_stamp, product.employee, product.parent_product_id)
    #     print("Queried Product: ", product_object.serial_number)
    # print(product)
    # print(product.children)

    
    # Query the parent product
    parent = (session.query(ProductHierarchy)
            .options(joinedload(ProductHierarchy.children))
            .filter_by(SerialNumber="1449929999")
            .order_by(ProductHierarchy.DateStamp.desc())
            .first())

    # Access children
    print(f"Parent SerialNumber: {parent.SerialNumber}")
    for child in parent.children:
        print(f"Child SerialNumber: {child.SerialNumber}, PartNumber: {child.PartNumber}")