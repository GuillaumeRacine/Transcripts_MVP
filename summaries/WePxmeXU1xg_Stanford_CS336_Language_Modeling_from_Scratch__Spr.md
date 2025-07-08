# Stanford CS336 Language Modeling from Scratch | Spring 2025 | Lecture 13: Data 1

<aside>
📺 🎥 Channel: Stanford Online
📅 Published: 2025-06-10T21:57:42Z
🔗 YouTube: https://www.youtube.com/watch?v=WePxmeXU1xg
</aside>

=== Strategic Overview & Relevance ===

**Why This Matters:**

The data used to train large language models (LLMs) is arguably the most critical factor in determining their capabilities and performance. As LLMs become more powerful and widely deployed, understanding the provenance, composition, and processing of their training data is essential for assessing their strengths, limitations, biases, and potential real-world impact.

This topic is highly relevant as LLMs are rapidly being integrated into a wide range of applications, from search engines and chatbots to coding assistants and content generation tools. The data used to train these models directly shapes what they "know", the tasks they can perform, and crucially, what biases and failure modes they may exhibit. Rigorous analysis of training data is necessary to ensure LLMs are safe, reliable, and aligned with human values as they are deployed in high-stakes domains.

The composition of training data also has major implications for issues like intellectual property, privacy, and data governance. As LLMs trained on web-scale data become commercialized, questions around copyright, fair use, and data licensing are coming to the forefront. Understanding the legal and ethical dimensions of training data is critical for AI companies, policymakers, and other stakeholders.

**Strategic Context:**

In the bigger picture, the "data-centric" view of AI capabilities advanced in this lecture represents an important paradigm shift. While architectural innovations and scaling laws have driven much progress in LLMs, data quality and diversity are increasingly seen as the key levers for further gains. This insight is causing leading AI labs to invest heavily in data curation and synthesis.

For the AI research community, this points to data-focused interventions, like filtering, augmentation and targeted collection, as some of the highest-leverage paths to creating more capable and aligned language models. Benchmarks and best practices around documenting and releasing training data are critical for the scientific integrity of the field.

For companies developing and deploying LLMs, training data is becoming a key source of competitive advantage. Proprietary, high-quality datasets may be as important as model architectures and computing power. At the same time, the need to respect intellectual property and personal privacy creates challenges in leveraging web-scale data. Navigating this tradeoff will be crucial.

More broadly, the importance of training data highlights the need for robust data governance frameworks and practices in the AI industry. Documenting data provenance, implementing accountability structures, and proactively addressing potential biases and misuse risks will be essential for maintaining public trust as LLMs become ubiquitous. Policymakers, ethicists, and responsible AI practitioners have a major role to play here.

In summary, while data may be the most neglected ingredient in the LLM recipe, it is in many ways the most important. As LLMs continue their rapid ascent, training data will be at the center of the action - in both scientific and societal terms. Engaging thoughtfully with the issues raised in this lecture will be critical for anyone seeking to understand and shape the trajectory of this transformative technology.

Here are the key takeaways and technical details from the lecture on data for language modeling:

Key Takeaways:

1. Data is the most important factor in getting language models right. Companies are secretive about their training data due to competitive dynamics and legal concerns.

- Data curation and cleaning requires significant effort, even more so than model architecture development. 
- Data work is highly parallelizable, allowing companies to allocate large teams to cover different aspects like multilinguality and multimodality.
- The lines between pre-training, mid-training, and post-training data are blurry. Models generally start with large amounts of lower quality data and progress to smaller, higher quality datasets.

2. Web crawled data like Common Crawl requires extensive filtering and processing to be usable for training. 

- Common Crawl aims for diversity over comprehensiveness. It doesn't contain all web pages and has duplicates.
- Extracting clean, natural language from raw HTML/HTTP responses is challenging. Different tools yield very different results.
- Filtering heuristics look at aspects like punctuation, number of sentences, presence of bad words, languages, etc. Model-based filtering is increasingly used.

3. Instruction tuning relies heavily on crowdsourced, synthetically generated, and creatively sourced datasets.

- Early work used GPT-4 to generate instruction data, but this violates terms of use. Newer open models enable less restricted distillation.
- Datasets combine public sources like Reddit, Wikipedia, Stack Exchange with synthetic generation from open models and reasoning traces.
- Some high-quality instruction data is created by hired annotators, which is expensive and slow but avoids IP restrictions.

