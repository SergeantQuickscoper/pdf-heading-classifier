from sentence_transformers import SentenceTransformer, util

# Load models
minilm = SentenceTransformer('all-MiniLM-L6-v2')           # ~90MB
e5 = SentenceTransformer('intfloat/e5-small')              # ~130MB

# Sample test
texts = [
    "Graph neural networks for molecule prediction",
    "Revenue trends of Apple from 2022 to 2024",
    "Mechanism of SN1 and SN2 reactions in organic chemistry"
]

# Persona + Job as query
query = "PhD researcher preparing a literature review on GNNs for drug discovery"

# Encode with MiniLM
minilm_scores = util.cos_sim(minilm.encode(query), minilm.encode(texts))
print("MiniLM scores:\n", minilm_scores)

# Encode with E5 (use the format: 'query: ...')
query_e5 = "query: " + query
e5_scores = util.cos_sim(e5.encode(query_e5), e5.encode(texts))
print("E5 scores:\n", e5_scores)
