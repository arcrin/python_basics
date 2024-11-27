from abc import ABC, abstractmethod 


class IMessageWriter(ABC):
    @abstractmethod
    def display(self, message: str) -> None:
        raise NotImplementedError


class ConsoleMessageWriter(IMessageWriter):
    def display(self, message: str) -> None:
        print(f"{message}")


class Salutation:
    def __init__(self, writer: IMessageWriter | None) -> None:
        if writer is None:
            raise TypeError("writer object can not be None")
        self._writer = writer
        
    def Exclaim(self) -> None:
        self._writer.display("Helle DI!")

def main():
    console_writer = ConsoleMessageWriter()
    salutation = Salutation(console_writer)
    salutation.Exclaim()

if __name__ == "__main__":
    main()