import matplotlib.pyplot as plt
import numpy as np

font = {'family': 'sans-serif',
        'color':  'black',
        'weight': 'normal',
        'size': 30,
        }

class PlottingHelper():
    @staticmethod
    def prepareAndSaveMultiBoxplot(data:list, labels:list, savePath,
        title:str = 'Boxplot', xleg:str = '', yleg:str = ''):
        fig = plt.figure(figsize=(19,10))
        ax = fig.add_subplot(111)

        # Draw the boxplot:
        boxplot = ax.boxplot(data, labels = labels)

        # Reference line at y = 0:
        ax.axhline(y=0, color='g')

        plt.title(title, fontdict=font)
        plt.xlabel(xleg, fontdict=font)
        plt.ylabel(yleg, fontdict=font)
        plt.xticks(fontsize=24)
        plt.yticks(fontsize=24)

        fig.savefig(savePath)
        plt.close()