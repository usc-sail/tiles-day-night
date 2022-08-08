library(lme4)
library(readr)
library(afex)
library(nlme)
library(emmeans)
library(psycho)
library(tidyverse)
library(easystats)
library(report)
library(desc)
require(lmerTest)
library(DescTools)

# read data
df_igtb <- read_csv("../code/ground_truth/igtb.csv.gz") 

# ------------------------------------------
# model for shift*age
# ------------------------------------------
# bfi_Neuroticism
model <- aov(bfi_Neuroticism ~ Shift * Age, data = df_igtb)

# em <- emmeans(model, pairwise ~ Shift * Age)
posthoc = PostHocTest(aov(bfi_Neuroticism ~ Shift * Age, data=df_igtb), method = "lsd")

sink("igtb/neurotism_shift.txt", append=FALSE)
print(summary(model))
print(posthoc)
# print(summary(em))
print(report(model))
sink()

