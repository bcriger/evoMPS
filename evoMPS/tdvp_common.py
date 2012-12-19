# -*- coding: utf-8 -*-
"""
Created on Sun Nov 25 11:49:32 2012

@author: ash
"""

import scipy as sp
import scipy.linalg as la
import numpy as np
import matmul as mm
import nullspace as ns   

def eps_l_noop(x, A1, A2):
    """Implements the left epsilon map (result is conjugated)

    Parameters
    ----------
    x : ndarray
        The argument matrix. For example, using l[n - 1] gives a result l[n]
    A1: ndarray
        The first MPS tensor (will be conjugated) for the current site.
    A2: ndarray
        The second MPS tensor for the current site.    

    Returns
    -------
    res : ndarray
        The resulting matrix.
    """
    out = np.zeros((A1.shape[2], A1.shape[2]), dtype=A1.dtype)
    for s in xrange(A1.shape[0]):
        out += A1[s].conj().T.dot(x.dot(A2[s]))
    return out
    
def eps_l_noop_inplace(x, A1, A2, out):
    out.fill(0)
    for s in xrange(A1.shape[0]):
        out += A1[s].conj().T.dot(x.dot(A2[s]))
    return out
        
def eps_l_op_1s(x, A1, A2, op):
    out = np.zeros((A1.shape[2], A2.shape[2]), dtype=A1.dtype)
    for s in xrange(A1.shape[0]):
        for t in xrange(A1.shape[0]):
            o_st = op[s, t]
            if o_st != 0:
                out += o_st * A1[s].conj().T.dot(x.dot(A2[t]))
    return out
    
def eps_r_noop(x, A1, A2):
    """Implements the right epsilon map

    Parameters
    ----------
    x : ndarray
        The argument matrix. For example, using l[n - 1] gives a result l[n]
    A1: ndarray
        The first MPS tensor (will be conjugated) for the current site.
    A2: ndarray
        The second MPS tensor for the current site.    

    Returns
    -------
    res : ndarray
        The resulting matrix.
    """
    out = np.zeros((A1.shape[1], A2.shape[1]), dtype=A1.dtype)
    for s in xrange(A1.shape[0]):
        out += A1[s].dot(x.dot(A2[s].conj().T))
    return out
    
def eps_r_noop_inplace(x, A1, A2, out):
    out.fill(0)
    for s in xrange(A1.shape[0]):
        out += A1[s].dot(x.dot(A2[s].conj().T))
    return out
    
def eps_r_op_1s(x, A1, A2, op):
    out = np.zeros((A1.shape[1], A1.shape[1]), dtype=A1.dtype)
    for s in xrange(A1.shape[0]):
        for t in xrange(A1.shape[0]):
            o_st = op[s, t]
            if o_st != 0:
                out += o_st * A1[t].dot(x.dot(A2[s].conj().T))
    return out
    
def eps_r_op_2s_A(x, A1, A2, A3, A4, op):
    res = np.zeros((A1.shape[1], A3.shape[1]), dtype=A1.dtype)
    zeros = np.zeros
    for u in xrange(A3.shape[0]):
        for v in xrange(A4.shape[0]):
            subres = zeros((A1.shape[1], A2.shape[2]), dtype=A1.dtype)
            for s in xrange(A1.shape[0]):
                for t in xrange(A2.shape[0]):
                    opval = op[u, v, s, t]
                    if opval != 0:
                        subres += opval * A1[s].dot(A2[t])
            AAuvH = (A3[u].dot(A4[v])).conj().T
            res += subres.dot(x.dot(AAuvH))
    return res
    
def eps_r_op_2s_AA12(x, AA12, A3, A4, op):
    res = np.zeros((AA12.shape[2], A3.shape[1]), dtype=A3.dtype)
    zeros_like = np.zeros_like
    for u in xrange(A3.shape[0]):
        for v in xrange(A4.shape[0]):
            subres = zeros_like(AA12[0, 0])
            for s in xrange(AA12.shape[0]):
                for t in xrange(AA12.shape[1]):
                    opval = op[u, v, s, t]
                    if opval != 0:
                        subres += opval * AA12[s, t]
            AAuvH = (A3[u].dot(A4[v])).conj().T
            res += subres.dot(x.dot(AAuvH))
    return res
    
