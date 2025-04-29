class Wine:
    def __init__(self, name):#, year, region, grape):
        self.name = name
        self.year = None
        #self.region = region
        self.grapes = None
        self.cost = None

    def __str__(self):
        outstr = f"Wine(name={self.name}"
        if self.year:
            outstr += f", year={self.year}"
        if self.grapes:
            outstr += f", grapes={self.grapes}"
        if self.cost:
            outstr += f", cost={self.cost}"
        outstr += ")"
        return outstr
