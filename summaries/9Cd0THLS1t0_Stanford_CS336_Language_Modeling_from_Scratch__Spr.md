# Stanford CS336 Language Modeling from Scratch | Spring 2025 | Lecture 14: Data 2

<aside>
📺 🎥 Channel: Stanford Online
📅 Published: 2025-06-16T16:14:37Z
🔗 YouTube: https://www.youtube.com/watch?v=9Cd0THLS1t0
</aside>

=== Part 1: Strategic Overview & Relevance ===

**Why This Matters**:

The techniques covered in this lecture on data filtering and deduplication for language models have significant implications for the development of large language models (LLMs) and their real-world applications. As web-scale data becomes the primary source for training LLMs, ensuring data quality and efficiency is critical. Poor quality data can lead to suboptimal model performance, biases, factual inaccuracies, and even regurgitation of copyrighted or private information. Deduplication reduces wasted compute and helps avoid over-representation of certain content.

These methods are strategically important now as LLMs are rapidly increasing in size and the demand for high-quality training data is skyrocketing. Companies are engaging in data races to procure ever-larger datasets to train frontier models with hundreds of billions of parameters. Implementing scalable data filtering and deduplication pipelines is key to staying competitive.

The techniques covered have broad applicability - from general web-scale pretraining corpora, to domain-specific datasets for specialized models (e.g. biomedicine, math, code). Improving data quality and efficiency leads to better downstream task performance, fairness, and safety of deployed models used for question-answering, summarization, code generation, and more. It also mitigates risks around memorization of sensitive content.

**Strategic Context**:

In the bigger picture, data-centric AI development is gaining prominence, with the realization that data quality is as important as model architecture. As LLMs become foundational for a wide range of applications, there is increased scrutiny on the datasets used to train them.

For companies building LLMs, implementing state-of-the-art data filtering and deduplication will be a key differentiator in producing high-performing and efficient models. Longer-term, techniques for constructing high-quality datasets, including instruction tuning, could become a competitive moat.

On the research side, better data curation methods can help accelerate progress by improving experimental reproducibility and enabling more systematic comparisons between modeling approaches. Scalable data filtering is also important for emerging areas like reinforcement learning with human feedback.

Key stakeholders that should pay attention include:
- Companies developing and deploying large language models 
- AI researchers working on LLMs and related areas
- Policymakers and social scientists examining LLM datasets
- Software engineers building data preprocessing pipelines
- Businesses using LLMs for various applications

In summary, while often overshadowed by model architecture, data filtering and deduplication techniques covered in this lecture are crucial considerations as language models continue scaling up. Mastering the art of dataset creation will only become more strategically important over time.

Here are the key takeaways and technical details from the lecture:

Key Takeaways:

1. Data filtering is important for curating high-quality datasets for language model training. Key approaches include:

- Fitting n-gram models on target data and scoring raw data 
- Training linear classifiers like fastText to predict if data is from target distribution
- Importance resampling by estimating target and proposal distributions

2. The same data filtering machinery can be applied to various tasks beyond just quality filtering, such as language identification and toxicity filtering. The general recipe is:
- Estimate a model based on target and raw data to get a scoring function 
- Keep high-scoring examples from the raw dataset

3. Exact and near-duplicate detection is critical for efficient training and avoiding memorization in language models. Key algorithms:
- Exact duplicates can be removed using Bloom filters in linear time
- Locality-sensitive hashing (LSH) with MinHash enables approximate near-duplicate detection

4. The number of hash functions and bands in LSH controls the sharpness of the collision probability curve around the Jaccard similarity threshold. More hash functions sharpen the threshold, while more bands shift the curve left.

5. Spending time analyzing the data, iteratively filtering it, and training models is crucial for building intuition on what works. Purely algorithmic approaches are just a starting point.

Technical Details:

- N-gram models are fit by counting n-grams and normalizing, with techniques like Kneser-Ney smoothing to handle unseen n-grams
- FastText trains a linear classifier but reduces parameters by having a lower-dimensional hidden layer. Hashing is used to handle arbitrary n-grams.
- Importance resampling weights each raw data example by the ratio p(x)/q(x) of the target and proposal distributions. These are often estimated by simple n-gram models.
- Bloom filters hash each item k times into a bit array of size m. False positive rate is controlled by the number of hash functions k and size m.
- MinHash has the property that Pr[h(A)=h(B)] = Jaccard(A,B). This is because only items in the intersection can be the minimum hash value.
- Locality-sensitive hashing bands together r MinHash values. If any band collides, the items are considered a near-duplicate.
- The probability of collision at the threshold Jaccard similarity t is 1-1/e ≈ 0.63. Below t it drops sharply to 0, above t it rises sharply to 1.

The lecture covered several specific algorithms, equations, and code examples to illustrate these key points. Overall, it emphasized the importance of data filtering and deduplication as key steps in the language model training pipeline that require careful engineering.

Here is Part 3 of the comprehensive analysis, focusing on actionable implementation guidance and resources:

Actionable Implementation:

1. Determine the unit of duplication (sentence, paragraph, document) based on your data and goals. Start with paragraphs or documents.

2. For exact deduplication:
- Implement a map-reduce pipeline that hashes items and keeps one item per hash value 
- Or use a Bloom filter with target false positive rate of 10^-5, hashing at paragraph level

3. For near-deduplication:
- Use minhash locality sensitive hashing (LSH)
- Break N hash functions into B bands of R hash functions each
- Declare items as duplicates if all hashes in any band match
- Tune B and R to get desired similarity threshold and collision probabilities
- Example config: B=20, R=450 for 0.99 similarity threshold 

4. Measure impact on downstream model quality and training efficiency. Aim for 10-20% data size reduction with minimal quality impact.

5. Incorporate deduplication into a recurring data pipeline that runs on all raw data sources prior to model training.

Comprehensive Resources:

- Key papers: 
C4 (2020) - used exact dedup of 3-sentence spans
DOMA (2022) - Bloom filter for exact, minhash LSH for near-dedup
Efficient Estimation of Word Representations in Vector Space (2013) - minhash for near-dedup

- Bloom filter lecture notes: https://www.cs.cmu.edu/~dga/15-744/S07/lectures/16-bloom.pdf 

- Minhash and LSH tutorial: http://infolab.stanford.edu/~ullman/mmds/ch3.pdf

- Open source tools:  
Spark - map reduce for exact dedup
Databricks - Bloom filter and LSH implementations
Dedupe - Python library for deduplication 

- Key concepts for further study: Jaccard similarity, hash functions, map reduce, nearest neighbor search

Next Steps:

- Implement exact deduplication using map reduce on a sample of your raw data
- Experiment with Bloom filters and minhash LSH for near-deduplication 
- Measure impact on downstream tasks like perplexity, question-answering, summarization
- Scale up deduplication to cover all data sources in training pipeline
- Explore more semantic embedding-based approaches for fuzzy deduplication
- Share findings with other teams to establish best practices

The key is to start simple with exact matching, then layer on more sophisticated near-deduplication techniques in a scalable map-reduce style framework. Careful tuning of hyperparameters like number of bands and rows in LSH is critical. Measure impact closely and incorporate deduplication as a standard preprocessing step for more efficient and higher quality language model training. Further research into embedding-based approaches can capture more semantic duplicates.

---

**Source**: [Stanford CS336 Language Modeling from Scratch | Spring 2025 | Lecture 14: Data 2](https://www.youtube.com/watch?v=9Cd0THLS1t0)

*Generated on 2025-07-08 at 16:55:48*