def eps_r_op_2s_AA_func_op(x, AA12, AA34, op):
    res = np.zeros((AA12.shape[2], AA34.shape[2]), dtype=AA12.dtype)
    zeros_like = np.zeros_like
    for u in xrange(AA34.shape[0]):
        for v in xrange(AA34.shape[1]):
            subres = zeros_like(AA12[0, 0])
            for s in xrange(AA12.shape[0]):
                for t in xrange(AA12.shape[1]):
                    opval = op(u, v, s, t)
                    if opval != 0:
                        subres += opval * AA12[s, t]
            res += subres.dot(x.dot((AA34[u, v]).conj().T))
    return res
    
def eps_r_op_2s_C12(x, C12, A3, A4):
    res = np.zeros((C12.shape[2], A3.shape[1]), dtype=A3.dtype)
    for u in xrange(A3.shape[0]):
        for v in xrange(A4.shape[0]):
            AAuvH = (A3[u].dot(A4[v])).conj().T
            res += C12[u, v].dot(x.dot(AAuvH))
    return res
    
def eps_r_op_2s_C34(x, A1, A2, C34):
    res = np.zeros((A1.shape[1], C34.shape[2]), dtype=A1.dtype)
    for u in xrange(C34.shape[0]):
        for v in xrange(C34.shape[1]):
            res += A1[u].dot(A2[v]).dot(x.dot(C34[u, v].conj().T))
    return res

def eps_r_op_2s_C12_AA34(x, C12, AA34):
    res = np.zeros((C12.shape[2], AA34.shape[2]), dtype=AA34.dtype)
    for u in xrange(AA34.shape[0]):
        for v in xrange(AA34.shape[1]):
            AAuvH = AA34[u, v].conj().T
            res += C12[u, v].dot(x.dot(AAuvH))
    return res
    
def eps_r_op_2s_AA12_C34(x, AA12, C34):
    res = np.zeros((AA12.shape[2], C34.shape[2]), dtype=C34.dtype)
    for u in xrange(C34.shape[0]):
        for v in xrange(C34.shape[1]):
            res += AA12[u, v].dot(x.dot(C34[u, v].conj().T))
    return res
    
def eps_l_op_2s_AA12_C34(x, AA12, C34):
    res = np.zeros((AA12.shape[3], C34.shape[3]), dtype=C34.dtype)
    for u in xrange(C34.shape[0]):
        for v in xrange(C34.shape[1]):
            res += AA12[u, v].conj().T.dot(x.dot(C34[u, v]))
    return res

def calc_AA(A, Ap1):
    Dp1 = Ap1.shape[2]
    Dm1 = A.shape[1]
    q = A.shape[0]
    qp1 = Ap1.shape[0]
    
    AA = sp.zeros((q, qp1, Dm1, Dp1), dtype=A.dtype)
    for u in xrange(q):
        for v in xrange(qp1):
            AA[u, v] = A[u].dot(Ap1[v])
    
    return AA
    
    #This works too: (just for reference)
    #AA = np.array([dot(A[s], A[t]) for s in xrange(self.q) for t in xrange(self.q)])
    #self.AA = AA.reshape(self.q, self.q, self.D, self.D)

def calc_C_mat_op_AA(op, AA):        
    return sp.tensordot(op, AA, ((2, 3), (0, 1)))

def calc_C_func_op(op, A, Ap1):
    q = A.shape[0]
    qp1 = Ap1.shape[0]
    C = sp.zeros((A.shape[0], Ap1.shape[0], A.shape[1], Ap1.shape[2]), dtype=A.dtype)
    for u in xrange(q):
        for v in xrange(qp1):
            AAuv = A[u].dot(Ap1[v])
            for s in xrange(q):
                for t in xrange(qp1):
                    h_nn_stuv = op(s, t, u, v)
                    if h_nn_stuv != 0:
                        C[s, t] += h_nn_stuv * AAuv
    return C
    
def calc_C_func_op_AA(op, AA):
    q = AA.shape[0]
    qp1 = AA.shape[1]
    C = sp.zeros_like(AA)
    for u in xrange(q):
        for v in xrange(qp1):
            AAuv = AA[u, v]
            for s in xrange(q):
                for t in xrange(qp1):
                    h_nn_stuv = op(s, t, u, v)
                    if h_nn_stuv != 0:
                        C[s, t] += h_nn_stuv * AAuv
    return C
    
