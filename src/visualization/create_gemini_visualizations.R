# Visualizations comparing Gemini vs GPT performance
# For "Scalable Qualitative Coding with LLMs" Replication

library(ggplot2)
library(tidyr)
library(dplyr)
library(scales)

# Set working directory to repository root
get_script_path <- function() {
  cmd_args <- commandArgs(trailingOnly = FALSE)
  file_arg <- grep("^--file=", cmd_args, value = TRUE)
  if (length(file_arg) == 0) {
    return(NULL)
  }
  sub("^--file=", "", file_arg[1])
}

script_path <- get_script_path()
if (!is.null(script_path)) {
  repo_root <- normalizePath(file.path(dirname(script_path), "..", ".."))
  setwd(repo_root)
}

# Read the comparison results
if (!file.exists("results/outputs/gemini_vs_gpt_comparison.csv")) {
  stop("Comparison file not found. Please run analyze_gemini_results.py first.")
}

results <- read.csv("results/outputs/gemini_vs_gpt_comparison.csv", stringsAsFactors = FALSE)

# Remove the average row for the main visualizations
results_no_avg <- results %>% filter(Code != "Average")
avg_row <- results %>% filter(Code == "Average")

# ============================================================================
# VISUALIZATION 1: Comparison of model performance across conditions
# ============================================================================

# Get column names for models (exclude 'Code')
model_cols <- setdiff(names(results_no_avg), "Code")

# Reshape data
results_long <- results_no_avg %>%
  pivot_longer(cols = -Code, names_to = "Condition", values_to = "Kappa")

# Categorize by model
results_long <- results_long %>%
  mutate(Model = case_when(
    grepl("Gemini", Condition) ~ "Gemini",
    grepl("GPT-4", Condition) ~ "GPT-4",
    grepl("GPT-3.5", Condition) ~ "GPT-3.5",
    TRUE ~ "Other"
  ))

# Create grouped bar plot
p1 <- ggplot(results_long, aes(x = Code, y = Kappa, fill = Condition)) +
  geom_bar(stat = "identity", position = position_dodge(width = 0.8), width = 0.7) +
  scale_fill_brewer(palette = "Set2") +
  theme_minimal() +
  theme(axis.text.x = element_text(angle = 45, hjust = 1, size = 8),
        legend.position = "bottom",
        legend.title = element_blank(),
        plot.title = element_text(size = 14, face = "bold")) +
  labs(title = "Gemini vs GPT: Cohen's Kappa by Code",
       subtitle = "Comparison across all experimental conditions",
       x = "Qualitative Code",
       y = "Cohen's Kappa") +
  guides(fill = guide_legend(nrow = 3))

ggsave("results/figures/gemini_comparison_by_code.png", p1, width = 14, height = 8, dpi = 300)
cat("Created: results/figures/gemini_comparison_by_code.png\n")

# ============================================================================
# VISUALIZATION 2: Average performance comparison (Gemini vs GPT)
# ============================================================================

# Extract averages
avg_long <- avg_row %>%
  select(-Code) %>%
  pivot_longer(cols = everything(), names_to = "Condition", values_to = "Avg_Kappa")

# Add model category
avg_long <- avg_long %>%
  mutate(Model = case_when(
    grepl("Gemini", Condition) ~ "Gemini 1.5 Pro",
    grepl("GPT-4", Condition) ~ "GPT-4",
    grepl("GPT-3.5", Condition) ~ "GPT-3.5",
    TRUE ~ "Other"
  ))

# Sort by performance
avg_long$Condition <- factor(avg_long$Condition,
                             levels = avg_long$Condition[order(-avg_long$Avg_Kappa)])

p2 <- ggplot(avg_long, aes(x = Condition, y = Avg_Kappa, fill = Model)) +
  geom_bar(stat = "identity") +
  geom_text(aes(label = sprintf("%.3f", Avg_Kappa)), vjust = -0.5, size = 3.5) +
  scale_fill_manual(values = c("Gemini 1.5 Pro" = "#34A853",
                               "GPT-4" = "#377eb8",
                               "GPT-3.5" = "#e41a1c")) +
  scale_y_continuous(limits = c(0, 0.75), breaks = seq(0, 0.75, 0.1)) +
  theme_minimal() +
  theme(axis.text.x = element_text(angle = 45, hjust = 1, size = 9),
        plot.title = element_text(size = 14, face = "bold"),
        legend.position = "top") +
  labs(title = "Average Performance: Gemini vs GPT",
       subtitle = "Mean Cohen's Kappa across all codes",
       x = "Condition",
       y = "Average Cohen's Kappa",
       fill = "Model")

ggsave("results/figures/gemini_average_comparison.png", p2, width = 12, height = 7, dpi = 300)
cat("Created: results/figures/gemini_average_comparison.png\n")

# ============================================================================
# VISUALIZATION 3: Difference plot (Gemini vs GPT-4 best condition)
# ============================================================================

