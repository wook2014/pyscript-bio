import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import argparse

def FormatData(path, sep = '\t', chromosome = 'chr', p_value = 'p'):
    data = pd.read_table(path, sep = sep)
    data['-log10(p_value)'] = -np.log10(data[p_value])
    data[chromosome] = data[chromosome].astype('category')
    data['ind'] = range(len(data))
    data_grouped = data.groupby((chromosome))
    return data, data_grouped

def GenerateManhattan(pyhattan_object, export_path = "Manhattan.png", significance = None, colors = ['#5da9fd', '#fdb15d'], refSNP = False):
    data = pyhattan_object[0]
    data_grouped = pyhattan_object[1]

    fig = plt.figure()
    ax = fig.add_subplot(111)

    x_labels = []
    x_labels_pos = []
    for num, (name, group) in enumerate(data_grouped):
        #group.plot(kind='scatter', x='ind', y='-log10(p_value)', color=colors[num % len(colors)], ax=ax, s= 10000/len(data),figsize=(10,6))
        group.plot(kind='scatter', x='ind', y='-log10(p_value)', color=colors[num % len(colors)], ax=ax,figsize=(12,6))
        x_labels.append(name)
        x_labels_pos.append((group['ind'].iloc[-1] - (group['ind'].iloc[-1] - group['ind'].iloc[0]) / 2))

    ax.spines['right'].set_visible(False)
    ax.spines['top'].set_visible(False)
    ax.set_xticks(x_labels_pos)
    ax.set_xticklabels(x_labels)
    ax.set_xlim([0, len(data)])
    ax.set_ylim([0, data['-log10(p_value)'].max() + 1])
    ax.set_xlabel('Chromosome')
    if significance:
        plt.axhline(y=significance, color='red', linestyle='-', linewidth = 1)
    plt.xticks(fontsize=8, rotation=45)
    plt.yticks(fontsize=8)

    if refSNP:
        for index, row in data.iterrows():
            if row['-log10(p_value)'] >= significance:
                ax.annotate(str(row[refSNP]), xy = (index, row['-log10(p_value)']))

    if export_path:
        plt.savefig(export_path,dpi=300)
    else:
        plt.show()

def qqplot(data, alpha=0.8,export_path ="Q-Q.png"):
    fig = plt.figure()
    ax = fig.add_subplot(111)
    xlabel = 'Expected(-log10)' 
    ylabel = 'Observed(-log10)'
    data = np.array(data, dtype=float)
    length  = len(data)
    e = (np.arange(length)+1-0.5)/length #(0,1) from R function ppoints
    o = -np.log10(sorted(data))
    e = -np.log10(e)
    ax.scatter(e, o, alpha=alpha, edgecolors='none')
    ax.plot([e.min(), e.max()], [e.min(), e.max()], color='r',linestyle='-') # guide line, y=x
    ax.spines['right'].set_visible(False)
    ax.spines['top'].set_visible(False)
    ax.set_xlim(xmin=e.min(), xmax=1.05 * e.max())
    ax.set_ylim(ymin=o.min())
    ax.set_xlabel(xlabel) 
    ax.set_ylabel(ylabel)
    if export_path:
        plt.savefig(export_path,dpi=300)
    else:
        plt.show()

def main():
    parser = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    parser.add_argument("-i", "--input", action="store", dest="infile", required=True,help="GWAS result file,It contains at least chr and p columns")
    parser.add_argument("-s", "--significance", type =str, dest="significance",help="significance,default is NA",default="NA")
    parser.add_argument("-o", "--output", type =str, dest="outfile",help="Output png file name",default="Manhattan.png")
    args = parser.parse_args()
    infile = args.infile
    outfile = args.outfile
    significance = args.significance
    dat_gwas_output = FormatData(infile) #deal with data

    qqplot(dat_gwas_output[0]['p']) #qq plot

    if significance=="NA":
        GenerateManhattan(dat_gwas_output,export_path=outfile) #Manhattan plot
    else:
        GenerateManhattan(dat_gwas_output,export_path=outfile,significance=float(significance))

if __name__ == "__main__":
	# cite: https://github.com/ShujiaHuang/geneview/blob/master/geneview/gwas/_qq.py
	# cite: https://github.com/Pudkip/Pyhattan/blob/master/Pyhattan/__init__.py
    main()
