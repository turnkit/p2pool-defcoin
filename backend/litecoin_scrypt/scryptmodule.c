// Copyright (C) 2013 Free Software Foundation, Inc. <http://fsf.org/>
//
// This program is free software: you can redistribute it and/or modify
// it under the terms of the GNU Affero General Public License as published by
// the Free Software Foundation, either version 3 of the License, or
// (at your option) any later version.
//
// This program is distributed in the hope that it will be useful,
// but WITHOUT ANY WARRANTY; without even the implied warranty of
// MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
// GNU Affero General Public License for more details.
//
// You should have received a copy of the GNU Affero General Public License
// along with this program.  If not, see <http://www.gnu.org/licenses/>.

#define PY_SSIZE_T_CLEAN 1
#include <Python.h>

#include "scrypt.h"

static PyObject *scrypt_getpowhash(PyObject *self, PyObject *args, PyObject* kwargs)
{
    char *input;
    Py_ssize_t inputlen;
    char *outbuf;
    PyObject *value = NULL;

    static char *g2_kwlist[] = {"input", NULL};

    if (!PyArg_ParseTupleAndKeywords(args, kwargs, "y#", g2_kwlist,
                                     &input, &inputlen)) {
        return NULL;
    }

    outbuf = PyMem_Malloc(32);
    if (outbuf == NULL) {
        return PyErr_NoMemory();
    }

    Py_BEGIN_ALLOW_THREADS;
    scrypt_1024_1_1_256(input, outbuf);
    Py_END_ALLOW_THREADS;

    value = Py_BuildValue("y#", outbuf, 32);
    PyMem_Free(outbuf);
    return value;
}

static PyMethodDef ScryptMethods[] = {
    { "getPoWHash", (PyCFunction) scrypt_getpowhash, METH_VARARGS | METH_KEYWORDS, "Returns the proof of work hash using scrypt" },
    { NULL, NULL, 0, NULL }
};

static struct PyModuleDef scryptmodule = {
    PyModuleDef_HEAD_INIT,
    "ltc_scrypt",
    NULL,
    -1,
    ScryptMethods
};

PyMODINIT_FUNC PyInit_ltc_scrypt(void) {
    return PyModule_Create(&scryptmodule);
}
