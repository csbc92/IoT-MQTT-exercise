import math

# Returns the system uptime in seconds
def get_uptime_seconds():
    with open('/proc/uptime', 'r') as f:
        uptime_seconds = float(f.readline().split()[0])
    return uptime_seconds

# Returns the system uptime as a tuple (days, hours, minutes, seconds) given seconds
def get_uptime(seconds=get_uptime_seconds()):
    days = seconds / (60*60*24)
    hours = (days - math.floor(days)) * 24
    minutes = (hours - math.floor(hours)) * 60
    seconds = (minutes - math.floor(minutes)) * 60
    return (math.floor(days), math.floor(hours), math.floor(minutes), math.floor(seconds))


def celsius_to_fahrenheit(c):
    return c * 1.8 + 32
