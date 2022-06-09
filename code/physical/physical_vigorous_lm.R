library(lme4)
library(readr)
library(afex)
library(nlme)
library(emmeans)
library(psycho)
library(tidyverse)
library(easystats)
library(report)
require(lmerTest)

# read data
df_work <- read_csv("../code/physical/stats_work_lm.csv.gz") 
df_off <- read_csv("../code/physical/stats_off_lm.csv.gz")

# ------------------------------------------
# model for shift*age
# ------------------------------------------
# model = lmer(vigorous ~ shift * age  + (1 | id), data = df_work)
model <- aov(vigorous_min ~ shift + age + gender, data = df_work)

em <- emmeans(model, ~ shift)
# posthoc = PostHocTest(aov(vigorous_min ~ shift + age + gender, data=df_work), method = "lsd")

sink("vigorous/vigorous_work_age_shift.txt", append=FALSE)
print(summary(model))
# print(posthoc)
print(summary(em))
print(report(model))
sink()

# model = lmer(vigorous ~ shift * age  + (1 | id), data = df_off)
model <- aov(vigorous_min ~ shift + age + gender, data = df_off)

em <- emmeans(model, pairwise ~ shift)
posthoc = PostHocTest(aov(vigorous_min ~ shift, data=df_off), method = "lsd")

sink("vigorous/vigorous_off_age_shift.txt", append=FALSE)
print(summary(model))
print(posthoc)
print(summary(emmeans(model, ~ shift)))
print(report(model))
sink()

