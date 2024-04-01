class NotFoundError(Exception):
    def __init__(self):
        self.message = "Item not found"
        super().__init__(self.message)
