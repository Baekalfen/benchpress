import matplotlib
matplotlib.use('Agg')       # Essential for generating graphs "headless".

from pylab import *
import os
import re

colors  = [
    "#B3E2CD", "#FDCDAC", "#CBD5E8",
    "#F4CAE4", "#E6F5C9", "#FFF2AE",
    "#F1E2CC", "#CCCCCC",
    "#B3E2CD", "#FDCDAC", "#CBD5E8",
    "#F4CAE4", "#E6F5C9", "#FFF2AE",
    "#F1E2CC", "#CCCCCC",
    "#B3E2CD", "#FDCDAC", "#CBD5E8",
    "#F4CAE4", "#E6F5C9", "#FFF2AE",
    "#F1E2CC", "#CCCCCC",
]

colors = [
    "#e41a1c", "#377eb8", "#4daf4a", "#984ea3", "#ff7f00", "#ffff33",
    "#e41a1c", "#377eb8", "#4daf4a", "#984ea3", "#ff7f00", "#ffff33",
    "#e41a1c", "#377eb8", "#4daf4a", "#984ea3", "#ff7f00", "#ffff33"
]

hatches = [
    "\\", "+", "o", "/", "-", "O",
    "\\", "+", "o", "/", "-", "O",
    "\\", "+", "o", "/", "-", "O",
    "\\", "+", "o", "/", "-", "O",
    "\\", "+", "o", "/", "-", "O",
]

class Graph(object):
    """
    Baseclass for rendering Matplotlib graphs.
    Does alot of the annoying work, just override the render(...) method,
    and you are good to go!
    """

    def __init__(
        self,
        output="/tmp",
        file_formats=["pdf"],
        file_postfix='runtime',
        graph_title="Unknown Graph",
        xaxis_label="Problemsize",
        yaxis_label="Time in Seconds"
    ):
        self.graph_title    = graph_title
        self.xaxis_label    = xaxis_label
        self.yaxis_label    = yaxis_label
        self.output         = output
        self.file_formats   = file_formats
        self.file_postfix   = file_postfix

    def prep(self):
        clf()                       # Essential! Othervise the plots will be f**d up!
        figure(1)

        gca().yaxis.grid(True)      # Makes it easier to compare bars
        gca().xaxis.grid(False)
        gca().set_axisbelow(True)

        title(self.graph_title)     # Title and axis labels
        ylabel(self.yaxis_label)    # Label on the y-axis
        xlabel(self.xaxis_label)    # Label on the x-axis

    def render(self):
        raise Exception('YOU ARE DOING IT WRONG!')

    def to_file(self, text):        # Creates the output-file.

        fn = self.output +os.sep+ text.lower() +'_'+self.file_postfix
        dname = os.path.dirname(fn)
        bname = re.sub('\W', '_', os.path.basename(fn))
        fn = dname +os.sep+ bname

        try:                            # Create output directory
            os.makedirs(self.output)
        except:
            pass

        filenames = []
        for ff in self.file_formats:    # Create the physical files
            filename = "%s.%s" % (fn, ff)
            filenames.append(filename)
            savefig(filename)

        show()

        return filenames
