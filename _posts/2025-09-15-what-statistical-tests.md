---
layout: post
title: A Guide on Statistical Tests
description: Make your findings statistically significant with this partical, flowchart-based guide on selecting the right statistical test and post-hoc analysis.
tags: Statistics
date: 2025-09-15
thumbnail: assets/img/posts/stats.png
related_posts: false
---

**Author**: [Naga Karthik Enamundram](https://scholar.google.com/citations?user=ZryIoMMAAAAJ) (edited with LLMs)

Too often, I see tables in ML papers where authors claim that their method is "significantly" better than the rest of the methods without performing any statistical tests. I feel that such claims should be backed up by statistical evidence and not just concluding from the magnitude of the metrics reported. Even if the error intervals are reported, the top methods tend to lie with the standard deviation of each other, making it hard to conclude which method is _actually_ better. Therefore, in this post, I intend to cover a few recurring scenarios when presenting results in ML papers and what kind of tests could be performed. Choosing the right test is tricky but it is worth the effort as results backed by statistical evidence seem more credible. This post is inspired from my own struggles in deciding what tests to do and how I wished there was a guide for non-stats folks to refer to when it's time to put results into the paper. 

Here's a flowchart on the most common types of tests depending on the type of the output variable followed by the series of tests to consider.

{% include figure.liquid path="assets/img/posts/stats1.svg" class="img-fluid rounded z-depth-1 center" width=600 zoomable=true %}

### Definitions

#### Outcome (dependent) variable types

- **Continuous variables**: Think measuring tape. Continuous variables represent values that can be measured on a continuous scale. Their values are not restricted to separate, distinct numbers. For example:
  - Performance metrics such as the F1-score, MSE; values whose range lies between 0-1. 
  - Features such as a person's height, average temperature, etc. 

- **Categorical variables**: Think groups or labeled buckets. Categorical variables only take on a limited set of values, assigning each data point to a particular group. There are two types of variables: (i) **Nominal**: categories have _no_ intrinsic order (e.g. car, bus, plane), and (ii) **Ordinal**: categories have a meaniningful order (e.g. rating something as `good`, `okay`, `bad`, or, levels of difficulty, etc.). A few examples of categorial variables:
  - Model prediction as `Spam`/`Not spam`, or, classification of a bacterium as `Resistant`/`Susceptible` against a specific antibiotic.
  - Features such as grading of a tumor on a scale of 1-4 (note: this is ordinal), or, a person's blood type (A, B, AB, O; note: this is nominal). 

- **Survival variables**: Think an hourglass. A survival variable is a unique type of data that has two parts: (i) a measure of time until a specific event occurs, and (ii) an indicator of whether the event has occurred or if the observation period ended before the event could happen (this is called censoring). A few examples:
  - Time until a patient relapses after treatment, with some patients still being disease-free at the end of the study (censored data).
  - Time until a machine fails, with some machines still operational at the end of the observation period (censored data).

#### Exposure (independent) variable types

- **Groups**: They refer to the different methods/models we want to compare. For example, if we have three models A, B, and C, then we have three "groups".

- **Samples**: They refer to the number of observations we have for each group. For example, (i) each set of predictions from models A, B, and C is a sample (so three models, three sets of samples), (ii) if we have five different runs of model A, then we have five samples for model A, and so on.

- **Paired samples**: They refer to the samples that are related to each other. For example, (i) if we have three models A, B, and C and we evaluate them on the same test set, then the samples from these models are "paired" because they are related to each other through the same test set, (ii) if we have a model that we run five times with different random seeds and evaluate them on the same test set, then the samples from these five runs are paired samples.

- **Independent samples**: They refer to the samples that are _not_ related to each other. For example, say we have a large test dataset and we create non-overlapping sub-test sets from it. Then, evaluating models A, B, and C on these different sub-test sets will give us independent samples. 

- **Parametric**: This class of tests assume that the data follows some "known" distribution (most commonly the normal distribution) and are based on the parameters like the mean and standard deviation. Normality of the data can be tested using D'Agostino and Pearson's test, Shapiro-Wilk test, etc. If the p-value from these tests is greater than a significance level (typically 0.05), meaning that the null hypothesis ($H_0$; stating that the data is normally distributed) is _not_ rejected. This implies that we don't have enough evidence to conclude that the data are not normally distributed, but know that the data lack a significant deviation from the normal distribution (hence enabling the use of parametric tests).  

- **Non-parametric**: This class of tests do not assume that the data follow a normal distribution. They are typically used when the data is not normally distributed or when the sample size is small (typically less than 30 per group). 

[Statistics How To](https://www.statisticshowto.com/probability-and-statistics/statistics-definitions/) is more extensive in terms of the definitions covered. Do check it out!

#### Errors in hypothesis testing

When performing statistical tests, we typically start with a null hypothesis ($H_0$) and an alternative hypothesis ($H_a$). The null hypothesis usually states that there is no effect or no difference between the groups, while the alternative hypothesis states that there is an effect or a difference. Based on the results of the statistical test, we either reject the null hypothesis or fail to reject it. However, there are two types of errors that can occur in this process:

- **Type I error (False Positive)**: It occurs when we reject the null hypothesis ($H_0$) when it is actually true. In simpler terms, it's like a false alarm where we think there is an effect or difference when there isn't one (e.g. concluding that a drug is effective when it's not). The significance level (alpha, typically set at 0.05) represents the probability of making a Type I error. For example, if we set alpha to 0.05, it means that we are willing to accept a 5% chance of incorrectly rejecting the null hypothesis.

- **Type II error (False Negative)**: It occurs when we fail to reject the null hypothesis ($H_0$) when it is actually false. In simpler terms, it's like missing a real effect or difference that actually exists (e.g. failing to detect that a drug is working). The probability of making a Type II error is denoted by beta (β). The power of a test, which is calculated as (1 - β), represents the probability of correctly rejecting the null hypothesis when it is false. A higher power means a lower chance of making a Type II error. Typically, researchers aim for a power of 0.8 or higher, meaning there is an 80% chance of correctly detecting an effect if it exists.

### Choosing the right test

When it comes to presenting the results, a recurring scenario is the following: 
> We have the method/model that we have proposed and we want to compare its performance with the rest of the methods/models from the literature. We also have a fixed test set on which we evaluate our models on. 

Now, let's take a bottom-up approach to arrive at the right test(s) to perform. Note that the test set is fixed so we have already reduced the search space for the class of the tests to be within: "2 groups" or ">2 groups" with "paired" samples (since the models are evaluated on the same test set). If we have two models (model A vs. model B) then we use either paired Student's t-test or Wilcoxon signed rank test if the variable we want to compare is continuous (e.g. accuracy, F1-score, etc.) and McNemar's test if the variable is categorical (e.g. model predictions as `Spam`/`Not spam`). If we're comparing more than two models (i.e. ours and two or more) then we use either repeated measures ANOVA or Friedman test if the variable we want to compare is continuous and Cochran's Q test if the variable is categorical. The next natural question is: should we use parametric or non-parametric tests? 


#### Parametric or Non-parametric?

When comparing continuous variables, the choice between choosing parametric or non-parametric tests depends on the distribution of the data. To ground it in ML terms, the "data" here refer to the set of performance metrics on the test set obtained from the models we want to compare. To know how the data are distributed we typically run normality tests from the `scipy.stats` package. Here's a short code example of how to do it:

```python
import numpy as np
from scipy import stats
# Example data: performance metrics from two models
model_a_metrics = np.array([0.85, 0.87, 0.86, 0.88, 0.84])
model_b_metrics = np.array([0.80, 0.82, 0.81, 0.83, 0.79])
# Perform D'Agostino and Pearson's test for normality
stat_a, p_value_a = stats.normaltest(model_a_metrics)
stat_b, p_value_b = stats.normaltest(model_b_metrics)
# Significance level
# NOTE: The null hypothesis (H0) is that the data is normally distributed.
alpha = 0.05
# Check if the data is normally distributed
is_a_normal = p_value_a > alpha
is_b_normal = p_value_b > alpha
print(f"Model A normality: {is_a_normal}, p-value: {p_value_a}")
print(f"Model B normality: {is_b_normal}, p-value: {p_value_b}")

# CHECK
# If p > alpha, we fail to reject the null hypothesis --> data is normally distributed --> parametric
# If p <= alpha, we reject the null hypothesis --> data is not normally distributed --> non-parametric
```

Based on the normality tests, we now know whether to choose from parametric or non-parametric tests. More detailed definitions with examples can be found [here](https://www.mayo.edu/research/documents/parametric-and-nonparametric-demystifying-the-terms/doc-20408960). Continuing the example from the scenario mentioned above, say there are more than 2 groups (i.e. we're comparing more than 2 methods) and the test indicates that there is a significant difference between the groups. How do we know which groups are different from each other? This is where post-hoc tests come into play.

#### Post-hoc tests

_Post-hoc_ is a Latin term that means "after this". [Post-hoc tests](https://www.statisticshowto.com/probability-and-statistics/statistics-definitions/post-hoc/) are additional tests performed after an initial statistical test (like ANOVA or Friedman test) to determine which specific groups are different from each other. They help to identify where the differences lie when the initial test indicates that there is a significant difference among the groups. More concretely, say we have three models A, B, and C and we perform a Friedman test (non-parametric) to compare their performance on a fixed test set. The test gives a p-value of 0.02 (which is significant!). But, we don't know which pairs of models are significantly different from each other (i.e. A vs. B, A vs. C, B vs. C). Therefore, we perform post-hoc tests, which involve multiple pairwise comparisons between the groups to identify which specific pairs of groups have significant differences in their means or distributions. Some common post-hoc tests include:
- **Tukey's HSD (Honestly Significant Difference) test**: used after ANOVA to find means that are significantly different from each other.
- **Bonferroni correction**: adjusts the significance level when multiple pairwise tests are performed to control the overall Type I error rate. This correction limits the possibility of getting a statistically significant result because, the more tests we run, the more likely we are to get a significant result. The correction essentially lowers the area where we can reject the null hypothesis by adjusting the alpha according to the number of tests. For e.g. after Bonferroni correction, $$\alpha_{\textrm{new}} = \alpha_{\textrm{old}} / N$$, where $N$ is the number of tests or number of comparisons.
- **Dunn's test**: non-parametric post-hoc test used after the Kruskal-Wallis test or Friedman test. 

Here's a short code example on performing Dunn's post-hoc test:

```python
import numpy as np
import pandas as pd
import scikit_posthocs as sp
# Example data: performance metrics from three models
model_a_metrics = np.array([0.85, 0.87, 0.86, 0.88, 0.84])
model_b_metrics = np.array([0.80, 0.82, 0.81, 0.83, 0.79])
model_c_metrics = np.array([0.78, 0.77, 0.79, 0.76, 0.80])
# Combine the data into a single array
data = np.concatenate([model_a_metrics, model_b_metrics, model_c_metrics])
# Create a group labels array
groups = (['A'] * len(model_a_metrics) +
          ['B'] * len(model_b_metrics) +
          ['C'] * len(model_c_metrics))
# Create a DataFrame for the data
df = pd.DataFrame({'Model': groups, 'Accuracy': data})
# Perform Dunn's test with Holm-Bonferroni correction
dunn_results = sp.posthoc_dunn(df, val_col='Accuracy', group_col='Model', p_adjust='holm')
print(dunn_results)
```

Note that post-hoc tests are only performed when the initial test indicates that there is a significant difference between the groups.

Okay, we now have an understanding of how to go about choosing the right test. Let's look at a few examples now.

### Examples

#### Example 1: Comparing accuracy between five models on a fixed test set
Say you have five models (A, B, C, D, E) and you want to compare their accuracy on a fixed test set. The workflow would be as follows:
1. Since we're comparing accuracy, the outcome variable is continuous.
2. We have five models, so we have more than two groups.
3. The samples are paired since the models are evaluated on the same test set.
4. Check for normality on each of the test set predictions for the five models. If all the models' predictions are normally distributed, we can use parametric tests. If at least one of them is not normally distributed, we use non-parametric tests.
5. Choose the appropriate test. So, we have:
  - `continuous`, `>2 groups`, `paired`, `non-parametric`: Friedman test
  - `continuous`, `>2 groups`, `paired`, `parametric`: Repeated measures ANOVA
6. If the test indicates that there is a significant difference between the groups, perform post-hoc test. For `parametric`, use Tukey's HSD test. For `non-parametric`, use Dunn's test.

#### Example 2: Comparing ages of patients in train and test sets
Say you are working with medical data and you have randomly split the data into train/test but you want to know if the age of the patients in train set is significantly different from that in the test set (to make a case for your model's generalization across age groups). The workflow would be as follows:
1. Identify the type of outcome variable: `Age` is a continuous variable.
2. Identify the number of groups: We have two groups (train and test).
3. Identify the type of samples: The samples are independent since the train and test sets are disjoint.
4. Check for normality: Use D'Agostino and Pearson's test or Shapiro-Wilk test to check if the age data in both groups is normally distributed.
5. Choose the appropriate test:
  - `continuous`, `2 groups`, `independent`, `non-parametric`: Mann-Whitney U test
  - `continuous`, `2 groups`, `independent`, `parametric`: Student's t-test (two-sample t-test)

#### Example 3: Comparing model predictions (categorical) between three models on a fixed test set

Say you have three models (A, B, C) and you want to compare their predictions (as `Malignant`/`Benign`) on a fixed test set. The workflow would be as follows:
1. Since we're comparing models' binary classification predictions, the outcome variable is categorical.
2. We have three models, so we have more than two groups.
3. The samples are paired since the models are evaluated on the same test set.
4. Choose the appropriate test. So, we have:
  - `categorical`, `>2 groups`, `paired`: Cochran's Q test


### General Notes and Common Pitfalls

#### Choosing significance level (alpha)

A good significance level balances the risks of false positives and false negatives. Choosing the right significance level depends on the context and the consequence of the errors. A significance level of 5% is more commonly used than that of 1% which is more conservative and used only in safety-critical applications like medicine. 

#### Ignoring the multiple comparisons problem

When we have 3 or more groups to compare, running multiple pairwise tests (i.e. A vs. B, A vs. C, B vs. C) should _not_ be done as multiple comparisons increase the chance of getting a "significant" result purely by luck. As each test has its own significance level (alpha), the overall chance of getting a false positive increases with multiple comparisons. Therefore, in this scenario, it is recommended to run a Friedman test or repeated measures ANOVA, and if it is significant, then only run post hoc tests to find specific differences between groups. 

I only focused on examples of contiguous and categorical variables in this post because those are what I came across most often. I will update this post with examples of survival variables and their tests in the future. 

Thanks to Kalum Ost, Jan Valošek, Pierre-Louis Benveniste, and Gemini 2.5 Pro for their suggestions on the drafts of this post.