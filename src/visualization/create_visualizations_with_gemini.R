#!/usr/bin/env Rscript
#
# Create visualizations including Gemini data
#

library(dplyr)
library(ggplot2)
library(tidyr)
library(scales)
library(viridis)
library(readr)

cat("Loading intercoder reliability results...\n")

# Load data (preserve column names)
results_wide <- read_csv('results/outputs/intercoder_reliability_results_with_gemini.csv', show_col_types = FALSE)

# Remove Average row for individual code visualizations
results_no_avg <- results_wide %>%
  filter(Code != 'Average')

# Reshape to long format
results_long <- results_no_avg %>%
  pivot_longer(
    cols = -c(Code, `Gold Standard Count`),
    names_to = 'Model',
    values_to = 'Kappa'
  )

# =============================================================================
# VISUALIZATION 1: HEATMAP
# =============================================================================
cat("\nCreating Visualization 1: Heatmap of Cohen's Kappa by Code and Model...\n")

# Order models for consistent display
model_order <- c(
  'GPT-4: Per-Code w/ Just',
  'GPT-4: Per-Code w/o Just',
  'GPT-4: Full w/ Just',
  'GPT-4: Full w/o Just',
  'GPT-3.5: Per-Code w/ Just',
  'GPT-3.5: Per-Code w/o Just',
  'Gemini: Per-Code w/ Just',
  'Gemini: Full w/ Just',
  'Llama: Per-Code w/ Just'
)

results_long$Model <- factor(results_long$Model, levels = model_order)

p1 <- ggplot(results_long, aes(x = Model, y = Code, fill = Kappa)) +
  geom_tile(color = 'white', linewidth = 0.5) +
  scale_fill_viridis(
    option = 'plasma',
    name = "Cohen's\nKappa",
    limits = c(-0.2, 1),
    breaks = seq(-0.2, 1, 0.2)
  ) +
  geom_text(aes(label = sprintf('%.2f', Kappa)), color = 'white', size = 2.5, fontface = 'bold') +
  labs(
    title = "Cohen's Kappa by Code and Model Condition",
    subtitle = "Performance Across GPT-4, GPT-3.5, Gemini, and Llama Models",
    x = 'Model Condition',
    y = 'Code'
  ) +
  theme_minimal() +
  theme(
    plot.title = element_text(face = 'bold', size = 16, hjust = 0.5),
    plot.subtitle = element_text(size = 12, hjust = 0.5, margin = margin(b = 15)),
    axis.text.x = element_text(angle = 45, hjust = 1, size = 9),
    axis.text.y = element_text(size = 10),
    axis.title = element_text(face = 'bold', size = 12),
    legend.title = element_text(face = 'bold', size = 10),
    legend.text = element_text(size = 9),
    panel.grid = element_blank(),
    plot.margin = margin(20, 20, 20, 20)
  )

ggsave('results/figures/visualization1_heatmap_with_gemini.png', p1, width = 12, height = 8, dpi = 300)
cat("✓ Saved: results/figures/visualization1_heatmap_with_gemini.png\n")

# =============================================================================
# VISUALIZATION 2: AVERAGE PERFORMANCE
# =============================================================================
cat("\nCreating Visualization 2: Average Performance Across Codes...\n")

# Get average row
avg_row <- results_wide %>%
  filter(Code == 'Average') %>%
  pivot_longer(
    cols = -c(Code, `Gold Standard Count`),
    names_to = 'Model',
    values_to = 'Kappa'
  )

avg_row$Model <- factor(avg_row$Model, levels = model_order)

# Define colors for each model
model_colors <- c(
  'GPT-4: Per-Code w/ Just' = '#1f77b4',
  'GPT-4: Per-Code w/o Just' = '#ff7f0e',
  'GPT-4: Full w/ Just' = '#2ca02c',
  'GPT-4: Full w/o Just' = '#d62728',
  'GPT-3.5: Per-Code w/ Just' = '#9467bd',
  'GPT-3.5: Per-Code w/o Just' = '#8c564b',
  'Gemini: Per-Code w/ Just' = '#e377c2',
  'Gemini: Full w/ Just' = '#7f7f7f',
  'Llama: Per-Code w/ Just' = '#bcbd22'
)

p2 <- ggplot(avg_row, aes(x = Model, y = Kappa, fill = Model)) +
  geom_bar(stat = 'identity', width = 0.7) +
  geom_text(aes(label = sprintf('%.3f', Kappa)), vjust = ifelse(avg_row$Kappa >= 0, -0.5, 1.5), size = 3.5, fontface = 'bold') +
  scale_fill_manual(values = model_colors) +
  geom_hline(yintercept = 0, linetype = 'solid', color = 'black', linewidth = 0.5) +
  scale_y_continuous(
    limits = c(min(avg_row$Kappa) * 1.2, max(avg_row$Kappa) * 1.15),
    breaks = seq(-0.2, 1, 0.1)
  ) +
  labs(
    title = "Average Performance Across All Codes",
    subtitle = "Mean Cohen's Kappa by Model Condition (GPT-4, GPT-3.5, Gemini, and Llama)",
    x = 'Model Condition',
    y = "Average Cohen's Kappa"
  ) +
  theme_minimal() +
  theme(
    plot.title = element_text(face = 'bold', size = 16, hjust = 0.5),
    plot.subtitle = element_text(size = 12, hjust = 0.5, margin = margin(b = 15)),
    axis.text.x = element_text(angle = 45, hjust = 1, size = 9),
    axis.text.y = element_text(size = 10),
    axis.title = element_text(face = 'bold', size = 12),
    legend.position = 'none',
    panel.grid.major.x = element_blank(),
    panel.grid.minor.y = element_blank(),
    plot.margin = margin(20, 20, 20, 20)
  )

