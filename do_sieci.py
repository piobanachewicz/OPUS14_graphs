import pandas as pd
import numpy as np
# import seaborn as sns
# from colormap import rgb2hex
# import networkx as nx
# import matplotlib.pyplot as plt
import matplotlib
import dash
from dash import Dash, html
import dash_cytoscape as cyto
import base64
import math 
import collections
##global
cyto.load_extra_layouts()
app = Dash()
compare = lambda x, y: collections.Counter(x) == collections.Counter(y)

#pallete = ['#f8766d','#f17d51','#e98429','#de8a00','#d49200','#c89800','#ba9e00','#aaa300','#97a800','#82ad00','#67b100','#3fb500','#00b929','#00bc4f','#00be6b','#00bf82','#00c097','#00c1aa','#00c0bc','#00becd','#00bbdc','#00b7e9','#00b1f4','#00aafe','#30a2ff','#7299ff','#988fff','#b584ff','#cc7aff','#de70f9','#ec68ee','#f663e1','#fd61d2','#ff61c1','#ff64af','#ff699b','#fd6f85']
#pallete = ['#e6194B', '#3cb44b', '#ffe119', '#4363d8', '#f58231', '#911eb4', '#42d4f4', '#f032e6', '#bfef45', '#fabed4', '#469990', '#dcbeff', '#9A6324', '#fffac8', '#800000', '#aaffc3', '#808000', '#ffd8b1', '#000075', '#a9a9a9']
pallete=['#00008b','#0000ff','#008000','#00bfff','#00ff00','#00ff7f','#20b2aa','#2f4f4f','#483d8b','#556b2f','#6495ed','#778899','#7b68ee','#7fffd4','#808000','#8b0000','#8b008b','#8fbc8f','#9400d3','#98fb98','#a0522d','#adff2f','#afeeee','#c71585','#d2b48c','#da70d6','#daa520','#db7093','#dc143c','#dda0dd','#f0e68c','#ff00ff','#ff4500','#ff7f50','#ff8c00','#ffb6c1','#ffff00']
#pallete=['#000080','#0000ff','#006400','#00bfff','#00fa9a','#00ffff','#6a5acd','#7fff00','#800080','#808000','#808080','#8a2be2','#8b4513','#8fbc8f','#9acd32','#add8e6','#b03060','#dc143c','#ee82ee','#ff0000','#ff00ff','#ff1493','#ff7f50','#ffa500','#ffb6c1','#ffdead','#ffff00']
edge_colors = {'lisc': '#304f40', 'korzen':'#836953', 'lodyga':'#cc5200', 'ziarniak': '#cfcfc4'}

#colors_czesci_roslin = ["#f8766d","#d89000", "#a3a500", "#39b600", "#00bf7d", "#00bfc4", "#00b0f6", "#9590ff", "#e76bf3", "#ff62bc"]

data_all = pd.read_csv("OPUS14_dane_do_garfiki_modified.csv")
spiecies_all = data_all['gatunek'].unique()
spiecies_all.sort()
sp_colors = {}
# for sp, co in zip(spiecies_all, pallete):
#     sp_colors[sp] = co

###
data_g0 = data_all.loc[data_all['Pokolenie'] == 'G0']
data_g1 = data_all.loc[data_all['Pokolenie'] == 'G1']

##
data = data_all
key = 'Pokolenie'
graphTitle = "All organs"

##tablice
spieciesinCurrentData = data['gatunek'].unique()
spieciesinCurrentData.sort()
all_names = {'Pokolenie': data_all['Pokolenie'].unique(),
             'gatunki': data_all['gatunek'].unique(),
             'Forma': data_all['Forma'].unique(),
             'Odmiana': data_all['Odmiana'].unique(),
             'Czesc_rosliny': data_all['Czesc_rosliny'].unique()}
spiecieID = {}
for i in range(len(spiecies_all)):
    spiecieID[spiecies_all[i]] = str(i+1)

labels = {'G0':"Gen. 0",
          'G1':"Gen. 1",
          'jara': "Spring crop", 
          'ozima':"Winter crop", 
          'Rospuda':'Rospuda', 
          'Rusalka':'Rusalka', 
          'Bombona':'Bombona', 
          'Kandela':'Kandela', 
          'Arabella':'Arabella', 
          'Bamberka':'Bamberka', 
          'Ostroga':'Ostroga', 
          'Arkadia':'Arkadia', 
          'Legenda':'Legenda', 
          'Euforia':'Euforia',
          'lisc':'Leaf',
          'lodyga':'Stem',
          'korzen':'Root',
          'ziarniak':'Kernel'}

