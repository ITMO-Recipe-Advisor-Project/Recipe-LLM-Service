class InvalidLanguageException(Exception):
    """Exception for non-English queries."""

    def __init__(self, message="The query is not in English."):
        self.message = message
        super().__init__(self.message)