# Find best GPT-4 and Gemini conditions for each code
if (any(grepl("Gemini", names(results_no_avg))) && any(grepl("GPT-4", names(results_no_avg)))) {

  gemini_cols <- grep("Gemini", names(results_no_avg), value = TRUE)
  gpt4_cols <- grep("GPT-4", names(results_no_avg), value = TRUE)

  if (length(gemini_cols) > 0 && length(gpt4_cols) > 0) {
    # Get best performance for each model
    results_no_avg$Gemini_Best <- apply(results_no_avg[, gemini_cols, drop = FALSE], 1, max, na.rm = TRUE)
    results_no_avg$GPT4_Best <- apply(results_no_avg[, gpt4_cols, drop = FALSE], 1, max, na.rm = TRUE)
    results_no_avg$Difference <- results_no_avg$Gemini_Best - results_no_avg$GPT4_Best

    # Sort by difference
    results_no_avg <- results_no_avg %>% arrange(Difference)
    results_no_avg$Code <- factor(results_no_avg$Code, levels = results_no_avg$Code)

    p3 <- ggplot(results_no_avg, aes(x = Code, y = Difference, fill = Difference > 0)) +
      geom_bar(stat = "identity") +
      geom_hline(yintercept = 0, linetype = "solid", color = "black") +
      scale_fill_manual(values = c("TRUE" = "#34A853", "FALSE" = "#EA4335"),
                        labels = c("GPT-4 Better", "Gemini Better"),
                        name = "") +
      theme_minimal() +
      theme(axis.text.x = element_text(angle = 45, hjust = 1, size = 9),
            plot.title = element_text(size = 14, face = "bold"),
            legend.position = "top") +
      labs(title = "Gemini vs GPT-4: Performance Difference by Code",
           subtitle = "Difference in Cohen's Kappa (Best condition for each model)",
           x = "Qualitative Code",
           y = "Kappa Difference (Gemini - GPT-4)") +
      coord_flip()

    ggsave("results/figures/gemini_gpt4_difference.png", p3, width = 10, height = 7, dpi = 300)
    cat("Created: results/figures/gemini_gpt4_difference.png\n")
  }
}

# ============================================================================
# VISUALIZATION 4: Heatmap comparison
# ============================================================================

# Create heatmap with just key conditions
key_conditions <- c(
  grep("Gemini.*Per.*Just", names(results_no_avg), value = TRUE),
  grep("GPT-4.*Per.*Just", names(results_no_avg), value = TRUE)
)

if (length(key_conditions) > 0) {
  heatmap_data <- results_no_avg %>%
    select(Code, all_of(key_conditions)) %>%
    pivot_longer(cols = -Code, names_to = "Condition", values_to = "Kappa")

  # Clean condition names
  heatmap_data$Condition <- gsub("GPT-4 ", "GPT-4\n", heatmap_data$Condition)
  heatmap_data$Condition <- gsub("Gemini ", "Gemini\n", heatmap_data$Condition)

  p4 <- ggplot(heatmap_data, aes(x = Condition, y = Code, fill = Kappa)) +
    geom_tile(color = "white", size = 1) +
    geom_text(aes(label = sprintf("%.2f", Kappa)), size = 3.5, fontface = "bold") +
    scale_fill_gradient2(low = "#d73027", mid = "#fee08b", high = "#1a9850",
                         midpoint = 0.5, limits = c(0, 1),
                         name = "Cohen's\nKappa") +
    theme_minimal() +
    theme(axis.text.x = element_text(angle = 0, hjust = 0.5, size = 9),
          axis.text.y = element_text(size = 9),
          plot.title = element_text(size = 14, face = "bold"),
          legend.position = "right") +
    labs(title = "Gemini vs GPT-4: Per-Code with Justification",
           subtitle = "Direct comparison of best-performing approach",
           x = "Model Condition",
           y = "Qualitative Code")

  ggsave("results/figures/gemini_gpt4_heatmap.png", p4, width = 10, height = 8, dpi = 300)
  cat("Created: results/figures/gemini_gpt4_heatmap.png\n")
}

# ============================================================================
# Print summary statistics
# ============================================================================

cat("\n")
cat(paste(rep("=", 80), collapse=""), "\n")
cat("SUMMARY STATISTICS\n")
cat(paste(rep("=", 80), collapse=""), "\n")

cat("\nAverage Cohen's Kappa by Model:\n")
model_summary <- avg_long %>%
  group_by(Model) %>%
  summarise(Mean_Kappa = mean(Avg_Kappa, na.rm = TRUE),
            SD_Kappa = sd(Avg_Kappa, na.rm = TRUE),
            .groups = 'drop') %>%
  arrange(desc(Mean_Kappa))

print(model_summary)

cat("\nBest Overall Condition:\n")
best_condition <- avg_long %>% arrange(desc(Avg_Kappa)) %>% slice(1)
cat(sprintf("  %s: %.3f\n", best_condition$Condition, best_condition$Avg_Kappa))

cat("\nVisualization creation complete!\n")
cat("All plots saved to results/figures/ directory\n")
