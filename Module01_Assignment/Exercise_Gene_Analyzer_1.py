# To execute notebook in PyCharm, either enable "Emulate Terminal in Output Console" in "Edit Configurations" or simply
# Highlight, right click, and use "Execute Function in Python Console".

# Import necessary packages
import pandas as pd
from pandas import read_csv
import csv

# Import and load dataset (Dataset is a TSV of approximately 7GB.)
# Ask the user to input the file path
file_path = input("Enter the full file path for the gene data TSV file: ").strip()
# Convert the path to a raw string format (fixes backslash issues)
file_path = file_path.replace("\\", "/")
# Load as a DataFrame with tab separator
try:
    gene_df_V1 = pd.read_csv(file_path, sep="\t", low_memory=False)
    print("\n✅ File loaded successfully!")
except FileNotFoundError:
    print("\n❌ Error: File not found. Please check the file path and try again.")
except Exception as e:
    print(f"\n❌ Error: {e}")
column_names = gene_df_V1.columns
print(column_names)

#Cleaning the dataset in preparation for analysis
# Replace placeholder values with NaN
gene_df_V1.replace("-", pd.NA, inplace=True)
# Remove duplicates based on GeneID and Symbol
gene_df_V1 = gene_df_V1.drop_duplicates(subset=['GeneID', 'Symbol'])
# Convert Modification_date to datetime
gene_df_V1['Modification_date'] = pd.to_datetime(gene_df_V1['Modification_date'], format='%Y%m%d')
# Standardize gene type names
gene_df_V1['type_of_gene'] = gene_df_V1['type_of_gene'].str.lower().str.strip()
# Drop unnecessary columns (if needed)
gene_df_V1.drop(columns=['LocusTag', 'dbXrefs', 'Other_designations'], inplace=True)

# To determine all unique gene instances, we can extract the unique values from the 'Symbol' column, as it represents gene symbols.
# Function to determine unique gene counts
def get_unique_gene_counts(df):
    """
    Returns a dataframe with unique gene symbols and their respective counts.
    """
    unique_counts = df['Symbol'].value_counts().reset_index()
    unique_counts.columns = ['Symbol', 'count']
    return unique_counts
# Call function for unique gene counts
unique_gene_counts_df = get_unique_gene_counts(gene_df_V1)
# Calculate the total number of unique genes
total_unique_genes = gene_df_V1['Symbol'].nunique()

#To check if a gene belongs to Homo sapiens, we need to filter based on the #tax_id column. The Homo sapien taxonomic ID is 9606.
# Function to filter Homo sapien genes
def filter_homo_sapien_genes(df):
    """
    Filters the dataframe to include only genes belonging to Homo sapiens (tax_id = 9606).
    """
    homo_sapien_df = df[df['#tax_id'] == 9606]
    total_homo_sapien_genes = homo_sapien_df.shape[0]
    return homo_sapien_df, total_homo_sapien_genes
# Call function for Homo sapien genes
homo_sapien_genes_df, total_homo_sapien_genes = filter_homo_sapien_genes(gene_df_V1)

# Function to determine unique gene types and their frequency
def get_unique_counts(df, column_name):
    """
    Returns a dataframe with unique instances in a dataframe column as keys and their respective counts,
    the most frequently occurring gene type, and a list of all unique gene types.
    """
    unique_counts = df[column_name].value_counts().reset_index()
    unique_counts.columns = [column_name, "count"]
    # Get the most frequently occurring gene type
    most_frequent_gene_type = unique_counts.iloc[0][column_name]
    # Get a list of all unique gene types
    unique_gene_types = unique_counts[column_name].tolist()
    return unique_counts, most_frequent_gene_type, unique_gene_types
# Call function for gene types
gene_type_counts_df, most_frequent_gene_type, unique_gene_types = get_unique_counts(gene_df_V1, "type_of_gene")

print("\n=== FINAL ANSWERS ===")
print(f"Answer Q1 - The total number of unique gene instances listed is: {total_unique_genes}")
print(f"Answer Q2 - The total number of Homo sapien gene instances is: {total_homo_sapien_genes}")
print(f"Answer Q3 - Gene types include: {unique_gene_types}")
print(f"Answer Q4 - The most frequently occurring gene type is: {most_frequent_gene_type}")