import io 

class PITemp:
    def readTemp():
        file = open("/sys/class/thermal/thermal_zone0/temp", "r")
        temp = float(file.read())
        tempC = temp/1000
        file.close()
        return tempC