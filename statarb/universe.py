"""Candidate pairs for the cointegration screen. Picked for a plausible
economic reason to move together, not because they happen to be
correlated - correlation and cointegration are not the same thing.
"""

from dataclasses import dataclass


@dataclass(frozen=True)
class CandidatePair:
    ticker_a: str
    ticker_b: str
    rationale: str


UNIVERSE: list[CandidatePair] = [
    CandidatePair("KO", "PEP", "Beverage duopoly, same retail shelf and input costs (sugar, aluminum)."),
    CandidatePair("XOM", "CVX", "Integrated oil majors, priced off the same crude benchmark."),
    CandidatePair("JPM", "BAC", "Money-center banks, same rate environment and credit cycle."),
    CandidatePair("MA", "V", "Card payment networks, near-duopoly on transaction volume growth."),
    CandidatePair("HD", "LOW", "Home improvement retail duopoly, same housing market exposure."),
    CandidatePair("T", "VZ", "Telecom duopoly, same spectrum/infrastructure costs."),
    CandidatePair("UNP", "CSX", "Class I railroads, same freight volume cycle."),
    CandidatePair("DUK", "SO", "Regulated utilities, earnings set largely by state rate cases."),
    CandidatePair("LIN", "APD", "Industrial gas duopoly, overlapping customer base."),
    CandidatePair("TRV", "CB", "Large P&C insurers, same underwriting cycle."),
    CandidatePair("DAL", "UAL", "Major network airlines, same fuel cost and travel demand exposure."),
    CandidatePair("TXN", "ADI", "Analog semiconductor peers, overlapping industrial/auto customers."),
    CandidatePair("BLK", "TROW", "Asset managers, fees tied to AUM and equity market levels."),
    CandidatePair("PG", "CL", "Household and personal care staples, same retail shelf."),
    CandidatePair("MCD", "YUM", "Quick service restaurant franchisors, same royalty model."),
    CandidatePair("WM", "RSG", "Waste hauling duopoly, regional monopoly style economics."),
    CandidatePair("LMT", "NOC", "Defense primes, same US defense budget cycle."),
    CandidatePair("AVB", "EQR", "Apartment REITs, same coastal rental demand exposure."),
    CandidatePair("COF", "SYF", "Card issuing consumer lenders, same credit cycle."),
    CandidatePair("DD", "DOW", "Diversified chemical majors, same feedstock costs."),
    CandidatePair("UPS", "FDX", "Parcel delivery duopoly, same e-commerce volume growth."),
]
