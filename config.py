# config.py
from structure import EligibilityCriteria

def load_criteria():
    criteria = EligibilityCriteria()
    return criteria.get_criteria()
