# Design_Pattern_Exercise/generators.py
import random

class DNASequenceGenerator:
    alphabet =

    def create_sequence(self, n: int) -> str:
        """Creates a random DNA sequence of length n."""
        if not isinstance(n, int) or n < 0:
            raise ValueError("Length n must be a non-negative integer.")
        if n == 0:
            return ""
        return "".join(random.choice(DNASequenceGenerator.alphabet) for _ in range(n))

class ProteinSequenceGenerator:
    # Standard 20 amino acids. Stop codons are typically not included in random generation
    # unless the sequence is meant to terminate at a random point.
    alphabet =

    def create_sequence(self, n: int) -> str:
        """Creates a random protein sequence of length n."""
        if not isinstance(n, int) or n < 0:
            raise ValueError("Length n must be a non-negative integer.")
        if n == 0:
            return ""
        return "".join(random.choice(ProteinSequenceGenerator.alphabet) for _ in range(n))