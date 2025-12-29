#!/usr/bin/env Rscript
# Four-way comparison: GPT-4 vs Gemini vs Llama vs Qwen

library(tidyverse)
library(ggplot2)

# Read comparison data (per-code, with justification)
gpt4_results <- read_csv("results/outputs/per-code-with-justification_gpt4_detailed_report.csv", show_col_types = FALSE) %>%
  select(Code, `% Agreement`, Kappa, Alpha, `Gwets AC1`) %>%
  mutate(Model = "GPT-4")

gemini_comparison <- read_csv("results/outputs/gemini-per-code-with-justification_detailed_report.csv", show_col_types = FALSE) %>%
  select(Code, `% Agreement`, Kappa, Alpha, `Gwets AC1`) %>%
  mutate(Model = "Gemini 2.5 Flash-Lite")

llama_comparison <- read_csv("results/outputs/llama-per-code-with-justification_detailed_report.csv", show_col_types = FALSE) %>%
  select(Code, `% Agreement`, Kappa, Alpha, `Gwets AC1`) %>%
  mutate(Model = "Llama 3.3 70B")

qwen_comparison <- read_csv("results/outputs/qwen_vs_gold_standard.csv", show_col_types = FALSE) %>%
  select(Code, `% Agreement`, Kappa, Alpha, `Gwets AC1`) %>%
  mutate(Model = "Qwen 2.5 72B")

# Combine all models
all_models <- bind_rows(
  gpt4_results %>% select(Code, Kappa, `% Agreement`, Model),
  gemini_comparison,
  llama_comparison,
  qwen_comparison
)

# 1. Four-way Kappa comparison by code
p1 <- ggplot(all_models, aes(x = reorder(Code, Kappa), y = Kappa, fill = Model)) +
  geom_bar(stat = "identity", position = "dodge") +
  coord_flip() +
  theme_minimal() +
  labs(
    title = "Cohen's Kappa by Code: Four-Model Comparison",
    subtitle = "Comparing GPT-4, Gemini 2.5 Flash-Lite, Llama 3.3 70B, and Qwen 2.5 72B",
    x = "Code",
    y = "Cohen's Kappa",
    fill = "Model"
  ) +
  scale_fill_manual(values = c(
    "GPT-4" = "#1f77b4",
    "Gemini 2.5 Flash-Lite" = "#ff7f0e",
    "Llama 3.3 70B" = "#2ca02c",
    "Qwen 2.5 72B" = "#d62728"
  )) +
  theme(
    plot.title = element_text(size = 14, face = "bold"),
    plot.subtitle = element_text(size = 11),
    legend.position = "bottom"
  )

ggsave("results/figures/fourway_kappa_by_code.png", p1, width = 12, height = 6, dpi = 300)
cat("✓ Saved: results/figures/fourway_kappa_by_code.png\n")

# 2. Average performance comparison
avg_performance <- all_models %>%
  group_by(Model) %>%
  summarise(
    `Average Kappa` = mean(Kappa, na.rm = TRUE),
    `Average % Agreement` = mean(`% Agreement`, na.rm = TRUE)
  )

p2 <- ggplot(avg_performance, aes(x = reorder(Model, `Average Kappa`), y = `Average Kappa`, fill = Model)) +
  geom_bar(stat = "identity") +
  geom_text(aes(label = sprintf("%.3f", `Average Kappa`)), vjust = -0.5) +
  theme_minimal() +
  labs(
    title = "Average Cohen's Kappa: Four-Model Comparison",
    subtitle = "Higher is better (per-code with justification approach)",
    x = "Model",
    y = "Average Cohen's Kappa"
  ) +
  scale_fill_manual(values = c(
    "GPT-4" = "#1f77b4",
    "Gemini 2.5 Flash-Lite" = "#ff7f0e",
    "Llama 3.3 70B" = "#2ca02c",
    "Qwen 2.5 72B" = "#d62728"
  )) +
  theme(
    plot.title = element_text(size = 14, face = "bold"),
    plot.subtitle = element_text(size = 11),
    legend.position = "none",
    axis.text.x = element_text(angle = 45, hjust = 1)
  ) +
  ylim(0, max(avg_performance$`Average Kappa`) * 1.1)

