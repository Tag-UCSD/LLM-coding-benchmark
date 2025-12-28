#!/usr/bin/env Rscript
#
# Create original three visualizations (heatmap, average performance, code difficulty)
#

library(dplyr)
library(ggplot2)
library(tidyr)
library(scales)
library(viridis)

cat("Loading intercoder reliability results...\n")

# Load data
results_wide <- read.csv('results/outputs/intercoder_reliability_results.csv')

# Remove Average row for individual code visualizations
results_no_avg <- results_wide %>%
  filter(Code != 'Average')

# Reshape to long format
results_long <- results_no_avg %>%
  pivot_longer(
    cols = -c(Code, Gold.Standard.Count),
    names_to = 'Model',
    values_to = 'Kappa'
  )

# Clean up model names
results_long <- results_long %>%
  mutate(Model = gsub('\\.', ' ', Model))

# =============================================================================
# VISUALIZATION 1: HEATMAP
# =============================================================================
cat("\nCreating Visualization 1: Heatmap of Cohen's Kappa by Code and Model...\n")

# Order models for consistent display
model_order <- c(
  'Per Code w/ Justification',
  'Per Code w/out Justification',
  'Full w/ Justification',
  'Full w/out Justification',
  'GPT 3 5 w/ Justification',
  'GPT 3 5 w/out Justification'
)

results_long$Model <- factor(results_long$Model, levels = model_order)

p1 <- ggplot(results_long, aes(x = Model, y = Code, fill = Kappa)) +
  geom_tile(color = 'white', linewidth = 0.5) +
  scale_fill_viridis(
    option = 'plasma',
    name = "Cohen's\nKappa",
    limits = c(0, 1),
    breaks = seq(0, 1, 0.2)
  ) +
  geom_text(aes(label = sprintf('%.2f', Kappa)), color = 'white', size = 3, fontface = 'bold') +
  labs(
    title = "Cohen's Kappa by Code and Model Condition",
    subtitle = "GPT-4 Performance Across Different Prompting Strategies",
    x = 'Model Condition',
    y = 'Code'
  ) +
  theme_minimal() +
  theme(
    plot.title = element_text(face = 'bold', size = 16, hjust = 0.5),
    plot.subtitle = element_text(size = 12, hjust = 0.5, margin = margin(b = 15)),
    axis.text.x = element_text(angle = 45, hjust = 1, size = 10),
    axis.text.y = element_text(size = 10),
    axis.title = element_text(face = 'bold', size = 12),
    legend.title = element_text(face = 'bold', size = 10),
    legend.text = element_text(size = 9),
    panel.grid = element_blank(),
    plot.margin = margin(20, 20, 20, 20)
  )

ggsave('results/figures/visualization1_heatmap_R.png', p1, width = 12, height = 8, dpi = 300)
cat("✓ Saved: results/figures/visualization1_heatmap_R.png\n")

# =============================================================================
# VISUALIZATION 2: AVERAGE PERFORMANCE
# =============================================================================
cat("\nCreating Visualization 2: Average Performance Across Codes...\n")

# Get average row
avg_row <- results_wide %>%
  filter(Code == 'Average') %>%
  pivot_longer(
    cols = -c(Code, Gold.Standard.Count),
    names_to = 'Model',
    values_to = 'Kappa'
  ) %>%
  mutate(Model = gsub('\\.', ' ', Model))

avg_row$Model <- factor(avg_row$Model, levels = model_order)

# Define colors for each model
model_colors <- c(
  'Per Code w/ Justification' = '#1f77b4',
  'Per Code w/out Justification' = '#ff7f0e',
  'Full w/ Justification' = '#2ca02c',
  'Full w/out Justification' = '#d62728',
  'GPT 3 5 w/ Justification' = '#9467bd',
  'GPT 3 5 w/out Justification' = '#8c564b'
)

