import csv
from collections import namedtuple
import ROOT

# nice_colours = ['#8dd3c7','#ffffb3','#bebada','#fb8072','#80b1d3','#fdb462','#b3de69','#fccde5'] # light
# nice_colours = ['#e41a1c','#377eb8','#4daf4a','#984ea3','#ff7f00','#ffff33','#a65628','#f781bf'] # medium
nice_colours = ['#a6cee3','#1f78b4','#b2df8a','#33a02c','#fb9a99','#e31a1c','#fdbf6f','#ff7f00','#cab2d6','#6a3d9a','#ffff99','#b15928'] # paired, 12 entries
# nice_colours = ['#7fc97f','#beaed4','#fdc086','#ffff99','#386cb0','#f0027f','#bf5b17','#666666'] # dark
colours = [ROOT.TColor.GetColor(hex) for hex in nice_colours]

Dataset = namedtuple('Dataset', ['csv', 'legend', 'style'])

datasets = [
    Dataset('csv/ATL_comb.csv', 'h_{125} (ATLAS)', 'l'),
    Dataset('csv/HIG-17-031-observed.csv', 'h_{125} (CMS)', 'l'),
    # Dataset('csv/ATL_ditau.csv', 'A/H #rightarrow #tau#tau (ATLAS)', 'f'),
    Dataset('csv/ATL_ditau_new.csv', 'A/H #rightarrow #tau#tau (ATLAS)', 'f'),
    Dataset('csv/HIG-17-020-observed_new.csv', 'A/H #rightarrow #tau#tau (CMS)', 'f'),
    # Dataset('csv/HIG-18-023-observed.csv', 'A #rightarrow Zh (CMS)', 'f'),
    # Dataset('csv/ATL-HIG-2016-11-observed.csv', 'H^{+} #rightarrow #tau#nu (ATLAS)', 'f'),
    Dataset('csv/ATL-HDBS-2018-58-observed.csv', 'H #rightarrow hh (ATLAS)', 'f'),
    Dataset('csv/HIG-17-033-observed.csv', 'H #rightarrow WW (CMS)', 'f'),
    # Dataset('csv/ATL-HIGG-2017-04-observed.csv', 'H^{+} #rightarrow tb (ATLAS)', 'f'),
    Dataset('csv/ATL-HDBS-2018-51-observed.csv', 'H^{+} #rightarrow tb (ATLAS)', 'f'),
    Dataset('csv/HIG-17-027-observed.csv', 'A/H #rightarrow t#bar{t} (CMS)', 'f'),

]


def create_canvas():
    canv = ROOT.TCanvas("MSSM", "MSSM Limits (hMSSM)", 1000, 640)
    canv.SetGridx(0)
    # canv.SetLogx(1)
    canv.SetGridy(0)
    canv.SetLogy(1)
    canv.SetLeftMargin(0.10)
    canv.SetRightMargin(0.05)
    canv.SetTopMargin(0.06)
    canv.SetBottomMargin(0.12)
    return canv

def draw_frame(canv):
    hr = canv.DrawFrame(130., 1., 2000., 60.);
    # format x axis
    hr.SetXTitle("m_{A} [GeV]")
    hr.GetXaxis().SetLabelFont(42)
    hr.GetXaxis().SetLabelSize(0.05)
    hr.GetXaxis().SetLabelOffset(0.015)
    hr.GetXaxis().SetTitleSize(0.05)
    hr.GetXaxis().SetTitleFont(42)
    hr.GetXaxis().SetTitleColor(1)
    hr.GetXaxis().SetTitleOffset(1.20)
    hr.GetXaxis().SetNdivisions(50005)
    hr.GetXaxis().SetMoreLogLabels()
    hr.GetXaxis().SetNoExponent()
    # format y axis
    hr.SetYTitle("tan#beta");
    hr.GetYaxis().SetLabelFont(42)
    hr.GetYaxis().SetTitleSize(0.05)
    hr.GetYaxis().SetTitleOffset(0.9)
    hr.GetYaxis().SetLabelSize(0.05)
    hr.GetYaxis().SetNdivisions(50005)
    hr.GetYaxis().SetMoreLogLabels()

def graph_style(g, i, style='f'):
    g.SetLineColor(colours[i])
    g.SetLineStyle(1)
    g.SetLineWidth(-303 if style == 'l' else 1)
    g.SetMarkerStyle(20)
    g.SetMarkerSize(0.7)
    g.SetMarkerColor(colours[i])
    g.SetLineColor(colours[i])
    g.SetFillColor(colours[i])
    g.SetFillColorAlpha(colours[i], 0.5)
    g.SetFillStyle(3004 if style == 'l' else 1001) # 3005

def get_graph(file_name):
    '''Converts information from CSV file into TGraph
    '''
    ma_tanb = []
    with open(file_name) as csv_file:
        csv_reader = csv.reader(csv_file)
        for row in csv_reader:
            ma_tanb.append((float(row[0]), float(row[1])))

    gr = ROOT.TGraph(len(ma_tanb))
    for i, (ma, tanb) in enumerate(ma_tanb):
        gr.SetPoint(i, ma, tanb)
    return gr


if __name__ == '__main__':
    cv = create_canvas()
    draw_frame(cv)
    graphs = []
    for i, dataset in enumerate(datasets):
        graph = get_graph(dataset.csv)
        graph_style(graph, i, dataset.style)
        for style in dataset.style:
            graph.Draw(style+'same')
        graphs.append(graph) # so ROOT doesn't delete it
    legend = ROOT.TLegend(0.72, 0.14, 0.995, 0.72)
    legend.SetBorderSize(0)
    legend.SetFillStyle (0)
    # legend.SetTextSize(0.019)
    legend.SetFillColorAlpha(0, 1.)
    legend.SetHeader("Observed exclusion 95% CL") 
    for graph, dataset in zip(graphs, datasets):
        legend.AddEntry(graph, dataset.legend, dataset.style)
    legend.Draw()
    cv.Print('hmssm.pdf')