ggsave('results/figures/visualization2_average_performance_with_gemini.png', p2, width = 14, height = 7, dpi = 300)
cat("✓ Saved: results/figures/visualization2_average_performance_with_gemini.png\n")

# =============================================================================
# VISUALIZATION 3: CODE DIFFICULTY WITH MODEL COMPARISON
# =============================================================================
cat("\nCreating Visualization 3: Code Difficulty Across Models...\n")

# Get data for per-code, with-justification condition across models
comparison_data <- results_no_avg %>%
  select(Code,
         `GPT-4: Per-Code w/ Just`,
         `GPT-3.5: Per-Code w/ Just`,
         `Gemini: Per-Code w/ Just`,
         `Llama: Per-Code w/ Just`) %>%
  pivot_longer(
    cols = -Code,
    names_to = 'Model',
    values_to = 'Kappa'
  ) %>%
  mutate(Model = case_when(
    Model == 'GPT-4: Per-Code w/ Just' ~ 'GPT-4',
    Model == 'GPT-3.5: Per-Code w/ Just' ~ 'GPT-3.5',
    Model == 'Gemini: Per-Code w/ Just' ~ 'Gemini',
    Model == 'Llama: Per-Code w/ Just' ~ 'Llama'
  ))

# Calculate average performance per code for ordering
code_order_df <- comparison_data %>%
  group_by(Code) %>%
  summarize(mean_kappa = mean(Kappa, na.rm = TRUE)) %>%
  arrange(desc(mean_kappa))

comparison_data$Code <- factor(comparison_data$Code, levels = code_order_df$Code)
comparison_data$Model <- factor(comparison_data$Model, levels = c('GPT-4', 'GPT-3.5', 'Gemini', 'Llama'))

# Define model colors
model_colors_3 <- c(
  'GPT-4' = '#1f77b4',
  'GPT-3.5' = '#9467bd',
  'Gemini' = '#e377c2',
  'Llama' = '#bcbd22'
)

p3 <- ggplot(comparison_data, aes(x = Code, y = Kappa, fill = Model)) +
  geom_bar(stat = 'identity', position = position_dodge(width = 0.8), width = 0.7) +
  geom_hline(yintercept = 0, linetype = 'solid', color = 'black', linewidth = 0.5) +
  scale_fill_manual(values = model_colors_3) +
  scale_y_continuous(
    limits = c(min(comparison_data$Kappa) * 1.1, 1.05),
    breaks = seq(-0.2, 1, 0.2)
  ) +
  labs(
    title = "Code Difficulty: Model Performance Comparison",
    subtitle = "Per-Code with Justification Condition\nOrdered by Average Performance (Easiest to Hardest)",
    x = 'Code',
    y = "Cohen's Kappa",
    fill = 'Model'
  ) +
  coord_flip() +
  theme_minimal() +
  theme(
    plot.title = element_text(face = 'bold', size = 16, hjust = 0.5),
    plot.subtitle = element_text(size = 11, hjust = 0.5, margin = margin(b = 15)),
    axis.text.x = element_text(size = 10),
    axis.text.y = element_text(size = 10),
    axis.title = element_text(face = 'bold', size = 12),
    legend.title = element_text(face = 'bold', size = 11),
    legend.text = element_text(size = 10),
    legend.position = 'bottom',
    panel.grid.major.y = element_blank(),
    panel.grid.minor.x = element_blank(),
    plot.margin = margin(20, 20, 20, 20)
  )

ggsave('results/figures/visualization3_code_difficulty_with_gemini.png', p3, width = 12, height = 8, dpi = 300)
cat("✓ Saved: results/figures/visualization3_code_difficulty_with_gemini.png\n")

cat("\n================================================================================\n")
cat("ALL VISUALIZATIONS CREATED SUCCESSFULLY\n")
cat("================================================================================\n")
cat("\nFiles created:\n")
cat("  1. results/figures/visualization1_heatmap_with_gemini.png\n")
cat("  2. results/figures/visualization2_average_performance_with_gemini.png\n")
cat("  3. results/figures/visualization3_code_difficulty_with_gemini.png\n")
cat("  4. results/figures/concreteness_vs_performance_with_gemini.png (from Python script)\n")
cat("\n")
