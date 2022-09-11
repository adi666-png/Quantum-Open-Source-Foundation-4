OPENQASM 3.0;
include "stdgates1.inc";

qreg[3] q;
creg c[3];

reset q;
h q[0];
cx q[0],q[1];
cx q[0],q[2];