"""Paths and current design scope."""
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1]
HARDWARE=ROOT/'hardware'
ENCLOSURE=ROOT/'enclosure'
DOCS=ROOT/'docs/design'
RFQ=ROOT/'rfq'
VARIANTS=('mini','explore')
BOARDS=('mini','explore','card-reader','story-card')
PARTS=('front','back','print_front','button','buttons','coupon','port_coupon','bridge')
WORK=ROOT/'work/current'
