import matplotlib.pyplot as plt

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

        plt.title(title)
        plt.xlabel(xleg)
        plt.ylabel(yleg)

        fig.savefig(savePath)
        plt.close()