#to binary
def toBinary(to_change):
    sp_dict = dict.fromkeys(all_names['gatunki'], {'G0':0, 
                                'G1':0,
                                'jara': 0, 
                                'ozima':0, 
                                'Rospuda':0, 
                                'Rusalka':0, 
                                'Bombona':0, 
                                'Kandela':0, 
                                'Arabella':0, 
                                'Bamberka':0, 
                                'Ostroga':0, 
                                'Arkadia':0, 
                                'Legenda':0, 
                                'Euforia':0,
                                'lisc':0,
                                'lodyga':0,
                                'korzen':0,
                                'ziarniak':0
                                })

    binary = pd.DataFrame(sp_dict)
    binary = binary.transpose()

    for index, row in to_change.iterrows():
        binary.loc[row['gatunek'], row['Pokolenie']] = 1
        binary.loc[row['gatunek'], row['Forma']] = 1
        binary.loc[row['gatunek'], row['Odmiana']] = 1
        binary.loc[row['gatunek'], row['Czesc_rosliny']] = 1
    return binary

binaryDf = toBinary(data_all)

bothAsterix = {}
for index, row in binaryDf.iterrows():
    if row['G0'] and row['G1']:
        bothAsterix[index] = "*"
    else:
        bothAsterix[index] = ""
##Mozliwosci
def combs(a):
    if len(a) == 0:
        return [[]]
    cs = []
    for c in combs(a[1:]):
        cs += [c, c+[a[0]]]
    return cs

def getCombinations(ele):
    tmp_possibilities = combs(ele)[1:]
    possibilities = []
    for p in tmp_possibilities:
        p.sort()
        possibilities.append("|".join(p))
    possibilities.sort()

    return possibilities
def getPossible():
    test = {}
    test2 = dict.fromkeys(spiecies_all, "")
    for sp in spiecies_all:
        test[sp] = []
    for index, row in data_all.iterrows():
        if row[key] not in test[row['gatunek']]:
            test[row['gatunek']].append(row[key])

    for k, values in test.items():
        values.sort()
        test2[k] = "|".join(values)
    possible = list(set(test2.values()))

    test = {}
    test2 = dict.fromkeys(spiecies_all, "")
    for sp in spiecies_all:
        test[sp] = []
    for index, row in data_g0.iterrows():
        if row[key] not in test[row['gatunek']]:
            test[row['gatunek']].append(row[key])

    for k, values in test.items():
        values.sort()
        test2[k] = "|".join(values)
    possible += list(set(test2.values()))

    test = {}
    test2 = dict.fromkeys(spiecies_all, "")
    for sp in spiecies_all:
        test[sp] = []
    for index, row in data_g1.iterrows():
        if row[key] not in test[row['gatunek']]:
            test[row['gatunek']].append(row[key])

    for k, values in test.items():
        values.sort()
        test2[k] = "|".join(values)
    possible += list(set(test2.values()))
    possible = list(set(possible))
    possible.sort()
    return possible

def checkGroup():
    grpTMP = {}
    for sp in spiecies_all:
        grpTMP[sp] = []
    groupsWithEmpty = dict.fromkeys(spiecies_all, "")

    for index, row in data.iterrows():
        if row[key] not in grpTMP[row['gatunek']]:
            grpTMP[row['gatunek']].append(row[key])

    for k, values in grpTMP.items():
        values.sort()
        groupsWithEmpty[k] = "|".join(values)

    groups = {}
    for k, value in groupsWithEmpty.items():
        if len(value) > 0:
            groups[k] = value
    
    groupColors = {}
    possibleGroups = getPossible() #getCombinations(all_names[key]) 
    #list(set(groups.values()))
    possibleGroups.sort()
    for n in all_names[key]:
        if n in possibleGroups:
            continue
        possibleGroups.append(n)

    colorJump = math.floor(len(pallete) / len(possibleGroups))
    for i in range(len(possibleGroups)):
        groupColors[possibleGroups[i]] = pallete[i*colorJump]

    return groups, groupColors

posib = getCombinations(all_names[key])
groups, groupColors = checkGroup()
# ###czesc rosliny jako glowne nody
# elements = [{'data':{'id':'lisc', 'label':"Leaves", 'url':'https://i.postimg.cc/Pxz6L3HW/leaves.png', 'color':groupColors["lisc"]},
#                    'position': {'x': 100, 'y': 100},
#                    'classes': 'center'}, 
#                   {'data':{'id':'korzen', 'label':"Roots", 'url':'https://i.postimg.cc/7YLB6nWz/roots.png', 'color':groupColors["korzen"]},
#                    'position': {'x': -100, 'y': 100},
#                    'classes': 'center'},
#                   {'data':{'id':'lodyga', 'label':"Stems", 'url':'https://i.postimg.cc/cCxFfR1V/stem.png', 'color':groupColors["lodyga"]},
#                    'position': {'x': 100, 'y': -100},
#                    'classes': 'center'},
#                   {'data':{'id': 'ziarniak', 'label': "Grains", 'url':'https://i.postimg.cc/d0SsbBp9/grain.png', 'color':groupColors["ziarniak"]},
#                    'position': {'x': -100, 'y': -100},
#                    'classes': 'center'}]
    
