#!/usr/bin/env Rscript
# Qwen vs Gemini Comparison Visualizations

library(tidyverse)
library(ggplot2)

# Create output directory if needed
dir.create("results/figures", showWarnings = FALSE, recursive = TRUE)

# Read data
qwen_results <- read_csv("results/outputs/qwen_vs_gold_standard.csv", show_col_types = FALSE) %>%
  select(Code, `% Agreement`, Kappa, Alpha, `Gwets AC1`) %>%
  mutate(Model = "Qwen 2.5 72B")

gemini_results <- read_csv("results/raw/output_gemini/per-code-with-justification_t=0_model=gemini/detailed_report.csv", show_col_types = FALSE) %>%
  select(Code, `% Agreement`, Kappa, Alpha, `Gwets AC1`) %>%
  mutate(Model = "Gemini 2.5 Flash-Lite")

# Combine both models
all_models <- bind_rows(qwen_results, gemini_results)

# 1. Kappa comparison by code
p1 <- ggplot(all_models, aes(x = reorder(Code, Kappa), y = Kappa, fill = Model)) +
  geom_bar(stat = "identity", position = "dodge", width = 0.7) +
  coord_flip() +
  theme_minimal() +
  labs(
    title = "Cohen's Kappa by Code: Qwen vs Gemini",
    subtitle = "Intercoder reliability with gold standard (test set IDs 9-119)",
    x = "Code",
    y = "Cohen's Kappa",
    fill = "Model"
  ) +
  scale_fill_manual(values = c(
    "Qwen 2.5 72B" = "#d62728",
    "Gemini 2.5 Flash-Lite" = "#ff7f0e"
  )) +
  theme(
    plot.title = element_text(size = 14, face = "bold"),
    plot.subtitle = element_text(size = 11),
    legend.position = "bottom"
  )

ggsave("results/figures/qwen_gemini_kappa_by_code.png", p1, width = 10, height = 6, dpi = 300)
cat("✓ Saved: results/figures/qwen_gemini_kappa_by_code.png\n")

# 2. Average performance comparison
avg_performance <- all_models %>%
  group_by(Model) %>%
  summarise(
    `Average Kappa` = mean(Kappa, na.rm = TRUE),
    `Average % Agreement` = mean(`% Agreement`, na.rm = TRUE),
    .groups = 'drop'
  )

p2 <- ggplot(avg_performance, aes(x = Model, y = `Average Kappa`, fill = Model)) +
  geom_bar(stat = "identity", width = 0.6) +
  geom_text(aes(label = sprintf("κ = %.3f", `Average Kappa`)), vjust = -0.5, size = 5) +
  theme_minimal() +
  labs(
    title = "Average Cohen's Kappa: Qwen vs Gemini",
    subtitle = "Per-code with justification approach",
    x = NULL,
    y = "Average Cohen's Kappa"
  ) +
  scale_fill_manual(values = c(
    "Qwen 2.5 72B" = "#d62728",
    "Gemini 2.5 Flash-Lite" = "#ff7f0e"
  )) +
  theme(
    plot.title = element_text(size = 14, face = "bold"),
    plot.subtitle = element_text(size = 11),
    legend.position = "none",
    axis.text.x = element_text(size = 11)
  ) +
  ylim(0, max(avg_performance$`Average Kappa`) * 1.15)

ggsave("results/figures/qwen_gemini_average_kappa.png", p2, width = 8, height = 6, dpi = 300)
cat("✓ Saved: results/figures/qwen_gemini_average_kappa.png\n")

# 3. Heatmap comparison
p3 <- ggplot(all_models, aes(x = Model, y = Code, fill = Kappa)) +
  geom_tile(color = "white", size = 1) +
  geom_text(aes(label = sprintf("%.2f", Kappa)), color = "white", size = 4, fontface = "bold") +
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
    title = "Performance Heatmap: Qwen vs Gemini",
    subtitle = "Cohen's Kappa by code and model",
    x = NULL,
    y = "Code"
  ) +
  theme(
    plot.title = element_text(size = 14, face = "bold"),
    plot.subtitle = element_text(size = 11),
    axis.text.x = element_text(size = 11),
    panel.grid = element_blank()
  )

