import itertools,numpy as np
import numpy as np

def get_bars_and_stripes(rows,cols):
    '''function to generate the bars and stripes representatin of the target states'''
    _data = [] 
    
    for h in itertools.product([0,1], repeat=cols):
        bas = np.repeat([h], rows, 0)
        _data.append(bas.ravel().tolist())
          
    for h in itertools.product([0,1], repeat=rows):
        bas = np.repeat([h], cols, 1)
        _data.append(bas.ravel().tolist())
    
    _data = np.unique(np.asarray(_data), axis=0)
    return _data

def generate_random_states():
    """ generates random states """
    return [f"{np.random.randint(16):4b}".replace(' ','0') for i in range(4)]
