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

import pandas

def standardise_ddd_de_novos(path):
    """ get standardised de novo data for DDD study.
    
    Args:
        path: path to DDD de novo dataset
    
    Returns:
        data frame of de novos, including gene symbol, functional consequence
        (VEP format), chromosome, nucleotide position and SNV or INDEL type.
    """
    
    variants = pandas.read_table(path, sep="\t")
    
    # standardise the SNV or INDEL flag
    variants["type"] = "indel"
    variants["type"][variants["var_type"] == "DENOVO-SNP"] = "snv"
    
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
    variants["sex"][variants["sex"] == "M"] = "male"
    variants["sex"][variants["sex"] == "F"] = "female"
    
    variants = variants[["person_id", "sex", "chrom", "start_pos",
        "end_pos", "ref_allele", "alt_allele", "hgnc", "consequence",
        "study_code", "publication_doi", "study_phenotype", "type"]]
    
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
    
    sep = "\t"
    if header.count("|") > 0:
        sep = "|"
    
    genes = pandas.read_table(path, sep=sep, index_col=False)
    if "ddg2p_status" in genes.columns:
        genes = genes[genes["ddg2p_status"] != "Possible DD Gene"]
    else:
        genes = genes[genes["type"] != "Possible DD Gene"]
    
    if "gencode_gene_name" not in genes.columns:
        genes["gencode_gene_name"] = genes["gene"]
    
    genes["dominant"] = genes["mode"].isin(["Monoallelic", "X-linked dominant"])
    genes["hemizygous"] = genes["mode"] == "Hemizygous"
    
    return genes