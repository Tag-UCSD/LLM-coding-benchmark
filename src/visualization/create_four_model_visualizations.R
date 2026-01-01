#!/usr/bin/env Rscript
# Four-Model Comparison: GPT-4, GPT-3.5, Gemini, Qwen

library(tidyverse)
library(ggplot2)

# Create output directory if needed
dir.create("results/figures", showWarnings = FALSE, recursive = TRUE)

cat("Loading data...\n")

# Load all model results
gpt4_results <- read_csv(
  "results/raw/output_original/per-code-with-justification_t=0_top_p=1_model=gpt-4/processed_responses.csv",
  show_col_types = FALSE
)

gpt35_results <- read_csv(
  "results/raw/output_original/per-code-with-justification_t=0_top_p=1_model=gpt-3.5/processed_responses.csv",
  show_col_types = FALSE
)

gemini_results <- read_csv(
  "results/raw/output_gemini/per-code-with-justification_t=0_model=gemini/processed_responses.csv",
  show_col_types = FALSE
)

qwen_results <- read_csv(
  "results/raw/output_qwen/per-code-with-justification_t=0_model=qwen/processed_responses.csv",
  show_col_types = FALSE
)

gold_standard <- read_csv(
  "data/processed/gold_standard_coding.csv",
  show_col_types = FALSE
)

# Code columns
codes <- c(
  'Scholar', 'Activist', 'Monumental Memorialization',
  'Mention of Scholarly Work', 'Social/Political Advocacy',
  'Coalition Building', 'Out of the Mouth of Academics',
  'Out of the Mouth of Activists', 'Collective Synecdoche'
)

# Calculate Cohen's Kappa for each model
library(irr)

calculate_kappa <- function(model_data, gold_data, code_name) {
  # Filter to test set (IDs 9-119)
  test_ids <- 9:119

  model_filtered <- model_data %>% filter(id %in% test_ids) %>% arrange(id)
  gold_filtered <- gold_data %>% filter(id %in% test_ids) %>% arrange(id)

  # Create data frame for kappa calculation
  # CRITICAL: Convert NA to 0 in gold standard (NA means "not coded as 1")
  df <- data.frame(
    coder1 = replace(gold_filtered[[code_name]], is.na(gold_filtered[[code_name]]), 0),
    coder2 = replace(model_filtered[[code_name]], is.na(model_filtered[[code_name]]), 0)
  )

  kappa_result <- tryCatch(
    kappa2(df)$value,
    error = function(e) NA
  )

  # Calculate percent agreement
  agreement <- mean(df$coder1 == df$coder2, na.rm = TRUE)

  list(kappa = kappa_result, agreement = agreement)
}

# Calculate metrics for all models and codes
results_list <- list()

for (code in codes) {
  gpt4_metrics <- calculate_kappa(gpt4_results, gold_standard, code)
  gpt35_metrics <- calculate_kappa(gpt35_results, gold_standard, code)
  gemini_metrics <- calculate_kappa(gemini_results, gold_standard, code)
  qwen_metrics <- calculate_kappa(qwen_results, gold_standard, code)

  results_list[[length(results_list) + 1]] <- data.frame(
    Code = code,
    `GPT-4 Kappa` = gpt4_metrics$kappa,
    `GPT-3.5 Kappa` = gpt35_metrics$kappa,
    `Gemini Kappa` = gemini_metrics$kappa,
    `Qwen Kappa` = qwen_metrics$kappa,
    `GPT-4 Agreement` = gpt4_metrics$agreement,
    `GPT-3.5 Agreement` = gpt35_metrics$agreement,
    `Gemini Agreement` = gemini_metrics$agreement,
    `Qwen Agreement` = qwen_metrics$agreement,
    check.names = FALSE
  )
}

results_df <- bind_rows(results_list)

# Reshape for visualizations
kappa_long <- results_df %>%
  select(Code, ends_with("Kappa")) %>%
  pivot_longer(
    cols = ends_with("Kappa"),
    names_to = "Model",
    values_to = "Kappa"
  ) %>%
  mutate(Model = str_remove(Model, " Kappa"))

