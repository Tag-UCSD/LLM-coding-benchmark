#!/usr/bin/env Rscript
#
# Analyze relationship between code concreteness and LLM performance
#

library(readxl)
library(dplyr)
library(ggplot2)
library(gridExtra)
library(scales)

# Load concreteness data
cat("Loading concreteness data...\n")
concreteness <- read_excel("data/processed/concreteness.xlsx")
concreteness$Word <- tolower(concreteness$Word)

# Code names
codes <- c(
  'Scholar',
  'Activist',
  'Monumental Memorialization',
  'Mention of Scholarly Work',
  'Social/Political Advocacy',
  'Coalition Building',
  'Out of the Mouth of Academics',
  'Out of the Mouth of Activists',
  'Collective Synecdoche'
)

# Function to convert code name to R column name format
code_to_r_colname <- function(code) {
  # R converts spaces and slashes to dots when reading CSVs
  gsub("/", ".", gsub(" ", ".", code))
}

# Function to get concreteness score for a text
get_concreteness <- function(text) {
  words <- strsplit(tolower(text), " ")[[1]]
  # Skip common function words
  words <- words[!words %in% c('of', 'the', 'a', 'an')]

  scores <- c()
  for (word in words) {
    match <- concreteness[concreteness$Word == word, ]
    if (nrow(match) > 0) {
      scores <- c(scores, match$Conc.M[1])
    }
  }

  if (length(scores) > 0) {
    return(mean(scores))
  } else {
    return(NA)
  }
}

# Function to calculate F1 and accuracy for a single code
calculate_f1_and_accuracy <- function(gold_standard, model_predictions, code_col) {
  # Filter to test set (IDs 9-119)
  gold_test <- gold_standard %>%
    filter(id >= 9 & id <= 119) %>%
    arrange(id) %>%
    select(id, all_of(code_col))

  model_test <- model_predictions %>%
    filter(id >= 9 & id <= 119) %>%
    arrange(id) %>%
    select(id, all_of(code_col))

  # Merge on ID
  merged <- merge(
    gold_test,
    model_test,
    by = 'id',
    suffixes = c('_gold', '_pred')
  )

  # Drop NaN values
  merged <- na.omit(merged)

  if (nrow(merged) == 0) {
    return(list(f1 = NA, accuracy = NA))
  }

  y_true <- merged[[paste0(code_col, '_gold')]]
  y_pred <- merged[[paste0(code_col, '_pred')]]

  # Calculate metrics
  tp <- sum(y_true == 1 & y_pred == 1)
  fp <- sum(y_true == 0 & y_pred == 1)
  fn <- sum(y_true == 1 & y_pred == 0)
  tn <- sum(y_true == 0 & y_pred == 0)

  # F1 score
  precision <- ifelse(tp + fp == 0, 0, tp / (tp + fp))
  recall <- ifelse(tp + fn == 0, 0, tp / (tp + fn))
  f1 <- ifelse(precision + recall == 0, 0, 2 * precision * recall / (precision + recall))

  # Accuracy
  accuracy <- (tp + tn) / (tp + tn + fp + fn)

  return(list(f1 = f1, accuracy = accuracy))
}

# Calculate concreteness scores for each code
cat("\nCalculating concreteness scores for each code...\n")
code_concreteness <- data.frame(
  code = codes,
  concreteness = sapply(codes, get_concreteness)
)

for (i in 1:nrow(code_concreteness)) {
  cat(sprintf("  %s: %.2f\n",
              code_concreteness$code[i],
              code_concreteness$concreteness[i]))
}

# Load gold standard and GPT-4 predictions
cat("\nLoading model results...\n")
gold_standard <- read.csv('data/processed/gold_standard_coding.csv')
gpt4 <- read.csv('results/raw/output_original/per-code-with-justification_t=0_top_p=1_model=gpt-4/processed_responses.csv')

# Calculate F1 and accuracy for each code
cat("\nCalculating performance metrics...\n")
results <- data.frame()

for (code in codes) {
  code_r <- code_to_r_colname(code)  # Convert to R column name format
  metrics <- calculate_f1_and_accuracy(gold_standard, gpt4, code_r)
  conc <- code_concreteness$concreteness[code_concreteness$code == code]

  results <- rbind(results, data.frame(
    Code = code,
    Concreteness = conc,
    F1 = metrics$f1,
    Accuracy = metrics$accuracy
  ))

  cat(sprintf("  %s: F1=%.3f, Acc=%.3f, Conc=%.2f\n",
              code, metrics$f1, metrics$accuracy, conc))
}

# Remove any codes with missing concreteness scores
results_clean <- na.omit(results)

cat(sprintf("\n%d out of %d codes have concreteness scores\n",
            nrow(results_clean), nrow(results)))

# Save results
write.csv(results, 'results/outputs/code_concreteness_analysis_R.csv', row.names = FALSE)
cat("\n✓ Saved analysis to results/outputs/code_concreteness_analysis_R.csv\n")

# Fit regression models
model_f1 <- lm(F1 ~ Concreteness, data = results_clean)
model_acc <- lm(Accuracy ~ Concreteness, data = results_clean)

# Get regression statistics
summary_f1 <- summary(model_f1)
summary_acc <- summary(model_acc)

# Create visualizations
cat("\nCreating visualizations...\n")

# Helper function to format p-values
format_pval <- function(p) {
  if (p < 0.001) return("p < 0.001")
  return(sprintf("p = %.3f", p))
}

