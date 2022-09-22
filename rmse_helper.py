from math import sqrt

class RmseHelper():
    def __init__(self):
        #construtor
        self.point_interval_dict = {}
    
    def registerLine(self, pointName:str, interval:int, delta:float, rinex:str):
        dict_key = self.dictKey(pointName, interval)

        if dict_key not in self.point_interval_dict:
            self.point_interval_dict[dict_key] = {
                "sqrSum": 0,
                "count": 0,
                "max": 0,
                "maxRinex": ''
            }
        
        self.point_interval_dict[dict_key]["count"] += 1
        self.point_interval_dict[dict_key]["sqrSum"] += delta*delta

        current_max = self.point_interval_dict[dict_key]["max"]
        if delta > current_max:
            self.point_interval_dict[dict_key]["max"] = delta
            self.point_interval_dict[dict_key]["maxRinex"] = rinex
    
    def getRmse(self, pointName:str, interval:int) -> float:
        dict_key = self.dictKey(pointName, interval)

        sqrSum = self.point_interval_dict[dict_key]["sqrSum"]
        count = self.point_interval_dict[dict_key]["count"]

        return sqrt(sqrSum/count)
    
    def getCount(self, pointName:str, interval:int) -> int:
        dict_key = self.dictKey(pointName, interval)

        count = self.point_interval_dict[dict_key]["count"]

        return count
    
    def getMaxError(self, pointName:str, interval:int) -> tuple[float, str]:
        dict_key = self.dictKey(pointName, interval)

        maxError = self.point_interval_dict[dict_key]["max"]
        rinex = self.point_interval_dict[dict_key]["maxRinex"]

        return (maxError, rinex)
    
    @staticmethod
    def dictKey(pointName:str, interval:int) -> str:
        return pointName + "@" + str(interval)