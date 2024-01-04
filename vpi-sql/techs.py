class Techs(object):
    class Tech(object):
        def __init__(self, name, number):
            self.name = name
            self.number = number


class Buildings(object):
    class B(object):
        def __init__(self, name, cost, res, lim, buildtime):
            self.name = name
            self.cost = cost
            self.res = res
            self.lim = lim
            self.buildtime = buildtime

    _buildingslist = {
        B("Основные промзоны", 2.0, 0.0, 0.0, 3),
        B("ВПК", 3.0, 0.0, 0.0, 5),
        B("Гражданский сектор", 2.0, 0.0, 0.0, 2),
        B("Технопарк", 5.0, 0.0, 0.0, 10),
        B("Академия", 3.0, 0.0, 0.0, 3),
    }

    def buildingcheck(self, name):
        for type in self._buildingslist:
            if type.name == name:
                return True
        return False, type.buildtime
