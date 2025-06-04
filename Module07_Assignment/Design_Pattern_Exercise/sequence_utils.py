# Design_Pattern_Exercise/sequence_utils.py

# Standard RNA Codon Table (for manual translation)
CODON_TABLE_RNA = {
    'UUU': 'F', 'UUC': 'F', 'UUA': 'L', 'UUG': 'L',
    'UCU': 'S', 'UCC': 'S', 'UCA': 'S', 'UCG': 'S',
    'UAU': 'Y', 'UAC': 'Y', 'UAA': '*', 'UAG': '*',  # '*' are stop codons
    'UGU': 'C', 'UGC': 'C', 'UGA': '*', 'UGG': 'W',
    'CUU': 'L', 'CUC': 'L', 'CUA': 'L', 'CUG': 'L',
    'CCU': 'P', 'CCC': 'P', 'CCA': 'P', 'CCG': 'P',
    'CAU': 'H', 'CAC': 'H', 'CAA': 'Q', 'CAG': 'Q',
    'CGU': 'R', 'CGC': 'R', 'CGA': 'R', 'CGG': 'R',
    'AUU': 'I', 'AUC': 'I', 'AUA': 'I', 'AUG': 'M',  # Methionine, also start codon
    'ACU': 'T', 'ACC': 'T', 'ACA': 'T', 'ACG': 'T',
    'AAU': 'N', 'AAC': 'N', 'AAA': 'K', 'AAG': 'K',
    'AGU': 'S', 'AGC': 'S', 'AGA': 'R', 'AGG': 'R',
    'GUU': 'V', 'GUC': 'V', 'GUA': 'V', 'GUG': 'V',
    'GCU': 'A', 'GCC': 'A', 'GCA': 'A', 'GCG': 'A',
    'GAU': 'D', 'GAC': 'D', 'GAA': 'E', 'GAG': 'E',
    'GGU': 'G', 'GGC': 'G', 'GGA': 'G', 'GGG': 'G',
}


class SequenceConverter:
    """
    Q2: Utility class for sequence operations.
    Contains methods for transcribing DNA to RNA and translating RNA to protein.
    """

    @staticmethod
    def transcribe_dna_to_rna(dna_sequence: str) -> str:
        """Converts a DNA sequence string to an RNA sequence string."""
        if not isinstance(dna_sequence, str):
            raise TypeError("Input DNA sequence must be a string.")
        return dna_sequence.upper().replace('T', 'U')

    @staticmethod
    def translate_rna_to_protein(rna_sequence: str) -> str:
        """
        Translates an RNA sequence string to a protein sequence string.
        The translation stops at the first stop codon.
        Unknown codons are translated as 'X'.
        """
        if not isinstance(rna_sequence, str):
            raise TypeError("Input RNA sequence must be a string.")

        protein_parts = []
        rna_upper = rna_sequence.upper()

        # Iterate over the RNA sequence in steps of 3 (for each codon)
        # Ensure processing only full codons
        for i in range(0, len(rna_upper) - (len(rna_upper) % 3), 3):
            codon = rna_upper[i:i + 3]

            # This check is mostly for safety, range should prevent partial codons
            if len(codon) < 3:
                break

            amino_acid = CODON_TABLE_RNA.get(codon, 'X')  # 'X' for unknown/unhandled codons

            if amino_acid == '*':  # Stop codon found
                break
            protein_parts.append(amino_acid)

        # The syntax error "protein = ^" likely occurred here if this line was malformed.
        # For example, if it was "protein_final = " (incomplete)
        protein_final_sequence = "".join(protein_parts)
        return protein_final_sequence