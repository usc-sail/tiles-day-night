# library(lme4)
# library(readr)
# library(afex)
# library(nlme)
# library(emmeans)
# library(psycho)
library(tidyverse)
# library(easystats)
library(report)
# library(rstatix)
library(ez)
# library(ggpubr)
library(DescTools)
# library(reshape2)

# # read data
# df_work <- read_csv("../code/physical/diurnal_work_lm_6.csv.gz") 
# df_off <- read_csv("../code/physical/diurnal_off_lm_6.csv.gz") 

df_work <- read_csv("/Users/brinkley97/Documents/development/lab-kcad/datasets/tiles_dataset/figure_2/physical/diurnal_work_lm_6.csv.gz") 
print(df_work)

df_off <- read_csv("/Users/brinkley97/Documents/development/lab-kcad/datasets/tiles_dataset/figure_2/physical/diurnal_off_lm_6.csv.gz") 

df_work$time <- factor(df_work$time)
# print(df_work$time)
df_work$shift <- factor(df_work$shift)
# print(df_work$shift)
df_work$id <- factor(df_work$id)
print(df_work$id)

print(df_work)
df_off$time <- factor(df_off$time)
df_off$shift <- factor(df_off$shift)
df_work$id <- factor(df_work$id)

# ------------------------------------------
# model for shift*age
# ------------------------------------------
model <- ezANOVA(data=df_work, dv=rest, wid=.(id), within=.(time), between=.(shift), type=3)
posthoc = PostHocTest(aov(rest ~ shift*time, data=df_work), method = "lsd")

# sink("diurnal_rest/work_shift_time.txt", append=FALSE)
# print(model)
# print(posthoc)
# sink()

model <- ezANOVA(data=df_off, dv=rest, wid=.(id), within=.(time), between=.(shift), type=3)
posthoc = PostHocTest(aov(rest ~ shift*time, data=df_off), method = "lsd")

# sink("diurnal_rest/off_shift_time.txt", append=FALSE)
# print(model)
# print(posthoc)
# sink()