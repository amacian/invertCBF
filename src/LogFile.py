class LogFile:
    def __init__(self, filename="logger", mode="r"):
        self.file = open(filename, mode)
    def write(self, data):
        self.file.write(data)
        return
    def close(self):
        self.file.close()
        return
    def flush(self):
        self.file.flush()
        return
