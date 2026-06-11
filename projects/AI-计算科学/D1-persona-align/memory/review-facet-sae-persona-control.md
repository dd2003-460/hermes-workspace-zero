# Review: Facet-Level Persona Control via Trait-Activated Routing with Contrastive SAE

**Paper**: Facet-Level Persona Control by Trait-Activated Routing with Contrastive SAE for Role-Playing LLMs
**Authors**: Wenqiu Tang, Zhen Wan, Takahiro Komamizu, Ichiro Ide (Japan, NAIST)
**Approach**: Contrastive Sparse AutoEncoder (SAE) for role-playing with facet-level personality vectors.

## Key Insights

1. **Contrastive SAE**: Learns distinct personality control vectors in model activations, enabling "precise and interpretable personality steering" without retraining.

2. **Trait-activated routing**: Different personality facets activate different routing paths in the model, allowing fine-grained control.

3. **Advantage over keyword injection**: Keywords work at the prompt level (text layer). SAE vectors work at the activation level (neural layer). Activation-level control is more direct and doesn't dilute the model's core reasoning.

4. **Interpretable steering**: Unlike embedding-based approaches, SAE makes personality vectors visible and adjustable.

## Connection to persona-v3

1. **Keyword vs Vector**: persona-v3 uses keyword matching (text-level). This paper proposes activation-level control. The two approaches are complementary:
   - Keywords: good for prompt injection (what we do)
   - SAE vectors: good for model-level steering (future work)

2. **Potential upgrade path**: persona-v3 keyword signatures could be used to TRAIN SAE vectors. The keyword matching scores (per-dimension) could be the supervision signal for learning facet vectors.

3. **Facet-level alignment**: Our 6 dimensions map to "facets." A contrastive SAE would learn 6 distinct activation vectors, one per dimension.

## Action Items

1. Research SAE implementation for our 6 dimensions
2. Keyword matching → SAE training pipeline
3. Evaluate activation-level vs keyword-level persona consistency
