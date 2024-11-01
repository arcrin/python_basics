# type: ignore
def decorator_function(original_function):
    def wrapper_function():
        # Add functionality before calling the original function
        print("Before the function call")

        original_function()

        # Add functionality after calling the original function

        print("After the function call")

    return wrapper_function
    

@decorator_function
def foo():
    print("The Fool")


foo()
