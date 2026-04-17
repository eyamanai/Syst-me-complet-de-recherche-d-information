"""
operateurs/__init__.py - Opérateurs booléens
"""


def et(A, B):
    """Intersection ensembliste."""
    return A & B


def ou(A, B):
    """Union ensembliste."""
    return A | B


def non(tous, A):
    """Complément : tous les documents sauf ceux dans A."""
    return tous - A
