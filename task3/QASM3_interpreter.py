from qiskit import QuantumCircuit, QuantumRegister, ClassicalRegister
import numpy as np
from pathlib import Path
import re

class QASM3toQCirc:
    """This program converts OpenQASM3 code to Qiskit QuantumCircuit Object for QOSF Cohort 4 Task 3.
       This does not capture the vastness of the OPENQASM 3.0 standard which itself is in development.
       It can perform operations for X, Y, Z, RX, RY, RZ, H, S, S†, T, T†, CX, CCX, SWAP & CSWAP gates
       and can initialise and pass variables as arguments to gates. It cannot make new gates and cannot check for errors
       as of now."""
    def __init__(self, prog_file=None, str_exp=None):
        ''' takes the QASM3 program as the only user defined input argument'''
        self.ptr = 0  # self.ptr is initialised to zero and is used to read the string expression from start to end
        if str_exp is not None and prog_file is None:
            self.str_exp = str_exp  # the OPENQASM 3 string
        if str_exp is None and prog_file is not None:
            self.str_exp = Path(prog_file).read_text()
        if prog_file is None and str_exp is None:
            print(
                "Specify a OpenQASM program to convert, either as a file or as a string"
            )
        self.params = {}    # dictionary of variables in the program
        self.grp_no = 0     # to print the line number in debug info
        self.debug = False  # the debug flag helps to identify the faulty part of the parsing in the code

    def run(self, input_exp):
        '''does the necessary parsing for the input expression
            and returns the evaluated one after running'''
        final_expr = ''
        expr_var = re.search('[_a-zA-Z]+', input_exp)
        if expr_var is not None and expr_var.group() != 'pi':
            var_start, var_end = expr_var.span()  
            # this gets the span of the expression in the current line
            while True:
                if expr_var.group() != 'pi':
                    final_expr = final_expr + \
                        (input_exp[:var_start] +
                            str(self.params[expr_var.group()][1]))
                expr_var = re.search('[_a-zA-Z]+', input_exp[var_end:])
                if expr_var is not None:
                    var_start, var_end = expr_var.span()
                else:
                    break
            final_expr += input_exp[var_end:]
            final_expr = final_expr.replace('pi', 'np.pi')

        else:
            final_expr = input_exp.replace('pi', 'np.pi')

        # eval is used as we are sure about the behaviour of the expressions
        return eval(final_expr)

    def get_prev_line_str(self, start_ptr):
        '''get next line of OpenQASM3 code'''
        idx = self.ptr
        while self.str_exp[idx] != '\n':
            idx -= 1
            if idx <= start_ptr:
                break
        line = self.str_exp[idx:self.ptr]
        self.ptr = idx - 1
        return line

    def get_symb(self, line):
        '''gets the symbols and parameters from each line of OpenQASM3 code'''
        symb = re.split(r'\s|\[|\]|\(|\)|,|;', line)
        try:
            while True:
                symb.remove('')
        except ValueError:
            pass
        return symb

    def get_next_line_str(self):
        '''get next line of OpenQASM3 code'''
        idx = self.ptr
        while self.str_exp[idx] != '\n':
            idx += 1
            if idx == len(self.str_exp):
                break
        line = self.str_exp[self.ptr:idx]
        self.ptr = idx + 1
        return line

    def init_reg(self, symb):
        '''initialize quantum and classical registers
            and store the corresponding objects in the str_exp variable'''

        if symb[0] in ['qreg', 'qubit']:
            #  ----------------------------------------------------------------------------------------------------
            #  the following code block handles the two different formats for initialising the registers :
            #   qubit[5] q1,q2...q5
            #   qreg q1[3],q2[5]....
            #  ----------------------------------------------------------------------------------------------------
            try:                                                                    # check if the third symbol is actually an Integer or not by trying to convert its type. 
                int(symb[2])                                                        # If it is an Integer, then handle the expression of type : qreg q1[3],q2[5]....
                reg_idxs = [i for i in range(1, len(symb), 2)]                      
                for i in range(1, len(symb), 2):
                    self.params[symb[i]] = QuantumRegister(int(symb[i + 1]),
                                                           name=symb[i])
            except ValueError:                                                      # else, handle the expression of type : qubit[5] q1,q2...q5
                reg_idxs = [i for i in range(2, len(symb))]
                self.params[symb[2]] = QuantumRegister(int(symb[1]),
                                                       name=symb[2])
                if len(symb) > 3:
                    left_regs = symb[3:]
                    for i in range(len(left_regs)):
                        self.params[left_regs[i]] = QuantumRegister(
                            int(symb[1]), name=left_regs[i])

        elif symb[0] in ['creg', 'bit']:
            try:
                int(symb[2])
                reg_idxs = [i for i in range(1, len(symb), 2)]
                for i in range(1, len(symb), 2):
                    self.params[symb[i]] = ClassicalRegister(int(symb[i + 1]),
                                                             name=symb[i])
            except ValueError:
                reg_idxs = [i for i in range(2, len(symb))]
                self.params[symb[2]] = ClassicalRegister(int(symb[1]),
                                                         name=symb[2])
                if len(symb) > 3:
                    left_regs = symb[3:]
                    for i in range(len(left_regs)):
                        self.params[left_regs[i]] = ClassicalRegister(
                            int(symb[1]), name=left_regs[i])
        return reg_idxs

    def init_params(self, symb):
        self.params[symb[1]] = (symb[0], symb[3])

    def add_gate(self, qc, line_symb, dagger=False):
        ''' Adds gates to the QuantumCircuit qc.
            line_symb : list of the parameters in the current line
            dagger : boolean ; indicates the mode of circuit making
            eval() is used as we are sure about the behaviour of the expressions'''

        dag_gates = ['s', 't', 'sdg', 'tdg']

        if self.debug is True:
            print(self.grp_no, line_symb)
            self.grp_no += 1

        if line_symb[0] in ['x', 'y', 'z', 'h']:                                                     # here we club all the gates in the QOSF list 
            eval("qc."+line_symb[0] + "(self.params[line_symb[1]][int(line_symb[2])])")              # which have the same syntax of declaration
            return qc
        
        elif line_symb[0] in dag_gates:
            g = dag_gates[(dag_gates.index(line_symb[0])+2)%4] if dagger else line_symb[0]
            eval("qc."+ g + "(self.params[line_symb[1]][int(line_symb[2])])")   
            return qc
            
        elif line_symb[0] in ['rx', 'ry', 'rz']:
            d = 1
            if dagger:
                d = -1
            eval("qc." + line_symb[0] + "(d * self.run(line_symb[1])" +
                 ",self.params[line_symb[2]][int(line_symb[3])])")
            return qc
        elif line_symb[0] in ['cx', 'swap']:
            eval("qc." + line_symb[0] +
                 "(self.params[line_symb[1]][int(line_symb[2])]," +
                 "self.params[line_symb[3]][int(line_symb[4])])")
            return qc
        elif line_symb[0] in ['ccx', 'cswap']:
            eval(
                "qc." + line_symb[0] +
                "(self.params[line_symb[1]][int(line_symb[2])]," +
                "self.params[line_symb[3]][int(line_symb[4])],self.params[line_symb[5]][int(line_symb[6])])"
            )
            return qc
        elif line_symb[0] in ['reset', 'barrier']:
            #  ----------------------------------------------------------------------------------------------------
            #  the following code block handles the two different formats for specifying the reset or barrier :
            #   barrier q[0] : for individual qubit barrier
            #   barrier q : for barrier-ing the entire quantum register
            #  ----------------------------------------------------------------------------------------------------
            if len(line_symb) > 2:
                ii = 1
                while ii < len(line_symb):
                    try:                                                                                # check if the third symbol is actually an Integer or not by trying to convert its type. 
                        int(line_symb[ii + 1])                                                          # If it is an Integer, then handle the expression of type : barrier q[0]....
                        eval("qc." + line_symb[0] + "(self.params[line_symb[ii]][int(line_symb[ii+1])])")
                        ii += 2
                    except ValueError:                                                                  # else, handle the expression of type : barrier q
                        eval("qc." + line_symb[0] + "(self.params[line_symb[ii]])")
                        ii += 1
            else:
                eval("qc." + line_symb[0] + "(self.params[line_symb[1]])")
            return qc
        elif 'measure' in line_symb:
            if line_symb[0] == 'measure':
                #  ----------------------------------------------------------------------------------------------------
                #  the following code block handles the two different formats for specifying the measurement :
                #   measure q[0] -> c[0] : for individual qubit measurement
                #   measure q -> c : for measuring the entire quantum register
                #  ----------------------------------------------------------------------------------------------------
                try:
                    int(line_symb[2])
                    qc.measure(self.params[line_symb[1]][int(line_symb[2])],
                               self.params[line_symb[4]][int(line_symb[5])])
                except ValueError:
                    qc.measure(self.params[line_symb[1]],
                               self.params[line_symb[3]])
            else:
                qc.measure(self.params[line_symb[-1]],
                           self.params[line_symb[0]])
            return qc

    def get_qcirc(self, debug=False):
        '''returns the QuantumCircuit object'''
        self.debug = debug
        qc = QuantumCircuit()
        while self.ptr < len(self.str_exp):
            line = self.get_next_line_str()
            symb = self.get_symb(line)
            if symb == []:
                continue
            elif symb[0] in ['OPENQASM', 'include']:
                continue
            if symb[0] in ['qubit', 'qreg', 'bit', 'creg']:
                reg_idxs = self.init_reg(symb)
                for i in reg_idxs:
                    qc.add_register(self.params[symb[i]])
            elif symb[0] in ['const', 'int', 'float', 'angle']:
                self.init_params(symb)
            else:
                self.add_gate(qc, symb)
        return qc

    def get_inv_qcirc(self, debug=False):
        '''returns the inverted QuantumCircuit object'''
        start_ptr = 0
        prev_ptr = 0
        self.debug = debug
        qc = QuantumCircuit()
        while self.ptr < len(self.str_exp):
            prev_ptr = self.ptr
            line = self.get_next_line_str()
            symb = self.get_symb(line)
            if symb == []:
                continue
            elif symb[0] in ['OPENQASM', 'include']:
                continue
            if symb[0] in ['qubit', 'qreg', 'bit', 'creg']:
                reg_idxs = self.init_reg(symb)
                for i in reg_idxs:
                    qc.add_register(self.params[symb[i]])
            elif symb[0] in ['const', 'int', 'float', 'angle']:
                self.init_params(symb)
            else:
                if start_ptr == 0:
                    start_ptr = prev_ptr
                continue
        self.ptr = len(self.str_exp) - 1
        while self.ptr > start_ptr:
            line = self.get_prev_line_str(start_ptr)
            symb = self.get_symb(line)
            if symb == []:
                continue
            self.add_gate(qc, symb, dagger=True)
        return qc
