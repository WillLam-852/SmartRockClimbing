class RenamedPath:
    """
    Pair of (old_name, new_name) to be renamed

    Attributes
    ----------
    old_name : str
        old path name
    new_name : str
        new path name
    """

    def __init__(self, old_name: str, new_name: str):
        self.old_name = old_name
        self.new_name = new_name