agreement_long <- results_df %>%
  select(Code, ends_with("Agreement")) %>%
  pivot_longer(
    cols = ends_with("Agreement"),
    names_to = "Model",
    values_to = "Agreement"
  ) %>%
  mutate(Model = str_remove(Model, " Agreement"))

# 1. Kappa by Code - All Models
cat("Creating kappa by code visualization...\n")
p1 <- ggplot(kappa_long, aes(x = reorder(Code, Kappa), y = Kappa, fill = Model)) +
  geom_bar(stat = "identity", position = "dodge", width = 0.7) +
  coord_flip() +
  theme_minimal() +
  labs(
    title = "Cohen's Kappa by Code: Four-Model Comparison",
    subtitle = "GPT-4, GPT-3.5, Gemini 2.5 Flash-Lite, and Qwen 2.5 72B (per-code with justification)",
    x = "Code",
    y = "Cohen's Kappa",
    fill = "Model"
  ) +
  scale_fill_manual(values = c(
    "GPT-4" = "#1f77b4",
    "GPT-3.5" = "#aec7e8",
    "Gemini" = "#ff7f0e",
    "Qwen" = "#d62728"
  )) +
  theme(
    plot.title = element_text(size = 14, face = "bold"),
    plot.subtitle = element_text(size = 10),
    legend.position = "bottom",
    axis.text.y = element_text(size = 9)
  )

ggsave("results/figures/four_model_kappa_by_code.png", p1, width = 12, height = 8, dpi = 300)
cat("✓ Saved: results/figures/four_model_kappa_by_code.png\n")

# 2. Average Performance Comparison
cat("Creating average performance comparison...\n")
avg_performance <- kappa_long %>%
  group_by(Model) %>%
  summarise(
    `Average Kappa` = mean(Kappa, na.rm = TRUE),
    .groups = 'drop'
  )

p2 <- ggplot(avg_performance, aes(x = reorder(Model, `Average Kappa`), y = `Average Kappa`, fill = Model)) +
  geom_bar(stat = "identity", width = 0.6) +
  geom_text(aes(label = sprintf("κ = %.3f", `Average Kappa`)), vjust = -0.5, size = 5) +
  theme_minimal() +
  labs(
    title = "Average Cohen's Kappa: Four-Model Comparison",
    subtitle = "Higher values indicate better agreement with gold standard",
    x = NULL,
    y = "Average Cohen's Kappa"
  ) +
  scale_fill_manual(values = c(
    "GPT-4" = "#1f77b4",
    "GPT-3.5" = "#aec7e8",
    "Gemini" = "#ff7f0e",
    "Qwen" = "#d62728"
  )) +
  theme(
    plot.title = element_text(size = 14, face = "bold"),
    plot.subtitle = element_text(size = 11),
    legend.position = "none",
    axis.text.x = element_text(size = 11)
  ) +
  ylim(0, max(avg_performance$`Average Kappa`) * 1.15)

ggsave("results/figures/four_model_average_kappa.png", p2, width = 8, height = 6, dpi = 300)
cat("✓ Saved: results/figures/four_model_average_kappa.png\n")

# 3. Performance Heatmap
cat("Creating performance heatmap...\n")
p3 <- ggplot(kappa_long, aes(x = Model, y = Code, fill = Kappa)) +
  geom_tile(color = "white", size = 1) +
  geom_text(aes(label = sprintf("%.2f", Kappa)), color = "white", size = 3.5, fontface = "bold") +
  scale_fill_gradient2(
    low = "#d73027",
    mid = "#fee08b",
    high = "#1a9850",
    midpoint = 0.5,
    limits = c(-0.1, 1),
    name = "Cohen's\nKappa"
  ) +
  theme_minimal() +
  labs(
    title = "Performance Heatmap: Four-Model Comparison",
    subtitle = "Cohen's Kappa by code and model",
    x = NULL,
    y = "Code"
  ) +
  theme(
    plot.title = element_text(size = 14, face = "bold"),
    plot.subtitle = element_text(size = 11),
    axis.text.x = element_text(size = 10),
    axis.text.y = element_text(size = 9),
    panel.grid = element_blank()
  )

ggsave("results/figures/four_model_heatmap.png", p3, width = 10, height = 8, dpi = 300)
cat("✓ Saved: results/figures/four_model_heatmap.png\n")

