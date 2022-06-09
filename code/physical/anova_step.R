library(lme4)
library(readr)
library(afex)
library(nlme)
library(emmeans)
library(psycho)
library(tidyverse)
library(easystats)
library(report)

# read data
df_work <- read_csv("../code/physical/stats_work_lm.csv.gz") 
df_off <- read_csv("../code/physical/stats_off_lm.csv.gz") 
df <- read_csv("../code/physical/stats_lm.csv.gz")

# ------------------------------------------
# model for shift*age
# ------------------------------------------
# model = lmer(rest ~ shift * age  + (1 | id), data = df_work)
# model = lmer(step_ratio ~ shift * age * work  + (1 | id), data = df)
model <- aov(step_ratio ~ shift + age + gender, data = df_work)

em <- emmeans(model, pairwise~shift)
# emm_contr <- contrast(em, simple = "each", combine = TRUE)
# posthoc = PostHocTest(aov(minutesAsleep ~ shift*age, data=df_work), method = "lsd")

sink("step/step_work_age_shift.txt", append=FALSE)
print(summary(model))
print(summary(em))
print(report(model))
sink()

model <- aov(step_ratio ~ shift + age + gender, data = df_off)

em <- emmeans(model, pairwise~shift)
sink("step/step_off_age_shift.txt", append=FALSE)
print(summary(model))
print(summary(em))
print(report(model))
sink()
