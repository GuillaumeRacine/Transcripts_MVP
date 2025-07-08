# Stanford CS336 Language Modeling from Scratch | Spring 2025 | Lecture 15: Alignment - SFT/RLHF

<aside>
📺 **Channel:** Stanford Online  
📅 **Published:** 2025-06-20T17:33:21Z  
🔗 **YouTube:** https://www.youtube.com/watch?v=Dfu7vC9jo4w
</aside>

---

## 🎯 Strategic Overview & Why This Matters

Here is a strategic overview and analysis of why this matters:

Why This Matters:
The lecture covers key techniques used to train large language models (LLMs) to be safe, truthful, and aligned with human preferences. This is critically important as LLMs become more powerful and widely deployed in real-world applications. Without careful training, LLMs could generate harmful content, spread misinformation, or pursue unintended goals. The methods covered, especially reinforcement learning from human feedback (RLHF), are essential for making LLMs beneficial and trustworthy as they are integrated into consequential domains like education, healthcare, business, and government.

The lecture also highlights the immense challenges in collecting high-quality human feedback data to train these models. Fact-checking model outputs, catching subtle biases, and judging open-ended responses is extremely difficult and labor-intensive for human raters. This bottleneck will become more severe as models and training datasets scale up. Promising directions include using AI to assist the human evaluation process and developing more sample-efficient RL algorithms.

Strategic Context:
These techniques are a key focus area for AI labs working on frontier LLMs (OpenAI, Anthropic, DeepMind, etc). Solving the AI alignment problem is seen as crucial for realizing the potential of artificial general intelligence (AGI) while mitigating existential risks. Companies are investing heavily in RLHF and related methods to make their models safer and more useful.

RLHF has enabled a new generation of powerful chatbots and digital assistants (ChatGPT, Claude, Bard, etc). Continued advances could transform how humans interact with AI systems across domains. However, challenges remain in making RLHF more robust, sample-efficient, and scalable to increasingly large models. Careful thought is needed on the human oversight involved and potential failure modes.

Longer-term, RLHF is a key paradigm for imbuing AI systems with human preferences, values, and goals. Mastering these techniques is important for steering the trajectory of AI development in beneficial directions as the technology grows more advanced. Policymakers, business leaders, and society at large need to understand the core concepts and grapple with the implications. Overall, this is a critical area that will shape the future of AI and its impact on the world.

## 📊 Detailed Analysis & Key Takeaways

Here are the key takeaways and technical details from the lecture:

Key Takeaways:

1. Transition from pre-training to post-training
- Pre-training packs models with capabilities, but post-training is needed to make them useful and safe
- Instruct GPT paper outlines 3-step process: supervised fine-tuning, RL, pairwise feedback loop
- Boundaries between pre-training and post-training are blurring with practices like mid-training

2. Collecting high-quality instruction tuning data is challenging
- Aggregating existing NLP datasets is one approach (e.g. Flan), but can lead to unnatural data
- Crowdsourcing (e.g. Open Assistant) and AI-generated data (e.g. Alpaca) are other methods
- Defining "high-quality" is complex - more knowledge/citations can encourage hallucination
- Stylistic factors like response length bias judgments of quality

3. Pairwise feedback and RLHF aim to improve upon supervised fine-tuning
- Collecting demonstrations for SFT is expensive; pairwise comparisons are cheaper 
- People don't always agree with themselves on what's good, so validation > generation
- But pairwise feedback still has challenges - fact-checking, subjectivity, ethical concerns
- AI feedback (e.g. from GPT-4) increasingly used to scale up pairwise data collection

4. RLHF optimizes a reward function rather than imitating a distribution
- Treats LMs as policies to maximize reward rather than probabilistic models
- Conceptually: roll out model, collect pairwise feedback, train reward model, optimize policy
- Proximal Policy Optimization (PPO) is key algorithm; aims to improve policy without straying too far

Technical Details:

- Instruct GPT equation for RLHF objective: maximize reward R_θ(x,y) minus KL divergence from SFT policy
- Reward modeling assumes each output has scalar reward; pairwise comparisons are logistic model of reward difference (Bradley-Terry model)
- Policy gradient theorem allows optimizing reward by weighting log probabilities by reward
- PPO introduces clipped importance sampling to enable multiple gradient steps per rollout
- Debate over simplifying RLHF by removing PPO complexities 
- Divergence-minimizing Policy Optimization (DPO): assumes nonparametric policy, optimizes implied reward using MLE on pairwise comparisons
- Derivation: express optimal policy in terms of reward, solve for implied reward, optimize probability of pairwise feedback

The lecture covered the transition from pre-training to post-training, focusing on instruction tuning and RLHF. It highlighted challenges in collecting high-quality data, the motivation for pairwise feedback over SFT, and the technical details of RLHF optimization using PPO and DPO algorithms. Key themes included the blurring of pre-training/post-training boundaries, the complexities of defining "high-quality" data, the trend towards AI feedback, and the conceptual shift to optimizing reward rather than imitating a distribution in RLHF.

## 🚀 Implementation Guide & Resources

Here are some key steps and resources for implementing the insights from this lecture on language modeling with alignment and safety:

Actionable Implementation:

1. Collect high-quality instruction tuning data through expert demonstrations, crowdsourcing, or AI-generated feedback. Be mindful of length effects, factual accuracy, and annotator biases.

2. Perform supervised fine-tuning (SFT) on the instruction data to adapt the pre-trained model to follow instructions. Experiment with mixing instruction data into the later stages of pre-training.

3. Collect pairwise human feedback data comparing model outputs. Use clear annotation guidelines focused on helpfulness, truthfulness, and safety. Allow sufficient time for fact-checking.

4. Train a reward model on the pairwise feedback data to assign scalar rewards to model outputs. 

5. Use the reward model to perform reinforcement learning from human feedback (RLHF) to further align the model. Start with simpler algorithms like DPO before trying more complex ones like PPO.

6. Evaluate the resulting model on both open-ended tasks (with human ratings) and closed-form benchmarks to assess capabilities and alignment. Monitor for issues like hallucination and length bias.

Key Resources:

- InstructGPT paper: Details the 3-stage process of SFT, reward modeling, and RLHF used by OpenAI
- Constitutional AI paper (Anthropic): Introduces the idea of AI-generated feedback for RLHF
- Mini-GPT-4 paper: Example of using a two-stage pre-training setup with instruction data mixed in
- Sparks of Artificial General Intelligence paper: Demonstrates impressive instruction-following capabilities of GPT-4
- TuLU 3.0 (AI2): Recent work using AI feedback and off-policy RLHF for model alignment

Next Steps:

- Experiment with collecting instruction data and pairwise feedback, starting small 
- Implement supervised fine-tuning and the DPO algorithm to gain hands-on experience
- Dive deeper into more advanced RLHF algorithms like PPO
- Stay up to date on the latest research in instruction tuning, alignment, and factuality

The most important things are to iterate quickly, evaluate rigorously, and remain vigilant for potential failure modes. Aligning powerful language models is still an open challenge requiring thoughtful data collection and algorithm design. But with the right approaches, we can make meaningful progress towards safer and more helpful AI systems.

---

**📖 Source:** [Stanford CS336 Language Modeling from Scratch | Spring 2025 | Lecture 15: Alignment - SFT/RLHF](https://www.youtube.com/watch?v=Dfu7vC9jo4w)  
**🤖 Generated:** 2025-07-08 at 17:53:25 using Claude 3 Opus