# 4. Difference from GPT-4 (Baseline)
cat("Creating GPT-4 baseline comparison...\n")
kappa_wide <- kappa_long %>%
  pivot_wider(names_from = Model, values_from = Kappa)

difference_data <- kappa_wide %>%
  mutate(
    `GPT-3.5 vs GPT-4` = `GPT-3.5` - `GPT-4`,
    `Gemini vs GPT-4` = Gemini - `GPT-4`,
    `Qwen vs GPT-4` = Qwen - `GPT-4`
  ) %>%
  select(Code, ends_with("vs GPT-4")) %>%
  pivot_longer(
    cols = ends_with("vs GPT-4"),
    names_to = "Comparison",
    values_to = "Difference"
  )

p4 <- ggplot(difference_data, aes(x = reorder(Code, Difference), y = Difference, fill = Comparison)) +
  geom_bar(stat = "identity", position = "dodge", width = 0.7) +
  geom_hline(yintercept = 0, linetype = "dashed", color = "gray30", size = 0.8) +
  coord_flip() +
  theme_minimal() +
  labs(
    title = "Model Performance Relative to GPT-4",
    subtitle = "Positive values = better than GPT-4, Negative values = worse than GPT-4",
    x = "Code",
    y = "Difference in Cohen's Kappa (vs GPT-4)",
    fill = "Comparison"
  ) +
  scale_fill_manual(
    values = c(
      "GPT-3.5 vs GPT-4" = "#aec7e8",
      "Gemini vs GPT-4" = "#ff7f0e",
      "Qwen vs GPT-4" = "#d62728"
    )
  ) +
  theme(
    plot.title = element_text(size = 14, face = "bold"),
    plot.subtitle = element_text(size = 10),
    legend.position = "bottom",
    axis.text.y = element_text(size = 9)
  )

ggsave("results/figures/four_model_vs_gpt4.png", p4, width = 12, height = 8, dpi = 300)
cat("✓ Saved: results/figures/four_model_vs_gpt4.png\n")

# 5. Percent Agreement Comparison
cat("Creating percent agreement comparison...\n")
p5 <- ggplot(agreement_long, aes(x = reorder(Code, Agreement), y = Agreement, fill = Model)) +
  geom_bar(stat = "identity", position = "dodge", width = 0.7) +
  coord_flip() +
  theme_minimal() +
  labs(
    title = "Percent Agreement by Code: Four-Model Comparison",
    subtitle = "Simple agreement percentage with gold standard",
    x = "Code",
    y = "Percent Agreement",
    fill = "Model"
  ) +
  scale_fill_manual(values = c(
    "GPT-4" = "#1f77b4",
    "GPT-3.5" = "#aec7e8",
    "Gemini" = "#ff7f0e",
    "Qwen" = "#d62728"
  )) +
  scale_y_continuous(labels = scales::percent_format(scale = 100), limits = c(0, 1)) +
  theme(
    plot.title = element_text(size = 14, face = "bold"),
    plot.subtitle = element_text(size = 11),
    legend.position = "bottom",
    axis.text.y = element_text(size = 9)
  )

ggsave("results/figures/four_model_percent_agreement.png", p5, width = 12, height = 8, dpi = 300)
cat("✓ Saved: results/figures/four_model_percent_agreement.png\n")

# Print summary
cat("\n", rep("=", 80), "\n", sep = "")
cat("FOUR-MODEL COMPARISON SUMMARY\n")
cat(rep("=", 80), "\n", sep = "")
cat("\nAverage Performance:\n")
print(avg_performance %>% arrange(desc(`Average Kappa`)))

cat("\nModel Rankings by Code:\n")
best_model_by_code <- kappa_long %>%
  group_by(Code) %>%
  slice_max(Kappa, n = 1) %>%
  ungroup() %>%
  select(Code, Model, Kappa)
print(best_model_by_code)

cat("\n✓ Created 5 visualizations comparing all four models\n")
cat("✓ All figures saved to results/figures/\n")

# Save summary results
write_csv(results_df, "results/outputs/four_model_comparison.csv")
cat("✓ Saved detailed results to: results/outputs/four_model_comparison.csv\n")