##ustalanie polozenia grup
def getCenterPositions(): #bingAI
    radius = 150
    positions = {}
    possibleGroups = list(set(groups.values()))

    for soloGroup in all_names[key]:
        if soloGroup not in possibleGroups:
            possibleGroups.append(soloGroup)

    for p in possibleGroups:
        positions[p] = {'x':0, 'y':0}

    for i in range(len(all_names[key])):
        angle = 2 * math.pi * i / len(all_names[key])
        x = radius * math.cos(angle)
        y = radius * math.sin(angle)
        positions[all_names[key][i]]['x'] = math.floor(x)
        positions[all_names[key][i]]['y'] = math.floor(y)

    multiGroupsNum = len(possibleGroups) - len(all_names[key])
    if multiGroupsNum == 1:
        return positions
    i = -1
    for g in possibleGroups:
        if '|' in g:
            i += 1
            angle = 2 * math.pi * i / multiGroupsNum
            x = 0.3 * radius * math.cos(angle)
            y = 0.3 * radius * math.sin(angle)
            positions[g]['x'] = math.floor(x)
            positions[g]['y'] = math.floor(y)
    return positions
    ##nieudany koncept?
    # multiGroupsNum = len(possibleGroups) - len(all_names[key])
    # i = -1
    # for g in possibleGroups:
    #     if '|' in g:
    #         inGroups = g.split('|')
    #         x = 0
    #         y = 0
    #         i += 1
    #         for ig in inGroups:
    #             print(positions[ig])
    #             x += abs(positions[ig]['x'])
    #             y += (positions[ig]['y'])
    #         x /= len(inGroups)
    #         y /= len(inGroups)
    #         angle = 2 * math.pi * i / multiGroupsNum
    #         positions[g]['x'] = abs(math.floor(x)) * math.cos(angle)
    #         positions[g]['y'] = 10 + abs(math.floor(y)) * math.sin(angle)

###dla Gatunkow
def getSpieciesNodesPositions(centerPositins):
    radius = 65
    positions = {}
    numOfElements = {}

    for g in centerPositins.keys():
        numOfElements[g] = 0
        numOfElements[g + '_i'] = 0

    for sp in spieciesinCurrentData:
        positions[sp] = {'x':0, 'y':0}
        if groups[sp] in centerPositins.keys():
            numOfElements[groups[sp]] += 1

    for sp in spieciesinCurrentData:
        if groups[sp] in centerPositins.keys():
            angle = 2 * math.pi * numOfElements[groups[sp] + "_i"] / numOfElements[groups[sp]]
            numOfElements[groups[sp] + "_i"] += 1
            if "|" not in groups[sp]:
                r = radius
            else:
                if numOfElements[groups[sp]] > 1:
                    r = 0.5 * radius
                else:
                    r = 0
            # if "|" in groups[sp] and numOfElements[groups[sp]] > 2:
            #     r = radius * 0.3
            # else:
            #     r = radius
            x = centerPositins[groups[sp]]['x'] + r * math.cos(angle)
            y = centerPositins[groups[sp]]['y'] + r * math.sin(angle)
            positions[sp]['x'] = math.floor(x)
            positions[sp]['y'] = math.floor(y)
        else:
            inGroups = groups[sp].split("|")
            x = 0
            y = 0
            for g in inGroups:
                x += centerPositins[g]['x']
                y += centerPositins[g]['y']
            x /= len(inGroups)
            y /= len(inGroups)
            positions[sp]['x'] = math.floor(x) + 10
            positions[sp]['y'] = math.floor(y) + 10
    return positions
###
def createElements(nodes_species, nodes_data, centerPositions, nodesPosition):
    elements = []
    ##main nodes
    for u in all_names[key]:
        if isLight(groupColors[u]):
            txtColor = 'black'
        else:
            txtColor = 'white' 
        tmp = {'data':{'id': u, 'label': labels[u], 'color':groupColors[u], 'textColor':txtColor},
               'position': {'x': centerPositions[u]['x'], 'y': centerPositions[u]['y']},
               'classes': 'center'}
        elements.append(tmp)
    ##nodes
    for sp in nodes_species:
        if isLight(groupColors[groups[sp]]):
            txtColor = 'black'
        else:
            txtColor = 'white' 
        tmp = {'data':{'id': sp, 'label': spiecieID[sp]+bothAsterix[sp], 'color':groupColors[groups[sp]], 'textColor':txtColor}}
        tmp['position'] = {'x': nodesPosition[sp]['x'], 'y': nodesPosition[sp]['y']}
        elements.append(tmp)

    ##edges
    for index, row in nodes_data.iterrows():
        elements.append({'data':{'source': row[key], 'target': row["gatunek"]}})
    return elements

