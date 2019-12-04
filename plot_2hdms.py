import numbers
import csv
from collections import namedtuple
from array import array
import numpy as np

import ROOT

# nice_colours = ['#8dd3c7','#ffffb3','#bebada','#fb8072','#80b1d3','#fdb462','#b3de69','#fccde5'] # light
# nice_colours = ['#e41a1c','#377eb8','#4daf4a','#984ea3','#ff7f00','#ffff33','#a65628','#f781bf'] # medium
# nice_colours = ['#a6cee3','#1f78b4','#b2df8a','#33a02c','#fb9a99','#e31a1c','#fdbf6f','#ff7f00','#cab2d6','#6a3d9a','#ffff99','#b15928'] # paired, 12 entries
nice_colours = ['#7fc97f','#beaed4','#fdc086','#ffff99','#386cb0','#f0027f','#bf5b17','#666666'] # dark
colours = [ROOT.TColor.GetColor(hex) for hex in nice_colours]

Dataset = namedtuple('Dataset', ['csv', 'legend', 'style', 'factors'])

datasets = [
    Dataset('2hdms/sm_obs.txt', 'h_{125} #rightarrow undetected (CMS)', 'l', []),
    Dataset('2hdms/atlas_mmmm_obs.txt', 'h_{125} #rightarrow aa #rightarrow #mu#mu#mu#mu (ATLAS)', 'f', [48610., 'mm', 'mm']),
    Dataset('2hdms/mmmm_obs.txt', 'h_{125} #rightarrow aa #rightarrow #mu#mu#mu#mu (CMS)', 'f', [54620., 'mm', 'mm']),
    Dataset('2hdms/bbtt_obs.txt', 'h_{125} #rightarrow aa #rightarrow bb#tau#tau (CMS)', 'f', [200., 'bb', 'tt']),
    # Dataset('2hdms/mmtt_obs.txt', 'h_{125} #rightarrow aa #rightarrow #mu#mu#tau#tau (CMS)', 'f', [2000., 'mm', 'tt']),
    Dataset('2hdms/atlas_bbmm_obs.txt', 'h_{125} #rightarrow aa #rightarrow #mu#mubb (ATLAS)', 'f', [2., 'mm', 'bb']),
    Dataset('2hdms/mmbb_obs.txt', 'h_{125} #rightarrow aa #rightarrow #mu#mubb (CMS)', 'f', [2., 'mm', 'bb']),
    Dataset('2hdms/atlas_mmtt_obs.txt', 'h_{125} #rightarrow aa #rightarrow #mu#mu#tau#tau (ATLAS)', 'f', ['tt', 'tt']),
    Dataset('2hdms/tttt_obs.txt', 'h_{125} #rightarrow aa #rightarrow #tau#tau#tau#tau (CMS)', 'f', ['tt', 'tt']),
    # Dataset('2hdms/atlas_bbbb_obs.txt', 'h_{125} #rightarrow aa #rightarrow bbbb (ATLAS)', 'f', ['bb', 'bb']),
]

class BRProvider:
    def __init__(self, myfile='Cecile/BR/BR_II_2.0.dat'):
        _, array_mass, _, array_BRbb, _, array_BRtt, array_BRmm, _, _, _, _ = np.loadtxt(myfile, unpack=True)
        self.list_mass = array("d", array_mass)
        # FIXME - make this a dict and simplify the rest of code in the class
        self.list_BRbb = array("d", array_BRbb)
        self.list_BRtt = array("d", array_BRtt)
        self.list_BRmm = array("d", array_BRmm)
    
    def get_index(self, mass):
        for i, m in enumerate(self.list_mass):
            if m > mass:
                if i > 0:
                    return i - 1
        return 0

    def get_BR_tt(self, mass):
        return self.list_BRtt[self.get_index(mass)]

    def get_BR_mm(self, mass):
        return self.list_BRmm[self.get_index(mass)]

    def get_BR_bb(self, mass):
        return self.list_BRbb[self.get_index(mass)]

    def get_factor(self, mass, factor):
        if isinstance(factor, numbers.Number):
            return factor
        if factor == 'tt':
            return self.get_BR_tt(mass)
        if factor == 'mm':
            return self.get_BR_mm(mass)
        if factor == 'bb':
            return self.get_BR_bb(mass)
        return 1.

def create_canvas():
    canv = ROOT.TCanvas("2HDM+S", "2HDM+S Limits", 1000, 640)
    canv.SetGridx(0)
    canv.SetLogx(1)
    canv.SetGridy(0)
    canv.SetLogy(1)
    canv.SetLeftMargin(0.15)
    canv.SetRightMargin(0.05)
    canv.SetTopMargin(0.06)
    canv.SetBottomMargin(0.12)
    return canv

def draw_frame(canv):
    hr = canv.DrawFrame(1., 0.0001, 60., 1.);
    # format x axis
    hr.SetXTitle("m_{a} [GeV]")
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
    hr.SetYTitle("95% CL upper limit on #frac{#sigma_{h_{125}}}{#sigma_{SM}}B(h_{125}#rightarrow aa)");
    hr.GetYaxis().SetLabelFont(42)
    hr.GetYaxis().SetTitleSize(0.05)
    hr.GetYaxis().SetTitleOffset(1.2)
    hr.GetYaxis().SetLabelSize(0.05)
    hr.GetYaxis().SetNdivisions(50005)
    # hr.GetYaxis().SetMoreLogLabels()

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

def get_graph(file_name, brs, factors):
    '''Converts information from CSV file into TGraph
    '''
    ma_sigmabr = []
    with open(file_name) as csv_file:
        csv_reader = csv.reader(csv_file, delimiter=' ')
        for row in csv_reader:
            ma_sigmabr.append((float(row[0]), float(row[1])))

    gr = ROOT.TGraph(len(ma_sigmabr))
    for i, (ma, sigmabr) in enumerate(ma_sigmabr):
        for factor in factors:
            div_by = brs.get_factor(ma, factor)
            if div_by == 0.:
                import pdb; pdb.set_trace()
            sigmabr /= div_by
        gr.SetPoint(i, ma, sigmabr)
    return gr


if __name__ == '__main__':
    cv = create_canvas()
    draw_frame(cv)
    brs = BRProvider()
    graphs = []
    for i, dataset in enumerate(datasets):
        graph = get_graph(dataset.csv, brs, dataset.factors)
        graph_style(graph, i, dataset.style)
        for style in dataset.style:
            graph.Draw(style+'same')
        graphs.append(graph) # so ROOT doesn't delete it
    legend = ROOT.TLegend(0.6, 0.12, 0.93, 0.7)
    legend.SetBorderSize(0)
    legend.SetFillStyle(0)
    # legend.SetTextSize(0.05)
    legend.SetFillColorAlpha(0, 1.)
    legend.SetHeader("2HDM+S Type 2, tan#beta = 2") 
    for graph, dataset in zip(graphs, datasets):
        legend.AddEntry(graph, dataset.legend, dataset.style)
    legend.Draw()
    cv.Print('2hdms.pdf')
