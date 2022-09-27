import numpy as np
import matplotlib.pyplot as plt
from scipy import stats

class HypothesisTestingHelper():
    @staticmethod
    def runNormalityTest(data:list, dataname:str, savePath):
        dataname = "[" + dataname + "]"

        n = len(data)
        if n < 30:
            print(dataname + " will be ignored (n = " + str(n) + ").")
            return

        k2, p = stats.normaltest(data)

        alpha = 0.05
        is_normal = p < alpha
        if is_normal:  # null hypothesis: x comes from a normal distribution
            print(dataname + " comes from a normal distribution.")
        else:
            print(dataname + " DOES NOT COME from a normal distribution!!")
        
        # === Regardless, generate an image comparing the actual distribution with the "desired" normal distribution...
        
        mu, std = stats.norm.fit(data)

        hist_color = 'g' if is_normal else 'r'
        plt.hist(data, bins=30, density=True, alpha=0.6, color=hist_color)

        xmin, xmax = plt.xlim()
        pdf_x = np.linspace(xmin, xmax, 100)
        pdf_p = stats.norm.pdf(pdf_x, mu, std)

        plt.plot(pdf_x, pdf_p, 'k', linewidth=2)
        title = dataname + " VS. dist. normal com µ = {:.2f}, σ = {:.2f}".format(mu, std)
        plt.title(title)

        plt.savefig(savePath)
        plt.close()
        
