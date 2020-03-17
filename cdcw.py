#compiler design coursework
import time
import os
import sys
from networkx import *
import matplotlib.pyplot as plt
import networkx as nx

#usedful functions i made:
def log(file, valid):
    f = open("logfile.txt", "a");
    s = "failed, invalid formula";
    if valid:
        s = "valid, successful parsing";
        
    f.write(f"{time.asctime()}\t file: {file}\t status: {s}\n");
    f.close();
    return 0;
def glist(l):
    s = "";
    for i in l:
        s = s+ f"|{i}"
    return s[1:];
def strippredi(quant):
    t = 0;
    for i in range(len(quant)):
        if ((quant[i] == "(") or (quant[i] == "[")):
            t= i
    q = quant[:t];
    s = quant[t+1:-1].split(",");
    return(q,s);
#i had this idea to define "blocks" idk if it's gonna work though
#nevermind, not doing that

class Block(object):
    def __init__(self, top, left, right, op):
        self.top = top;
        self.left = left;
        self.right = right;
        self.op = op;
    def display(self):
        print(f"{top}({left}{op}{right})");

#code from stack overflow to draw the graph a bit more neatly as a binary tree
def hierarchy_pos(G, root=None, width=1., vert_gap = 0.2, vert_loc = 0, xcenter = 0.5):

    '''
    From Joel's answer at https://stackoverflow.com/a/29597209/2966723.  
    Licensed under Creative Commons Attribution-Share Alike 

    If the graph is a tree this will return the positions to plot this in a 
    hierarchical layout.

    G: the graph (must be a tree)

    root: the root node of current branch 
    - if the tree is directed and this is not given, 
      the root will be found and used
    - if the tree is directed and this is given, then 
      the positions will be just for the descendants of this node.
    - if the tree is undirected and not given, 
      then a random choice will be used.

    width: horizontal space allocated for this branch - avoids overlap with other branches

    vert_gap: gap between levels of hierarchy

    vert_loc: vertical location of root

    xcenter: horizontal location of root
    '''
    if not nx.is_tree(G):
        raise TypeError('cannot use hierarchy_pos on a graph that is not a tree')

    if root is None:
        if isinstance(G, nx.DiGraph):
            root = next(iter(nx.topological_sort(G)))  #allows back compatibility with nx version 1.11
        else:
            root = random.choice(list(G.nodes))

    def _hierarchy_pos(G, root, width=1., vert_gap = 0.2, vert_loc = 0, xcenter = 0.5, pos = None, parent = None):
        '''
        see hierarchy_pos docstring for most arguments

        pos: a dict saying where all nodes go if they have been assigned
        parent: parent of this branch. - only affects it if non-directed

        '''

        if pos is None:
            pos = {root:(xcenter,vert_loc)}
        else:
            pos[root] = (xcenter, vert_loc)
        children = list(G.neighbors(root))
        if not isinstance(G, nx.DiGraph) and parent is not None:
            children.remove(parent)  
        if len(children)!=0:
            dx = width/len(children) 
            nextx = xcenter - width/2 - dx/2
            for child in children:
                nextx += dx
                pos = _hierarchy_pos(G,child, width = dx, vert_gap = vert_gap, 
                                    vert_loc = vert_loc-vert_gap, xcenter=nextx,
                                    pos=pos, parent = root)
        return pos


    return _hierarchy_pos(G, root, width, vert_gap, vert_loc, xcenter)



def parse(formula, variables, constants, predicates, equality, connectives, quantifiers):
    print("trying to generate syntax tree. parsing...");
    try:
        j = 0;
        tree = DiGraph();
        first_node_created = False;
        prev_node = None;
        prev = -1;
        u = 0;
        while(j < len(formula)):
            prevlist = [];
            i = formula[j];
            #print(j);
            
            if i == '(':
                tree.add_node(u);
                tree.nodes[u]["label"] = None;
                if(u>0):
                    tree.add_edge(prev,u);
                #print("create blank node: ");
                prev = u;
                u+=1;
            elif((i in connectives) or (i in equality)):
                if(formula[j-1] in connectives):
                    tree.add_node(u);
                    tree.nodes[u]["label"] = i;
                    if(prev>=0):
                        tree.add_edge(prev,u);
                    prev = u;
                    u+=1;
                    #print("place 'negation' -type (unary) connective as a child of the most recently visited node")
                else:    
                    while(tree.nodes[prev]["label"] != None):
                        prev = list(tree.predecessors(prev))[0];
                    tree.nodes[prev]["label"] = i;
                    #print(f"go up until you find a blank node and replace with {i}: ");
            elif((i in variables)or(i in constants)or(i in quantifiers)or(strippredi(i)[0] in predicates)):
                #print(f"add a node with value {i}");
                tree.add_node(u);
                tree.nodes[u]["label"] = i;
                if(prev>=0):
                    tree.add_edge(prev,u);
                prev = u;
                u+=1;

            elif i == ')':
                #print("go up one node: ");
                prev = list(tree.predecessors(prev))[0];
                
            else:
                print("error");
                return 0;
            j = j+1;
        return tree;
    except:
        return 0


