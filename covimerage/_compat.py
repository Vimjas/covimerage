try:
    FileNotFoundError = FileNotFoundError
except NameError:
    FileNotFoundError = IOError
