
import commands
import os
import os.path
 
def get_mounts_old():
    "Get de mountpoints of the system. Probably not the best way"
    mount = commands.getoutput('mount -v')
    lines = mount.split('\n')
    points = map(lambda line: line.split()[2], lines)
    return points
 
def get_mounts():
    "Get de mountpoints of the system. Probably not the best way"
    return [os.path.join("/media/",p) for p in os.listdir("/media/")]