4. Copyright law and fair use doctrines raise complex legal questions around training data.

- Most web content is copyrighted by default, even without explicit notices. Licenses are required for legal use.
- Fair use enables some unlicensed use for education, research, transformation, etc. But the lines are blurry for ML training.
- Even with licenses or fair use, terms of service may prohibit web scraping and redistribution of content.

Technical Details:

- CCNet used an n-gram model trained on Wikipedia to score and filter Common Crawl pages for "wikipedia-like" quality
- C4 (Colossal Clean Crawled Corpus) used heuristics like punctuation, number of sentences, presence of braces, etc. Resulted in 750B tokens.
- GPT-3 trained a classifier to identify "high-quality" pages similar to WebText, Wikipedia, and books. Resulted in 400B tokens.
- Pile combined 22 diverse, high-quality domains suggested by researchers in a collaborative effort. 825 GiB of data.
- ROOTS used Reddit and Wikipedia references to score Common Crawl pages. Trained BERT-like models.
- Chinchilla and PaLM focused on scaling laws, but PaLM filtered Common Crawl with n-gram and neural classifiers.
- BLOOM emphasized data diversity across languages and domains. 1.6T tokens across 46 natural languages and 13 programming languages.
- Llama 2 used 40B tokens from public datasets combined with 60B tokens of crowdsourced high-quality instruction tuning data.

The key themes highlight the central role of data curation, the challenges of extracting usable data from web crawls, the growing use of synthetic data generation for instruction tuning, and the complex legal landscape around training data and fair use. The technical evolution shows a progression from heuristics to learned models for data filtering and an emphasis on diversity and quality over sheer scale.

Here are some actionable steps and resources for implementing the insights from this lecture on data for language modeling:

Actionable Implementation:

1. Start by identifying and accessing raw data sources relevant to your language modeling task. Key sources include Common Crawl, GitHub, Wikipedia, books, academic papers, Stack Exchange, Reddit, etc.

2. Process the raw data into a trainable format. Use tools like Trafilatura to extract clean text from HTML. Apply quality filters using manual rules (e.g. Gopher rules) and/or ML-based classifiers trained on high-quality reference data. Remove duplicates. 

3. Curate data subsets aimed at specific capabilities. For long-range context, use books or math data. For instruction-following, convert NLP benchmarks into prompt-completion format or generate synthetic instructions using language models.

4. Decide on an approach for instruction data - use open datasets, generate synthetic instructions from open LMs, or hire annotators to create high-quality examples. Weigh cost, speed, quality.

5. Evaluate data quality by training models and measuring performance on relevant benchmarks. Iterate on data filtering and curation.

6. Be mindful of legal (copyright, terms of use) and ethical considerations. Aim for "fair use" by being transformative. Consider releasing processed datasets with permissive licenses.

Key Resources:

- Common Crawl - web archive with periodic snapshots
- GitHub - 28M public code repositories 
- Books3 - books from shadow libraries (no longer available)
- The Pile - diverse 800GB text dataset from Eleuther AI
- C4 (Colossal Clean Crawled Corpus) - processed Common Crawl from Google 
- RedPajama - reproduction of LLaMA training data
- OpenWebText2 - recreation of GPT-3 training data from Common Crawl
- Trafilatura - tool for extracting main content from web pages
- Gopher filtering rules - heuristics used by DeepMind for quality filtering
- FastChat, Vicuna, Alpaca - open source chatbots with instruction data

Next Steps:
- Access and explore raw data sources to understand their characteristics
- Implement a basic data processing pipeline to convert a subset of raw data to trainable format
- Train initial models and evaluate to get a baseline, then iterate
- Dive deeper into data filtering techniques, both rule-based and ML-based
- Explore instruction datasets and techniques for aligning models to follow instructions
- Stay on top of emerging open source datasets and models to learn from their approaches

The key is to get hands-on experience working with the actual data. Expect it to be messy and involve a lot of iteration. Focus on defining clear quality criteria and implementing scalable processing pipelines. Look to open source projects for inspiration but don't be afraid to innovate!

---

**Source**: [Stanford CS336 Language Modeling from Scratch | Spring 2025 | Lecture 13: Data 1](https://www.youtube.com/watch?v=WePxmeXU1xg)

*Generated on 2025-07-08 at 16:54:21*