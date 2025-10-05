import pandas as pd
from custom_parsers.icici_parser import parse

def test_icici_parser():
    pdf = "data/icici/icici_sample.pdf"
    expected = pd.read_csv("data/icici/result.csv")
    out = parse(pdf)
    assert out.equals(expected)
