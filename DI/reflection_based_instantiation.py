# type: ignore
# Reflection-based object creation example in Python

# Define some classes to be dynamically instantiated 
class ConsoleMessageWriter:
    def write_message(self):
        print("Hello from ConsoleMessageWriter!")


class FileMessageWriter:
    def __init__(self, file_path):
        self.file_path = file_path

    def write_message(self):
        with open(self.file_path, 'w') as f:
            f.write("Hello from FileMessageWriter!\n")
        print(f"Message written to {self.file_path}")
        

# A factory function that creates an instance of a class using reflection
def create_instance(class_name, *args, **kwargs):
    # Get the class reference from the globals dictionary
    clazz = globals().get(class_name)
    if not clazz:
        raise ValueError(f"Class {class_name} not found.") 

    # Create an instance of the class with the provided arguments
    instance = clazz(*args, **kwargs)
    return instance

# Example usage of reflection-based object creation
if __name__ == "__main__":
    # Create an instance of ConsoleMessageWriter dynamically
    console_writer = create_instance("ConsoleMessageWriter")  
    console_writer.write_message()

    # Create an instance of FileMessageWriter  dynamically with a file path argument
    file_writer = create_instance("FileMessageWriter", "output.txt")
    file_writer.write_message()