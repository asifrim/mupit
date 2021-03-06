"""
Copyright (c) 2016 Genome Research Ltd.

Permission is hereby granted, free of charge, to any person obtaining a copy of
this software and associated documentation files (the "Software"), to deal in
the Software without restriction, including without limitation the rights to
use, copy, modify, merge, publish, distribute, sublicense, and/or sell copies
of the Software, and to permit persons to whom the Software is furnished to do
so, subject to the following conditions:

The above copyright notice and this permission notice shall be included in all
copies or substantial portions of the Software.

THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY, FITNESS
FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE AUTHORS OR
COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER LIABILITY, WHETHER
IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM, OUT OF OR IN
CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE SOFTWARE.
"""

import math
import pandas

def standardise_ddd_de_novos(path, extra_columns=[]):
    """ get standardised de novo data for DDD study.
    
    Args:
        path: path to DDD de novo dataset
        extra_columns: list of additional columns to retain (such as ['pp_dnm'])
    
    Returns:
        data frame of de novos, including gene symbol, functional consequence
        (VEP format), chromosome, nucleotide position and SNV or INDEL type.
    """
    
    variants = pandas.read_table(path, sep="\t")
    
    # standardise the SNV or INDEL flag
    variants["type"] = (variants["ref"].str.len() == 1) & (variants["alt"].str.len() == 1)
    variants["type"] = variants["type"].map({True: "snv", False: "indel"})
    
    # standardise the columns, and column names
    variants["person_id"] = variants["person_stable_id"]
    variants["start_pos"] = variants["pos"]
    variants["ref_allele"] = variants["ref"]
    variants["alt_allele"] = variants["alt"]
    variants["end_pos"] = variants["start_pos"] + variants["ref_allele"].str.len() - 1
    
    variants["hgnc"] = variants["symbol"]
    
    variants["study_code"] = "ddd_unpublished"
    variants["publication_doi"] = None
    variants["study_phenotype"] = "developmental_disorders"
    
    # standardise the sex codes
    variants["sex"] = variants["sex"].map({"M": "male", "F": "female"})
    
    columns = ["person_id", "sex", "chrom", "start_pos", "end_pos", "ref_allele",
        "alt_allele", "hgnc", "consequence", "study_code", "publication_doi",
        "study_phenotype", "type"]
    columns += extra_columns
    
    variants = variants[columns].copy()
    
    return variants

def open_known_genes(path):
    """ open the dataset of known developmental disorder genes
    
    Args:
        path: path to known developmental disorder genes data file.
    
    Returns:
        DataFrame for the known genes.
    """
    
    with open(path) as handle:
        header = handle.readline()
        sep = '|' if header.count('|') > 0 else '\t'
    
    genes = pandas.read_table(path, sep=sep, index_col=False)
    genes = genes.rename(columns={'DDD.category': 'type',
        'ddg2p_status': 'type', 'allelic.requirement': 'mode',
        'mutation.consequence': 'mech', 'gencode_gene_name': 'gene'})
    
    genes = genes[~genes['type'].str.lower().isin(["possible dd gene"])]
    
    # clean up a few column values
    genes['chr'] = genes['chr'].str.lstrip('chr')
    genes['mode'] = [ x[0].upper() + x[1:] if type(x) != float else None for x in genes['mode'] ]
    genes['mech'] = [ x[0].upper() + x[1:] if type(x) != float else None for x in genes['mech'] ]
    
    genes["dominant"] = genes["mode"].isin(["Monoallelic", "X-linked dominant"])
    genes["hemizygous"] = genes["mode"] == "Hemizygous"
    
    return genes

def get_ddd_rates(rates_path):
    """ load DDD mutation rates, and rename columns to match Samocha et al.
    
    Args:
        rates_path: path to table of mutation rates.
    
    Returns:
        pandas dataframe of mutation rates per gene, across different consequence
        types.
    """
    
    rates = pandas.read_table(rates_path, sep="\t")
    
    # convert from my column names to those used when estimating the gene
    # mutation rates given the cohort size
    rates["hgnc"] =  rates["transcript_id"]
    rates["mis"] = 10 ** rates["missense_rate"]
    rates["non"] = 10 ** rates["nonsense_rate"]
    rates["splice_site"] = 10 ** rates["splice_lof_rate"]
    rates["syn"] = 10 ** rates["synonymous_rate"]
    rates["frameshift"] = 10 ** rates["frameshift_rate"]
    
    rates = rates[["hgnc", "chrom", "length", "mis", "non", "splice_site",
        "syn", "frameshift"]].copy()
    
    return rates
