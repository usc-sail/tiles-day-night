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
model = lmer(step_ratio ~ shift * age  + (1 | id), data = df_work)
em <- emmeans(model, ~ shift)

sink("step/step_work_age_shift.txt", append=FALSE)
print(summary(model))
print(summary(em))
print(report(model))
sink()

model = lmer(step_ratio ~ shift * age  + (1 | id), data = df_off)
em <- emmeans(model, ~ shift)

sink("step/step_off_age_shift.txt", append=FALSE)
print(summary(model))
print(summary(em))
print(report(model))
sink()

model = lmer(step_ratio ~ shift * age * work  + (1 | id), data = df)
# em <- emmeans(model, "work")

sink("step/step_age_shift.txt", append=FALSE)
print(summary(model))
# print(summary(em))
print(report(model))
sink()

# ------------------------------------------
# model for shift*gender
# ------------------------------------------
# model = lmer(step ~ shift * gender  + (1 | id), data = df_work)
# 
# sink("step/step_work_gender_shift.txt", append=FALSE)
# print(summary(model))
# print(report(model))
# sink()
# 
# model = lmer(step ~ shift * gender  + (1 | id), data = df_off)
# 
# sink("step/step_off_gender_shift.txt", append=FALSE)
# print(summary(model))
# print(report(model))
# sink()
# 
# # ------------------------------------------
# # model for shift*gender*age
# # ------------------------------------------
# # model = lmer(step ~ shift * age * gender  + (1 | id), data = df_work)
# model = lmer(step ~ shift + age + gender + shift:age + shift:gender + (1 | id), data = df_work)
# 
# sink("step/step_work_gender_age_shift.txt", append=FALSE)
# print(summary(model))
# print(report(model))
# sink()
# 
# # model = lmer(step ~ shift * age * gender  + (1 | id), data = df_off)
# model = lmer(step ~ shift + age + gender + shift:age + shift:gender + (1 | id), data = df_off)
# 
# sink("step/step_off_gender_age_shift.txt", append=FALSE)
# print(summary(model))
# print(report(model))
# sink()