ggsave("results/figures/qwen_gemini_heatmap.png", p3, width = 8, height = 8, dpi = 300)
cat("✓ Saved: results/figures/qwen_gemini_heatmap.png\n")

# 4. Direct comparison (side-by-side)
comparison_data <- all_models %>%
  select(Code, Model, Kappa) %>%
  pivot_wider(names_from = Model, values_from = Kappa) %>%
  mutate(
    Difference = `Qwen 2.5 72B` - `Gemini 2.5 Flash-Lite`,
    Winner = ifelse(Difference > 0, "Qwen", ifelse(Difference < 0, "Gemini", "Tie"))
  )

p4 <- ggplot(comparison_data, aes(x = reorder(Code, abs(Difference)), y = Difference, fill = Winner)) +
  geom_bar(stat = "identity") +
  geom_hline(yintercept = 0, linetype = "dashed", color = "gray30", size = 0.8) +
  coord_flip() +
  theme_minimal() +
  labs(
    title = "Qwen vs Gemini: Code-by-Code Differences",
    subtitle = "Positive values = Qwen better, Negative values = Gemini better",
    x = "Code",
    y = "Difference in Cohen's Kappa (Qwen - Gemini)",
    fill = "Better Model"
  ) +
  scale_fill_manual(
    values = c(
      "Qwen" = "#d62728",
      "Gemini" = "#ff7f0e",
      "Tie" = "#7f7f7f"
    )
  ) +
  theme(
    plot.title = element_text(size = 14, face = "bold"),
    plot.subtitle = element_text(size = 11),
    legend.position = "bottom"
  )

ggsave("results/figures/qwen_gemini_differences.png", p4, width = 10, height = 6, dpi = 300)
cat("✓ Saved: results/figures/qwen_gemini_differences.png\n")

# 5. Percent Agreement comparison
p5 <- ggplot(all_models, aes(x = reorder(Code, `% Agreement`), y = `% Agreement`, fill = Model)) +
  geom_bar(stat = "identity", position = "dodge", width = 0.7) +
  coord_flip() +
  theme_minimal() +
  labs(
    title = "Percent Agreement by Code: Qwen vs Gemini",
    subtitle = "Simple agreement percentage with gold standard",
    x = "Code",
    y = "Percent Agreement",
    fill = "Model"
  ) +
  scale_fill_manual(values = c(
    "Qwen 2.5 72B" = "#d62728",
    "Gemini 2.5 Flash-Lite" = "#ff7f0e"
  )) +
  scale_y_continuous(labels = scales::percent_format(scale = 1)) +
  theme(
    plot.title = element_text(size = 14, face = "bold"),
    plot.subtitle = element_text(size = 11),
    legend.position = "bottom"
  )

ggsave("results/figures/qwen_gemini_percent_agreement.png", p5, width = 10, height = 6, dpi = 300)
cat("✓ Saved: results/figures/qwen_gemini_percent_agreement.png\n")

# Print summary statistics
cat("\n", rep("=", 80), "\n", sep = "")
cat("QWEN vs GEMINI COMPARISON SUMMARY\n")
cat(rep("=", 80), "\n", sep = "")
cat("\nAverage Performance:\n")
print(avg_performance)

cat("\nCode-by-Code Winners:\n")
winners_summary <- comparison_data %>%
  count(Winner) %>%
  arrange(desc(n))
print(winners_summary)

cat("\nLargest Differences:\n")
largest_diffs <- comparison_data %>%
  arrange(desc(abs(Difference))) %>%
  select(Code, `Qwen 2.5 72B`, `Gemini 2.5 Flash-Lite`, Difference, Winner) %>%
  head(5)
print(largest_diffs)

cat("\n✓ Created 5 visualizations comparing Qwen and Gemini\n")
cat("✓ All figures saved to results/figures/\n")
