library(lme4)
library(readr)
library(afex)
library(nlme)
library(emmeans)
library(psycho)
library(tidyverse)
library(easystats)
library(report)
library(rstatix)
library(ez)
library(ggpubr)
library(DescTools)
library(reshape2)

# read data
df_work <- read_csv("../code/physical/diurnal_work_lm_6.csv.gz") 
df_off <- read_csv("../code/physical/diurnal_off_lm_6.csv.gz") 

df_work$time <- factor(df_work$time)
df_work$shift <- factor(df_work$shift)
df_work$id <- factor(df_work$id)

df_off$time <- factor(df_off$time)
df_off$shift <- factor(df_off$shift)
df_work$id <- factor(df_work$id)

# ------------------------------------------
# model for shift*age
# ------------------------------------------
# model = lmer("step_ratio ~ time * shift  + (1 | id)", data = df_work)
# model <- aov(step_ratio ~ time * shift + Error(id), data = df_work)
# model = anova_test(data = df_work, dv = step_ratio, wid = id, between = c(shift, time))
model <- ezANOVA(data=df_work, dv=step_ratio, wid=.(id), within=.(time), between=.(shift), type=3)

# em <- emmeans(model, ~ shift|time)
# posthoc <- TukeyHSD(aov(step_ratio ~ shift*time, data=df_work, conf.level=.95))
# posthoc <- pairwise.t.test(step_ratio, shift*time, p.adjust.method="bonferroni")
posthoc = PostHocTest(aov(step_ratio ~ shift*time, data=df_work), method = "lsd")


sink("diurnal_step/work_shift_time.txt", append=FALSE)
# print(summary(model))
# print(get_anova_table(model, correction = "GG"))
print(model)
print(posthoc)
# print(summary(em))
# print(report(model))
# print(anova(model))
sink()

# model = lmer(step_ratio ~ shift * time  + (1 | id), data = df_off)
# model <- aov(step_ratio ~ shift * time + Error(id), data = df_off)
# model <- aov(step_ratio ~ time * shift + Error(id), data = df_off)
model <- ezANOVA(data=df_off, dv=step_ratio, wid=.(id), within=.(time), between=.(shift), type=3)
# model <- ezANOVA(data=df_off, dv=step_ratio, wid=.(id), between=shift*time, type=3)
posthoc = PostHocTest(aov(step_ratio ~ shift*time, data=df_off), method = "lsd")
# em <- emmeans(model, ~ shift|time)

sink("diurnal_step/off_shift_time.txt", append=FALSE)
print(summary(model))
print(model)
print(posthoc)
# print(summary(em))
# print(report(model))
sink()