def calc_K(Kp1, C, lm1, rp1, A, Ap1, sanity_checks=False):
    Dm1 = A.shape[1]
    q = A.shape[0]
    qp1 = Ap1.shape[0]
    
    K = sp.zeros((Dm1, Dm1), dtype=A.dtype)
    
    Hr = sp.zeros_like(K)

    for s in xrange(q):
        Ash = A[s].conj().T
        for t in xrange(qp1):
            Hr += C[s, t].dot(rp1.dot(mm.H(Ap1[t]).dot(Ash)))

        K += A[s].dot(Kp1.dot(Ash))
        
    op_expect = mm.adot(lm1, Hr)
        
    K += Hr
    
    return K, op_expect
    
def calc_l_r_roots(lm1, r, sanity_checks=False):
    try:
        l_sqrt = lm1.sqrt()
        l_sqrt_i = l_sqrt.inv()
    except AttributeError:
        l_sqrt, evd = mm.sqrtmh(lm1, ret_evd=True)
        l_sqrt_i = mm.invmh(l_sqrt, evd=evd)
        
    try:
        r_sqrt = r.sqrt()
        r_sqrt_i = r_sqrt.inv()
    except AttributeError:
        r_sqrt, evd = mm.sqrtmh(r, ret_evd=True)
        r_sqrt_i = mm.invmh(r_sqrt, evd=evd)
    
    if sanity_checks:
        if not np.allclose(l_sqrt.dot(l_sqrt), lm1):
            print "Sanity check failed: l_sqrt is bad!"
        if not np.allclose(l_sqrt.dot(l_sqrt_i), np.eye(lm1.shape[0])):
            print "Sanity check failed: l_sqrt_i is bad!"
        if not np.allclose(r_sqrt.dot(r_sqrt), r):
            print "Sanity check failed: r_sqrt is bad!"
        if (not np.allclose(r_sqrt.dot(r_sqrt_i), np.eye(r.shape[0]))):
            print "Sanity check failed: r_sqrt_i is bad!"
    
    return l_sqrt, l_sqrt_i, r_sqrt, r_sqrt_i
    
def calc_Vsh(A, r_s, sanity_checks=False):
    D = A.shape[2]
    Dm1 = A.shape[1]
    q = A.shape[0]
    
    R = sp.zeros((D, q, Dm1), dtype=A.dtype, order='C')

    for s in xrange(q):
        R[:,s,:] = r_s.dot(mm.H(A[s]))

    R = R.reshape((q * D, Dm1))
    Vconj = ns.nullspace_qr(mm.H(R)).T

    if sanity_checks:
        if not sp.allclose(mm.mmul(Vconj.conj(), R), 0):
            print "Sanity Fail in calc_Vsh!: VR != 0"
        if not sp.allclose(mm.mmul(Vconj, mm.H(Vconj)), sp.eye(Vconj.shape[0])):
            print "Sanity Fail in calc_Vsh!: V H(V) != eye"
        
    Vconj = Vconj.reshape((q * D - Dm1, D, q))

    Vsh = Vconj.T
    Vsh = sp.asarray(Vsh, order='C')

    if sanity_checks:
        M = sp.zeros((q * D - Dm1, Dm1), dtype=A.dtype)
        for s in xrange(q):
            M += mm.mmul(mm.H(Vsh[s]), r_s, mm.H(A[s]))
        if not sp.allclose(M, 0):
            print "Sanity Fail in calc_Vsh!: Bad Vsh"

    return Vsh

   
def calc_x(Kp1, C, Cm1, rp1, lm2, Am1, A, Ap1, lm1_s, lm1_si, r_s, r_si, Vsh):
    D = A.shape[2]
    Dm1 = A.shape[1]
    q = A.shape[0]
    qp1 = Ap1.shape[0]
    
    x = sp.zeros((Dm1, q * D - Dm1), dtype=A.dtype)
    x_part = sp.empty_like(x)
    x_subpart = sp.empty_like(A[0])
    x_subsubpart = sp.empty_like(A[0])
    
    H = mm.H
    
    x_part.fill(0)
    for s in xrange(q):
        x_subpart.fill(0)

        if not C is None:
            x_subsubpart.fill(0)
            for t in xrange(qp1):
                x_subsubpart += C[s,t].dot(rp1.dot(H(Ap1[t]))) #~1st line

            x_subsubpart += A[s].dot(Kp1) #~3rd line

            try:
                x_subpart += r_si.dot_left(x_subsubpart)
            except AttributeError:
                x_subpart += x_subsubpart.dot(r_si)

        x_part += x_subpart.dot(Vsh[s])

    x += lm1_s.dot(x_part)

    if not lm2 is None:
        x_part.fill(0)
        for s in xrange(q):     #~2nd line
            x_subsubpart.fill(0)
            for t in xrange(qp1):
                x_subsubpart += H(Am1[t]).dot(lm2.dot(Cm1[t, s]))
            x_part += x_subsubpart.dot(r_s.dot(Vsh[s]))
        x += lm1_si.dot(x_part)

    return x
    
