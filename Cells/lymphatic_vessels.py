from . import Macrophage
from . import Dendritic
from . import TCell
from . import BCell

def permissionMacro(file_path):
    Macrophage.isolate_virus(file_path)

def request_Tcell_resources():
    return TCell.request_resources()

def generate_antibodies():
    BCell.make_antibodies()
