import constatnts


class Item(object):
    def __init__(self):
        self.id = None
        self.type = constatnts.TYPE_ITEM
        self.value = None
        self.health = None
        self.importance = None