# Plot 1: F1 Score
p1 <- ggplot(results_clean, aes(x = Concreteness, y = F1)) +
  geom_point(size = 4, alpha = 0.6, color = 'steelblue') +
  geom_smooth(method = 'lm', se = FALSE, color = 'red', linetype = 'dashed', linewidth = 1) +
  geom_text(aes(label = Code), hjust = -0.1, vjust = -0.5, size = 2.5, alpha = 0.7) +
  labs(
    title = 'GPT-4 Performance vs Code Concreteness\n(F1 Score)',
    x = 'Code Concreteness (Mean)',
    y = 'F1 Score'
  ) +
  annotate('text',
           x = min(results_clean$Concreteness) + 0.1,
           y = max(results_clean$F1) - 0.05,
           label = sprintf('y = %.3fx + %.3f\nR² = %.3f, %s',
                          coef(model_f1)[2],
                          coef(model_f1)[1],
                          summary_f1$r.squared,
                          format_pval(summary_f1$coefficients[2, 4])),
           hjust = 0, size = 3.5, color = 'red') +
  theme_minimal() +
  theme(
    plot.title = element_text(face = 'bold', size = 14, hjust = 0.5),
    axis.title = element_text(face = 'bold', size = 12),
    panel.grid.minor = element_blank()
  )

# Plot 2: Accuracy
p2 <- ggplot(results_clean, aes(x = Concreteness, y = Accuracy)) +
  geom_point(size = 4, alpha = 0.6, color = 'darkgreen') +
  geom_smooth(method = 'lm', se = FALSE, color = 'red', linetype = 'dashed', linewidth = 1) +
  geom_text(aes(label = Code), hjust = -0.1, vjust = -0.5, size = 2.5, alpha = 0.7) +
  labs(
    title = 'GPT-4 Performance vs Code Concreteness\n(Accuracy)',
    x = 'Code Concreteness (Mean)',
    y = 'Accuracy'
  ) +
  annotate('text',
           x = min(results_clean$Concreteness) + 0.1,
           y = max(results_clean$Accuracy) - 0.05,
           label = sprintf('y = %.3fx + %.3f\nR² = %.3f, %s',
                          coef(model_acc)[2],
                          coef(model_acc)[1],
                          summary_acc$r.squared,
                          format_pval(summary_acc$coefficients[2, 4])),
           hjust = 0, size = 3.5, color = 'red') +
  theme_minimal() +
  theme(
    plot.title = element_text(face = 'bold', size = 14, hjust = 0.5),
    axis.title = element_text(face = 'bold', size = 12),
    panel.grid.minor = element_blank()
  )

# Combine plots
combined_plot <- grid.arrange(p1, p2, ncol = 2)

# Save plot
ggsave('results/figures/concreteness_vs_performance_R.png',
       combined_plot,
       width = 16, height = 6, dpi = 300)

cat("✓ Saved visualization to results/figures/concreteness_vs_performance_R.png\n")

# Print summary statistics
cat("\n================================================================================\n")
cat("SUMMARY STATISTICS\n")
cat("================================================================================\n")
cat(sprintf("\nCorrelation between Concreteness and F1: %.3f\n",
            cor(results_clean$Concreteness, results_clean$F1)))
cat(sprintf("Correlation between Concreteness and Accuracy: %.3f\n",
            cor(results_clean$Concreteness, results_clean$Accuracy)))
cat(sprintf("\nMean Concreteness: %.2f (SD: %.2f)\n",
            mean(results_clean$Concreteness), sd(results_clean$Concreteness)))
cat(sprintf("Mean F1: %.3f (SD: %.3f)\n",
            mean(results_clean$F1), sd(results_clean$F1)))
cat(sprintf("Mean Accuracy: %.3f (SD: %.3f)\n",
            mean(results_clean$Accuracy), sd(results_clean$Accuracy)))

# Print detailed regression statistics
cat("\n================================================================================\n")
cat("REGRESSION STATISTICS\n")
cat("================================================================================\n")

cat("\n--- Predicting F1 Score from Concreteness ---\n")
cat(sprintf("Slope (β): %.4f (SE = %.4f)\n",
            coef(model_f1)[2],
            summary_f1$coefficients[2, 2]))
cat(sprintf("  p-value: %.4f\n", summary_f1$coefficients[2, 4]))
cat(sprintf("Intercept: %.4f (SE = %.4f)\n",
            coef(model_f1)[1],
            summary_f1$coefficients[1, 2]))
cat(sprintf("  p-value: %.4f\n", summary_f1$coefficients[1, 4]))
cat(sprintf("R²: %.4f\n", summary_f1$r.squared))
cat(sprintf("N: %d\n", nrow(results_clean)))

cat("\n--- Predicting Accuracy from Concreteness ---\n")
cat(sprintf("Slope (β): %.4f (SE = %.4f)\n",
            coef(model_acc)[2],
            summary_acc$coefficients[2, 2]))
cat(sprintf("  p-value: %.4f\n", summary_acc$coefficients[2, 4]))
cat(sprintf("Intercept: %.4f (SE = %.4f)\n",
            coef(model_acc)[1],
            summary_acc$coefficients[1, 2]))
cat(sprintf("  p-value: %.4f\n", summary_acc$coefficients[1, 4]))
cat(sprintf("R²: %.4f\n", summary_acc$r.squared))
cat(sprintf("N: %d\n", nrow(results_clean)))

cat("\n================================================================================\n")
cat("DONE\n")
cat("================================================================================\n")
