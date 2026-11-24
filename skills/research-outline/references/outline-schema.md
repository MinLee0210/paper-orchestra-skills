# Outline schema

## Top level

| Key | Type | Required | Meaning |
|---|---|---|---|
| `plotting_plan` | array | yes | figures to generate or collect |
| `intro_related_work_plan` | object | yes | literature search strategy |
| `section_plan` | array | yes | section-by-section writing plan |

## `plotting_plan[]`

| Field | Type | Allowed values |
|---|---|---|
| `figure_id` | string | semantic id, no spaces, no "Figure" |
| `title` | string | short human title |
| `plot_type` | string | `plot` or `diagram` |
| `data_source` | string | `idea.md`, `experimental_log.md`, or `both` |
| `objective` | string | what the figure must show; include chart type |
| `aspect_ratio` | string | `1:1`, `1:4`, `2:3`, `3:2`, `3:4`, `4:1`, `4:3`, `4:5`, `5:4`, `9:16`, `16:9`, `21:9` |

## `intro_related_work_plan`

### `introduction_strategy`

| Field | Type |
|---|---|
| `hook_hypothesis` | string |
| `problem_gap_hypothesis` | string |
| `search_directions` | array of strings (3–5) |

### `related_work_strategy`

| Field | Type |
|---|---|
| `overview` | string |
| `subsections` | array of cluster objects |

Each cluster:

| Field | Type |
|---|---|
| `subsection_title` | string |
| `methodology_cluster` | string |
| `sota_investigation_mission` | string |
| `limitation_hypothesis` | string |
| `limitation_search_queries` | array of strings |
| `bridge_to_our_method` | string |

## `section_plan[]`

```json
{
  "section_title": "3. Methodology",
  "subsections": [
    {
      "subsection_title": "3.1 Temporal-Aware Attention",
      "content_bullets": ["Define the query-key matching logic"],
      "citation_hints": ["Vaswani et al. (Attention Is All You Need)"]
    }
  ]
}
```

After the literature stage, every subsection gains `citation_candidates` (array of citation keys) and loses `citation_hints`. The writing stage expects `citation_candidates`.

## Minimal valid example

```json
{
  "plotting_plan": [
    {
      "figure_id": "fig_main_results",
      "title": "Main results",
      "plot_type": "plot",
      "data_source": "experimental_log.md",
      "objective": "Grouped bar chart comparing the method with three baselines on two datasets.",
      "aspect_ratio": "16:9"
    }
  ],
  "intro_related_work_plan": {
    "introduction_strategy": {
      "hook_hypothesis": "Sparse attention is the standard way to scale sequence models.",
      "problem_gap_hypothesis": "Existing sparse patterns are fixed before training and ignore input content.",
      "search_directions": [
        "Find papers establishing the cost of dense attention",
        "Find surveys of efficient attention",
        "Find foundational sparse-attention papers"
      ]
    },
    "related_work_strategy": {
      "overview": "Compare fixed, learned, and content-dependent sparsity.",
      "subsections": [
        {
          "subsection_title": "2.1 Fixed Sparse Patterns",
          "methodology_cluster": "Static sparsity",
          "sota_investigation_mission": "Identify the main fixed-pattern methods before the cutoff.",
          "limitation_hypothesis": "Fixed patterns cannot adapt to input content.",
          "limitation_search_queries": [
            "fixed sparse attention limitation content adaptivity",
            "static attention pattern generalization"
          ],
          "bridge_to_our_method": "A learned router selects the pattern per input."
        }
      ]
    }
  },
  "section_plan": [
    {
      "section_title": "Abstract",
      "subsections": [
        {
          "subsection_title": "Abstract Content",
          "content_bullets": ["State the problem", "Introduce the method", "Report the gain"],
          "citation_hints": []
        }
      ]
    },
    {
      "section_title": "3. Methodology",
      "subsections": [
        {
          "subsection_title": "3.1 Learned Routing",
          "content_bullets": ["Formalize the router", "Define the sparsity loss"],
          "citation_hints": ["research paper or technical report introducing 'Gumbel-Softmax'"]
        }
      ]
    }
  ]
}
```
