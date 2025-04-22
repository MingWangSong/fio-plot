import sys
from pathlib import Path

sys.path.append(str(Path(__file__).parent.parent))
import fio_plot

if __name__ == '__main__':
    fio_plot.main()