p2 <- ggplot(avg_row, aes(x = Model, y = Kappa, fill = Model)) +
  geom_bar(stat = 'identity', width = 0.7) +
  geom_text(aes(label = sprintf('%.3f', Kappa)), vjust = -0.5, size = 4, fontface = 'bold') +
  scale_fill_manual(values = model_colors) +
  scale_y_continuous(
    limits = c(0, max(avg_row$Kappa) * 1.15),
    breaks = seq(0, 1, 0.1),
    expand = c(0, 0)
  ) +
  labs(
    title = "Average Performance Across All Codes",
    subtitle = "Mean Cohen's Kappa by Model Condition",
    x = 'Model Condition',
    y = "Average Cohen's Kappa"
  ) +
  theme_minimal() +
  theme(
    plot.title = element_text(face = 'bold', size = 16, hjust = 0.5),
    plot.subtitle = element_text(size = 12, hjust = 0.5, margin = margin(b = 15)),
    axis.text.x = element_text(angle = 45, hjust = 1, size = 10),
    axis.text.y = element_text(size = 10),
    axis.title = element_text(face = 'bold', size = 12),
    legend.position = 'none',
    panel.grid.major.x = element_blank(),
    panel.grid.minor.y = element_blank(),
    plot.margin = margin(20, 20, 20, 20)
  )

ggsave('results/figures/visualization2_average_performance_R.png', p2, width = 12, height = 7, dpi = 300)
cat("✓ Saved: results/figures/visualization2_average_performance_R.png\n")

# =============================================================================
# VISUALIZATION 3: CODE DIFFICULTY
# =============================================================================
cat("\nCreating Visualization 3: Code Difficulty (Best Model)...\n")

# Get best model performance for each code
best_model_data <- results_no_avg %>%
  select(Code, `Per.Code.w..Justification`) %>%
  rename(Kappa = `Per.Code.w..Justification`) %>%
  arrange(desc(Kappa))

# Set factor order for bars
best_model_data$Code <- factor(best_model_data$Code, levels = best_model_data$Code)

# Color gradient based on difficulty (lower kappa = harder = red, higher kappa = easier = green)
p3 <- ggplot(best_model_data, aes(x = Code, y = Kappa, fill = Kappa)) +
  geom_bar(stat = 'identity', width = 0.7) +
  geom_text(aes(label = sprintf('%.3f', Kappa)), hjust = -0.1, size = 3.5, fontface = 'bold') +
  scale_fill_viridis(
    option = 'viridis',
    name = "Cohen's\nKappa",
    direction = 1,
    limits = c(0, 1)
  ) +
  scale_y_continuous(
    limits = c(0, 1.1),
    breaks = seq(0, 1, 0.2),
    expand = c(0, 0)
  ) +
  labs(
    title = "Code Difficulty: GPT-4 Performance by Code",
    subtitle = "Per-Code with Justification (Best Performing Condition)\nOrdered by Performance (Easiest to Hardest)",
    x = 'Code',
    y = "Cohen's Kappa"
  ) +
  coord_flip() +
  theme_minimal() +
  theme(
    plot.title = element_text(face = 'bold', size = 16, hjust = 0.5),
    plot.subtitle = element_text(size = 11, hjust = 0.5, margin = margin(b = 15)),
    axis.text.x = element_text(size = 10),
    axis.text.y = element_text(size = 10),
    axis.title = element_text(face = 'bold', size = 12),
    legend.title = element_text(face = 'bold', size = 10),
    legend.text = element_text(size = 9),
    panel.grid.major.y = element_blank(),
    panel.grid.minor.x = element_blank(),
    plot.margin = margin(20, 20, 20, 20)
  )

ggsave('results/figures/visualization3_code_difficulty_R.png', p3, width = 10, height = 8, dpi = 300)
cat("✓ Saved: results/figures/visualization3_code_difficulty_R.png\n")

cat("\n================================================================================\n")
cat("ALL VISUALIZATIONS CREATED SUCCESSFULLY\n")
cat("================================================================================\n")
cat("\nFiles created:\n")
cat("  1. results/figures/visualization1_heatmap_R.png\n")
cat("  2. results/figures/visualization2_average_performance_R.png\n")
cat("  3. results/figures/visualization3_code_difficulty_R.png\n")
cat("  4. results/figures/concreteness_vs_performance_R.png (from previous script)\n")
cat("\n")