##
###bingAI
def isLight(hex_color: str) -> bool:
    hex_color = hex_color.lstrip('#')
    # Konwersja do wartości w skali 0-1
    r, g, b = [int(hex_color[i:i+2], 16) / 255 for i in (0, 2, 4)]

    def adjust(c):
        return c / 12.92 if c <= 0.03928 else ((c + 0.055) / 1.055) ** 2.4
    
    r, g, b = adjust(r), adjust(g), adjust(b)
    # Obliczenie luminancji
    luminance = 0.2126 * r + 0.7152 * g + 0.0722 * b

    # Ustalamy próg luminancji – wartość 0.5 jest często dobrym przybliżeniem
    return luminance > 0.5
##
def shapeByGen(elements):
    for e in elements:
        if 'id' not in list(e['data'].keys()):
            break
        sp = e['data']['id']
        if sp in ['lisc', 'korzen', 'lodyga', 'ziarniak']:
            continue
        if binaryDf.loc[sp, 'G0']:
            e['classes'] = 'G0'
        if binaryDf.loc[sp, 'G1']:
            e['classes'] = 'G1'
        if binaryDf.loc[sp, 'G0'] & binaryDf.loc[sp, 'G1']:
            e['classes'] = 'both'

centerPositions = getCenterPositions()
nodesPosition = getSpieciesNodesPositions(centerPositions)
elements = createElements(spieciesinCurrentData, data, centerPositions, nodesPosition)

#elements = "mock"
#shapeByGen(elements)

##Grops Labels
groupLabels = {}
for grp in groups.values():
    g = grp.split('|')
    label = ""
    for name in g:
        label = label + labels[name] + " & "
    groupLabels[grp] = label[:-3]

labelsColors = {}
for key_group, value_label in groupLabels.items():
    labelsColors[value_label] = groupColors[key_group]

labelsColors = sorted_dict = dict(sorted(labelsColors.items()))

aaa = ""
for i in spieciesinCurrentData:
    aaa += spiecieID[i] +". "+i +" "
print(aaa)
##main app
app.layout = html.Div([
    html.H1([graphTitle], style={'text-align' : 'center'}),
    #html.H2(['test'], style={'text-align' : 'center'}),
    cyto.Cytoscape(
        id='cytoscape-styling-1',
        layout={'name': 'preset'},
        style={'width': '50%', 'height': '1200px', 'float' : 'left'},
        elements=elements,
        stylesheet=[
            # Group selectors
            {'selector': 'node',
             'style': {
                 'background-color': 'data(color)',
                 'width' : '20px',
                 'height': '20px',
                 'content' : 'data(label)',
                 'text-halign':'center',
                 'text-valign':'center',
                 'font-size' : '10px',
                 'color' : 'data(textColor)'
                }
            },
            {'selector': 'edge',
             'style': {
                 'line-color': '#7f7f7f',
                 'width' : '0.2'
                }
            },
            # Classes
            {'selector': '.center',
             'style': {
                 'text-halign':'center',
                 'text-valign':'center',
                 'background-color' : 'data(color)',
                 'width' : '50px',
                 'height': '50px'
                }
            }
        ]
    ),

    html.Div([
        html.Div([
            html.Div(spiecieID[i] +". "+i+bothAsterix[i], style = {'font-size' : '25px','font-style': 'italic'}) for i in spieciesinCurrentData], 
            style = {'line-height': '1.5', 'width' : '50%','weight' : '600px', 'float' : 'left', 'column-count':'2'}
        )
    ]),
    html.Div([
        html.Div([
                html.Div('■■', style={'color' : lc, 'letter-spacing': '-5px'}) for lc in labelsColors.values()],
                style = {'float' : 'left', 'line-height': '1.5', 'font-size' : '25px'}
            ),
        html.Div([
                html.Div(lc, style={'color':'black', 'margin-left' : '50px'}) for lc in labelsColors.keys()],
                style = {'text-indent' : '15px', 'line-height': '1.5', 'font-size' : '25px'}
            )],
        style = {'width' : '50%', 'float' : 'left', 'overflow-x': 'hidden', 'overflow-y': 'scroll', 'height':'1000px'}
    )
])

app.run(debug=True)
#["random","preset","circle","concentric","grid","breadthfirst","cose","cose-bilkent","fcose","cola","euler","spread","dagre","klay"]
#                    'background-fit': 'cover',
#                    'background-image': 'data(url)',