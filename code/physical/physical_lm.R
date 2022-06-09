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
model = lmer(rest ~ shift * age  + (1 | id), data = df_work)
# model = lmer(rest ~ shift * age * work  + (1 | id), data = df)
em <- emmeans(model, "shift")

sink("rest/rest_work_age_shift.txt", append=FALSE)
print(summary(model))
print(summary(em))
print(report(model))
sink()

model = lmer(rest ~ shift * age  + (1 | id), data = df_off)
# model = lmer(rest ~ shift * age * work  + (1 | id), data = df)

em <- emmeans(model, "shift")
sink("rest/rest_off_age_shift.txt", append=FALSE)
print(summary(model))
print(summary(em))
print(report(model))
sink()

# ------------------------------------------
# model for shift*gender
# ------------------------------------------
# model = lmer(rest ~ shift * gender  + (1 | id), data = df_work)
# 
# sink("rest/rest_work_gender_shift.txt", append=FALSE)
# print(summary(model))
# print(report(model))
# sink()
# 
# model = lmer(rest ~ shift * gender  + (1 | id), data = df_off)
# 
# sink("rest/rest_off_gender_shift.txt", append=FALSE)
# print(summary(model))
# print(report(model))
# sink()
# 
# # ------------------------------------------
# # model for shift*gender*age
# # ------------------------------------------
# # model = lmer(rest ~ shift + age + gender + (1 | id), data = df_work)
# model = lmer(rest ~ shift + age + gender + shift:age + shift:gender + (1 | id), data = df_work)
# 
# sink("rest/rest_work_gender_age_shift.txt", append=FALSE)
# print(summary(model))
# print(report(model))
# sink()
# 
# # model = lmer(rest ~ shift + age + gender + (1 | id), data = df_off)
# model = lmer(rest ~ shift + age + gender + shift:age + shift:gender + (1 | id), data = df_off)
# 
# sink("rest/rest_off_gender_age_shift.txt", append=FALSE)
# print(summary(model))
# print(report(model))
# sink()

# options <- as.list(c("shift*age + (1 | id)", "shift*gender + (1 | id)"))
# save_list <- list("physical_daily/rest_off_age_shift.txt", "physical_daily/rest_off_gender_shift.txt")
# closeAllConnections()
# 
# for (i in seq_along(options)){
#   model <- lmer(paste('rest',  '~', options[i]), data = df)
#   # model <- lmer(reformulate(options[i], 'rest'), data = df)
#   
#   save_name <- save_list[[i]]
#   print(c(save_name))
#   
#   # sink(save_name, append=FALSE)
#   print("Facial variance LMM")
#   print(summary(model))
#   # print(summary(em))
#   print("-----------------------------------")
#   print("-----------------------------------")
#   print(report(model))
#   # sink()
#   print('here')
#   closeAllConnections()
# }
