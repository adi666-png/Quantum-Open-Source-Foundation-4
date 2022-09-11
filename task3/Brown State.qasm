OPENQASM 3.0;
include "stdgates.inc";

qreg q[5];
creg c[5];

h q[0];
h q[2];
h q[3];
cx q[0],q[1];
cx q[3],q[4];
x q[1];
cx q[2],q[4];
cz q[2],q[3];
cx q[0],q[4];
cz q[1],q[3];
measure q -> c;