#validation variable to be set to false whenever something deosnt look right           
valid = True;
#read in lines for rules and stuff
file = sys.argv[1];
lines = [];
f = open(file, "r");
for i in f:
  lines.append(i);

#initialise variables for rules and stuff
variables = [];
constants = [];
predicates = {};
equality = [];
connectives = [];
quantifiers = [];

#collect variable identifiers
v = lines[0][10:];
variables = v.split();
#print(variables);

#collect constant identifiers
const = lines[1][10:];
constants = const.split();
#print(constants);

#collect predicate identifiers and their "arity"
p = lines[2][11:];
pr = p.split();
for i in pr:
    y = strippredi(i);
    x = y[0];
    n = int(y[1][0]);
    predicates[x] = int(n);
#print(predicates);

#collect equality symbol
equality = lines[3][9:].split();
#print(equality);

#collect connective identifiers
c = lines[4][12:];
connectives = c.split();
#print(connectives);

#collect quantifier identifiers
q = lines[5][12:];
quantifiers = q.split();
#print(quantifiers);

#make grammar

grammar = f"S->(S)|SCS|SC|CS\nS->P(T)\nS->S{equality[0]}S\nS->QX\nS->{glist(variables)}|{glist(constants)}\nP->{glist(predicates)}\nX->X,X|{glist(variables)}|{glist(constants)}\nT->T,T|{glist(variables)}|{glist(constants)}|<epsilon>\nC->C,C|{glist(connectives)}";
f = open(f"{file[:-4]}-grammar.txt", "a")
f.write("GRAMMAR:\n");
f.write(grammar);
f.write("\n\n......\n");
f.write(f"ORIGINAL DATA COLLECTED FROM INPUT: \n variables:{variables}\nconstants: {constants}\npredicates and their 'arity': {predicates}\n equality: {equality}, connectives: {connectives},quantifiers: {quantifiers}")
f.close()
print("grammar saved.");

#initialise formula string and list
formula = [];
form = "";
formul = [];

#collect formula into a list ignoring spaces, and separating symbols
for i in range(6,len(lines)):
    form = form + lines[i];
formul = form[8:].split();
print();
print();
print();
for i in formul:
    if((len(i)>1)and(i[0]=="(")):
        formula.append(i[0]);
        formula.append(i[1:]);
    elif((len(i)>1)and(i[-1]==")")and(strippredi(i)[0] not in predicates)):
        formula.append(i[:-1]);
        formula.append(i[-1]);
    else:
        formula.append(i);
print(formula);
#validating brackets:
brackets = [];
for i in formula:
    if i in ["(",")"]:
        brackets.append(i)
tot = 0;
for i in brackets:
    if i =="(":
        tot = tot+1;
    elif i==")":
        tot = tot-1;
        
if tot !=0:
    print("invalid brackets");
    valid = False;
if len(brackets):
    if((brackets[0] == ")") or (brackets[-1] == "(")):
       valid = False;
#validating quantifiers
        
predis = [];
for i in formula:
    b = strippredi(i)
    if b[0] in predicates:
        predis.append(b)
for x in predis:
    if predicates[x[0]] != len(x[1]):
        valid = False
    for y in x[1]:
        if (y not in variables) and (y not in constants):
            print("invalid predicates");
            valid = False;
for i in formula:
    if ((i not in ["(",")"] )and(i not in variables )and(i not in constants)and(i not in quantifiers)and(i not in equality)and(i not in connectives)and (strippredi(i)[0] not in predicates)):
        print("invalid symbols");
        valid = False;
        



#draw and save graph if valid
if valid:
    pt = parse(formula, variables, constants, predicates, equality, connectives, quantifiers);
    if pt ==0:
        valid = False;
    if valid:
        for node in pt.nodes:
            if pt.nodes[node]["label"] == None:
                print("invalid tree");
                valid = False;
    if valid:
        pos = hierarchy_pos(pt,0);
        draw(pt, pos = pos, labels = nx.get_node_attributes(pt, 'label'),node_size=1000);
        plt.savefig(f"{file[:-4]}-syntax-tree.png");
        print("graph saved");
        plt.show();
if not valid:
    print("invalid formula");
log(file, valid);
