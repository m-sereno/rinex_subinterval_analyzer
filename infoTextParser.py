from datetime import datetime, timedelta


class InfoTextParser():
    def __init__(self, lines:list[str]):
        #construtor
        self.lines = lines
    
    def notProcessed(self) -> bool:
        lineToCheck = self.lines[2]
        return lineToCheck == "Arquivo não processado!\n"
    
    def isTopcon(self) -> bool:
        antennaLine = self.lines[6]
        return antennaLine == "ANTENA NÃO DISPONÍVEL\n"
    
    def rinex(self) -> str:
        return self.lines[1].split(' ')[-1].replace("\n", "")
    
    def utmn(self) -> str:
        return self.lines[19].split(' ')[-2]
    
    def utme(self) -> str:
        return self.lines[20].split(' ')[-2]
    
    def hnor(self) -> str:
        return self.lines[25].split(' ')[-2]
    
    def startTime(self) -> datetime:
        startTimeLine = self.lines[3]
        startTime_date_str = startTimeLine.split(' ')[-2]
        startTime_time_str = startTimeLine.split(' ')[-1]

        date_time_str = ' '.join([startTime_date_str, startTime_time_str])
        date_time_obj = self.str_to_datetime_obj(date_time_str)

        return date_time_obj
    
    def endTime(self) -> datetime:
        endTimeLine = self.lines[4]
        endTime_date_str = endTimeLine.split(' ')[-2]
        endTime_time_str = endTimeLine.split(' ')[-1]

        date_time_str = ' '.join([endTime_date_str, endTime_time_str])
        date_time_obj = self.str_to_datetime_obj(date_time_str)

        return date_time_obj
    
    def trackingDuration(self) -> timedelta:
        startTime = self.startTime()
        endTime = self.endTime()

        duration = endTime - startTime
        return duration
    
    @staticmethod
    def str_to_datetime_obj(datetime_str:str) -> datetime:
        return datetime.strptime(datetime_str.replace('\n', ''), '%Y/%m/%d %H:%M:%S,%f')