def restore_RCF_r(A, r, G_n_i, sanity_checks=False):
    """Transforms a single A[n] to obtain right orthonormalization.

    Implements the condition for right-orthonormalization from sub-section
    3.1, theorem 1 of arXiv:quant-ph/0608197v2.

    This function must be called for each n in turn, starting at N + 1,
    passing the gauge transformation matrix from the previous step
    as an argument.

    Finds a G[n-1] such that ON_R is fulfilled for n.

    Eigenvalues = 0 are a problem here... IOW rank-deficient matrices.
    Apparently, they can turn up during a run, but if they do we're screwed.

    The fact that M should be positive definite is used to optimize this.

    Parameters
    ----------
    n : int
        The site number.
    G_n_i : ndarray
        The inverse gauge transform matrix for site n obtained in the previous step (for n + 1).

    Returns
    -------
    G_n_m1_i : ndarray
        The inverse gauge transformation matrix for the site n - 1.
    """
    if G_n_i is None:
        GGh_n_i = r
    else:
        GGh_n_i = G_n_i.dot(r.dot(G_n_i.conj().T))

    M = eps_r_noop(GGh_n_i, A, A)

    try:
        tu = la.cholesky(M) #Assumes M is pos. def.. It should raise LinAlgError if not.
        G_nm1 = mm.invtr(tu).conj().T #G is now lower-triangular
        G_nm1_i = tu.conj().T
    except sp.linalg.LinAlgError:
        print "Restore_ON_R: Falling back to eigh()!"
        e,Gh = la.eigh(M)
        G_nm1 = mm.H(Gh.dot(np.diag(1/sp.sqrt(e) + 0.j)))
        G_nm1_i = la.inv(G_nm1)

    if G_n_i is None:
        G_n_i = G_nm1_i

    if sanity_checks:
        if not sp.allclose(G_nm1.dot(G_nm1_i), np.eye(G_nm1.shape[0]), atol=1E-13, rtol=1E-13):
            print "Sanity Fail in restore_ONR!: Bad GT!"

    for s in xrange(A.shape[0]):
        A[s] = G_nm1.dot(A[s]).dot(G_n_i)
        
    r_nm1 = mm.eyemat(A.shape[1], A.dtype)

    if sanity_checks:
        r_n_ = mm.eyemat(A.shape[2], A.dtype)

        r_nm1_ = eps_r_noop(r_n_, A, A)
        if not sp.allclose(r_nm1_, r_nm1.A, atol=1E-13, rtol=1E-13):
            print "Sanity Fail in restore_RCF_r!: r is bad"
            print la.norm(r_nm1_ - r_nm1)

    return r_nm1, G_nm1_i, G_nm1
    
def restore_RCF_l(A, lm1, Gm1, sanity_checks=False):
    if Gm1 is None:
        x = lm1
    else: 
        x = mm.mmul(mm.H(Gm1), lm1, Gm1)
        
    M = eps_l_noop(x, A, A)
    ev, EV = la.eigh(M)

    l = mm.simple_diag_matrix(ev, dtype=A.dtype)
    G_i = EV

    if Gm1 is None:
        Gm1 = mm.H(EV) #for left uniform case
        lm1 = l #for sanity check

    for s in xrange(A.shape[0]):
        A[s] = Gm1.dot(A[s].dot(G_i))

    if sanity_checks:
        l_ = eps_l_noop(lm1, A, A)
        if not sp.allclose(l_, l, atol=1E-12, rtol=1E-12):
            print "Sanity Fail in restore_RCF_l!: l is bad!"
            print la.norm(l_ - l)

    G = mm.H(EV)

    if sanity_checks:
        if not sp.allclose(sp.dot(G, G_i), sp.eye(G_i.shape[0]),
                           atol=1E-12, rtol=1E-12):
            print "Sanity Fail in restore_RCF_l!: Bad GT!"
    
    return l, G, G_i
