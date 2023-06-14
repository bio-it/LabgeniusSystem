###############################################################################
# Interface class
# must provide xfer_cmd(cmd), xfer_param(cmd)
###############################################################################
class Interface():
    def xfer_cmd(self, cmd):
        print(f'Interface.xfer_cmd({cmd})')
        return bytes(1)
    def xfer_param(self, no, value):
        print(f'Interface.xfer_param({no}, {value})')
        return bytes(4)
    def __str__(self):
        return 'Interface class'
# interface.py

