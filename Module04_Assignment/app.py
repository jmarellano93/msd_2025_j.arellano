import streamlit as st
import random
import textwrap
import io

# Calculate GC content
def calculate_gc_content(sequence):
    gc_count = sum(1 for base in sequence if base in ['G', 'C'])
    return (gc_count / len(sequence)) * 100 if sequence else 0.0

# Load FASTA from uploaded file
def load_fasta(file_content):
    sequences = {}
    current_header = None
    current_sequence = []
    content = file_content.decode('utf-8').splitlines()

    for line in content:
        line = line.strip()
        if not line:
            continue
        if line.startswith(">"):
            if current_header:
                full_seq = ''.join(current_sequence).upper()
                sequences[current_header] = full_seq
            current_header = line
            current_sequence = []
        else:
            current_sequence.append(line)

    if current_header:
        full_seq = ''.join(current_sequence).upper()
        sequences[current_header] = full_seq

    if not sequences:
        raise ValueError("No sequences found in the FASTA file.")

    return sequences

# Random sequence generator
def generate_random_sequence(length):
    random.seed(42)
    bases = ['A', 'T', 'C', 'G']
    sequence = ''.join(random.choices(bases, k=length))
    header = f">Random_DNA_Seq_{random.randint(1, 99):02}"
    return header, sequence

# Streamlit App
def main():
    st.title("GC-Compute: DNA Sequence GC Content Analyzer")
    st.write("Analyze your DNA sequences in FASTA format for GC-content!")

    st.sidebar.header("Choose an option:")
    option = st.sidebar.radio(
        "Select Input Type:",
        ("Enter DNA Sequence", "Upload FASTA File", "Generate Random DNA Sequence")
    )

    if option == "Enter DNA Sequence":
        st.subheader("Enter Your DNA Sequence in FASTA Format")
        fasta_text = st.text_area(
            "Paste your FASTA formatted sequence below (up to ~1 billion bases)",
            height=300
        )

        if fasta_text:
            try:
                sequences = load_fasta(fasta_text.encode())
                for header, sequence in sequences.items():
                    gc_content = calculate_gc_content(sequence)
                    st.success(f"{header}\nGC-content: {gc_content:.6f}%")
            except Exception as e:
                st.error(f"Error: {e}")

    elif option == "Upload FASTA File":
        st.subheader("Upload a FASTA File (max 1GB uncompressed)")
        uploaded_file = st.file_uploader("Choose a FASTA file", type=["fasta", "fa", "txt"])

        if uploaded_file:
            try:
                sequences = load_fasta(uploaded_file.read())
                for header, sequence in sequences.items():
                    gc_content = calculate_gc_content(sequence)
                    st.success(f"{header}\nGC-content: {gc_content:.6f}%")
            except Exception as e:
                st.error(f"Error: {e}")

    elif option == "Generate Random DNA Sequence":
        st.subheader("Generate a Random DNA Sequence")

        length = st.number_input(
            "Enter desired sequence length (50,000 to 1,000,000,000 bases)",
            min_value=50000,
            max_value=1_000_000_000,
            value=50000,
            step=1000
        )

        if st.button("Generate and Analyze"):
            header, sequence = generate_random_sequence(length)
            gc_content = calculate_gc_content(sequence)
            st.success(f"{header}\nGC-content: {gc_content:.6f}%")
            st.download_button(
                label="Download Generated FASTA File",
                data=f"{header}\n{textwrap.fill(sequence, 80)}",
                file_name="random_sequence.fasta",
                mime="text/plain"
            )

if __name__ == "__main__":
    main()
