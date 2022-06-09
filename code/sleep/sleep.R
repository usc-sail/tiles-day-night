library(lme4)
library(readr)
library(afex)
library(nlme)
library(emmeans)
library(psycho)
library(tidyverse)
library(easystats)
library(report)

emm_options(opt.digits = FALSE)

# read data
df <- read_csv("../code/sleep/sleep.csv.gz")
df_work <- subset(df,df$work=='workday')
df_off <- subset(df,df$work=='offday')
df_all <- subset(df,df$work=='all')

# ------------------------------------------
# model for shift*age
# ------------------------------------------
model <- aov(duration ~ shift + age + gender, data = df_work)
em <- emmeans(model, "shift", adjust = "bonferroni")
sink("sleep_duration/work.txt", append=FALSE)
print(summary(model))
print(summary(em))
print(report(model))
sink()

model <- aov(duration ~ shift + age + gender, data = df_off)
em <- emmeans(model, "shift", adjust = "bonferroni")
sink("sleep_duration/off.txt", append=FALSE)
print(summary(model))
print(summary(em))
print(report(model))
sink()

# ------------------------------------------
# model for ratio
# ------------------------------------------
model <- aov(efficiency ~ shift + age + gender, data = df_work)
em <- emmeans(model, ~shift*age)
# posthoc = PostHocTest(aov(efficiency ~ shift*age, data=df_work), method = "lsd")

sink("sleep_ratio/work.txt", append=FALSE)
print(summary(model))
print(summary(emmeans(model, ~shift)))
# print(summary(em))
print(report(model))
# print(posthoc)
sink()

model <- aov(efficiency ~ shift + age + gender, data = df_off)
em <- emmeans(model, "shift", adjust = "bonferroni")
sink("sleep_ratio/off.txt", append=FALSE)
print(summary(model))
print(summary(em))
print(report(model))
sink()


model <- aov(mid ~ shift + age + gender, data = df_all)
em <- emmeans(model, "shift", adjust = "bonferroni")
sink("sleep_ratio/mid.txt", append=FALSE)
print(summary(model))
print(summary(em))
print(report(model))
sink()

# model <- aov(total_seconds ~ shift * age, data = df_work)
# em <- emmeans(model, "shift")
# sink("sleep_ms/work.txt", append=FALSE)
# print(summary(model))
# print(summary(em))
# print(report(model))
# sink()

print("here")
# model <- aov(total_seconds ~ shift * age, data = df_off)
# em <- emmeans(model, "shift", adjust = "bonferroni")
# sink("sleep_ms/off.txt", append=FALSE)
# print(summary(model))
# print(summary(em))
# print(report(model))
# sink()
print("here")

