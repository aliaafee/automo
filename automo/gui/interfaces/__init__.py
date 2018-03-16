"""GUI Interfaces"""
from .shellinterface import ShellInterface
from .wardinterface import WardInterface
from .circumward import CircumWard
from .dischargeinterface import DischargeInterface

INTERFACES = {
    'gui-shell' : ('Python Shell', ShellInterface),
    'gui-ward' : ('Ward', WardInterface),
    'gui-cward' : ('Circum Ward', CircumWard),
    'gui-discharge' : ('Discharges', DischargeInterface)
}

def get_by_name(name):
    """Return interface class from name"""
    try:
        label, interface_class = INTERFACES[name]
        return interface_class
    except KeyError:
        return None