ggsave("results/figures/fourway_average_kappa.png", p2, width = 8, height = 6, dpi = 300)
cat("✓ Saved: results/figures/fourway_average_kappa.png\n")

# 3. Heatmap comparison
heatmap_data <- all_models %>%
  select(Code, Model, Kappa) %>%
  pivot_wider(names_from = Model, values_from = Kappa) %>%
  pivot_longer(-Code, names_to = "Model", values_to = "Kappa")

p3 <- ggplot(heatmap_data, aes(x = Model, y = Code, fill = Kappa)) +
  geom_tile(color = "white") +
  geom_text(aes(label = sprintf("%.2f", Kappa)), color = "white", size = 3) +
  scale_fill_gradient2(
    low = "#d73027",
    mid = "#fee08b",
    high = "#1a9850",
    midpoint = 0.5,
    limits = c(0, 1),
    name = "Cohen's\nKappa"
  ) +
  theme_minimal() +
  labs(
    title = "Four-Model Performance Heatmap",
    subtitle = "Cohen's Kappa by code and model",
    x = "Model",
    y = "Code"
  ) +
  theme(
    plot.title = element_text(size = 14, face = "bold"),
    plot.subtitle = element_text(size = 11),
    axis.text.x = element_text(angle = 45, hjust = 1),
    panel.grid = element_blank()
  )

ggsave("results/figures/fourway_heatmap.png", p3, width = 12, height = 8, dpi = 300)
cat("✓ Saved: results/figures/fourway_heatmap.png\n")

# 4. Difference from GPT-4
difference_data <- all_models %>%
  select(Code, Model, Kappa) %>%
  pivot_wider(names_from = Model, values_from = Kappa) %>%
  mutate(
    `Gemini Diff` = `Gemini 2.5 Flash-Lite` - `GPT-4`,
    `Llama Diff` = `Llama 3.3 70B` - `GPT-4`,
    `Qwen Diff` = `Qwen 2.5 72B` - `GPT-4`
  ) %>%
  select(Code, `Gemini Diff`, `Llama Diff`, `Qwen Diff`) %>%
  pivot_longer(-Code, names_to = "Comparison", values_to = "Difference")

p4 <- ggplot(difference_data, aes(x = reorder(Code, Difference), y = Difference, fill = Comparison)) +
  geom_bar(stat = "identity", position = "dodge") +
  geom_hline(yintercept = 0, linetype = "dashed", color = "gray50") +
  coord_flip() +
  theme_minimal() +
  labs(
    title = "Model Performance Relative to GPT-4",
    subtitle = "Positive values indicate better performance than GPT-4",
    x = "Code",
    y = "Difference in Cohen's Kappa",
    fill = "Model"
  ) +
  scale_fill_manual(
    values = c(
      "Gemini Diff" = "#ff7f0e",
      "Llama Diff" = "#2ca02c",
      "Qwen Diff" = "#d62728"
    ),
    labels = c(
      "Gemini Diff" = "Gemini vs GPT-4",
      "Llama Diff" = "Llama vs GPT-4",
      "Qwen Diff" = "Qwen vs GPT-4"
    )
  ) +
  theme(
    plot.title = element_text(size = 14, face = "bold"),
    plot.subtitle = element_text(size = 11),
    legend.position = "bottom"
  )

ggsave("results/figures/fourway_difference_from_gpt4.png", p4, width = 12, height = 6, dpi = 300)
cat("✓ Saved: results/figures/fourway_difference_from_gpt4.png\n")

# Print summary statistics
cat("\n" , rep("=", 80), "\n", sep = "")
cat("FOUR-WAY COMPARISON SUMMARY\n")
cat(rep("=", 80), "\n", sep = "")
cat("\nAverage Cohen's Kappa:\n")
print(avg_performance)

cat("\n✓ Created 4 four-way comparison visualizations\n")
