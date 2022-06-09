library(lme4)
library(readr)
library(afex)
library(nlme)
library(emmeans)
library(psycho)
library(tidyverse)
library(easystats)
library(report)
library(sjPlot)
library(sjmisc)
library(ggplot2)
library(jtools)
library(interactions)
library(datasets)
library(lm.beta)
library(reghelper)
library(varhandle)

emm_options(opt.digits = FALSE)

# read data
df <- read_csv("../code/sleep/sleep.csv.gz")
df_work <- subset(df,df$work=='workday')
df_off <- subset(df,df$work=='offday')
df_all <- subset(df,df$work=='all')

df_work <- read_csv("../code/physical/stats_work_lm.csv.gz")
df_off <- read_csv("../code/physical/stats_off_lm.csv.gz")

df_off$step_ratio <- df_off$step_ratio * 100
df_off$rest <- df_off$rest * 100

model <- lm(swls ~ 1 + age + gender + shift * rest, data=df_off)
a <- tab_model(model, show.std = T, show.ci = F, show.est = F)

print(tab_model(model, show.std = T, show.ci = F, show.est = F))

print(summary(model))

# df_work <- read_csv("../code/physical/stats_work_lm.csv.gz")
# df_off <- read_csv("../code/physical/stats_off_lm.csv.gz")
# 
# df_off$step_ratio <- df_off$step_ratio * 100
# df_off$rest <- df_off$rest * 100


# ------------------------------------------
# model for shift*age
# ------------------------------------------
# model <- lm(psqi ~ shift * rest, data=df_off)
# model <- lm(swls ~ shift * rest, data=df_off)
# model <- lm(pan_PosAffect ~ shift * minutesAsleep, data=df_work)
# model <- lm(pan_NegAffect ~ shift * minutesAsleep, data=df_work)
# model <- lm(stai ~ shift * minutesAsleep, data=df_work)

# model <- lm(stai ~ shift * vigorous_min, data=df_off)
# model <- lm(psqi ~ shift * efficiency, data=df_off)

# em <- emmeans(model, ~ shift)
# print(em)

# sink("sleep_duration/work.txt", append=FALSE)

# print(report(model))
# sink()

# ----------------------------------------------------
# PSQI ~ Shift * Sleep Efficiencys (Off-day)
# ----------------------------------------------------
# df_off$shift <- to.dummy(df_off$shift, "shift")
model <- lm(psqi ~ shift * efficiency, data=df_off)
print(summary(model))
print(summary(lm.beta(model)))

pdf("predict/efficiency_off_psqi.pdf", width = 5, height = 5)
par(xpd=TRUE, mar = c(4.5, 4.5, 1.75, 1.25))

text_size = 1.35
plot(x = df_off[df_off$shift == "night", ]$efficiency, y = df_off[df_off$shift == "night", ]$psqi, xlim=c(87,99), ylim=c(0,18),
     cex.axis=text_size, cex.lab=text_size, font.lab=2, cex.main=text_size, xaxt="none", yaxt="none",
     main = "PSQI ~ Shift * Sleep Efficiency (Off-day)",
     pch = 19, xlab = "Sleep Efficiency (%)", ylab = "PSQI", col = rgb(red = 0, green = 0, blue = 1, alpha = 0.6))
points(x = df_off[df_off$shift == "day", ]$efficiency, y = df_off[df_off$shift == "day", ]$psqi, 
       col = rgb(red = 1, green = 0, blue = 0, alpha = 0.6), pch = 19)

clip(87.5,98,0,20)
abline(a = coef(model)[1], b = coef(model)[3], col = "red", lwd = 2)
abline(a = coef(model)[1] + coef(model)[2], b = coef(model)[3] + coef(model)[4], col = "blue", lwd = 2)

clip(85,110,0,20)
axis(1, seq(87,99,3), font=2, cex.axis=text_size)
axis(2, seq(0,18,4), font=2, cex.axis=text_size, las = 2)
legend(93.75, 18.25, legend=c("Day shift", "Night shift"), col=c("red","blue"), lty = c(1, 1), lwd=3, text.font=2, cex = 1.1)
dev.off()



# ----------------------------------------------------
# Life Satisfaction ~ Shift * Sleep Duration (Off-day)
# ----------------------------------------------------
# df_work <- read_csv("../code/physical/stats_work_lm.csv.gz")
# df_off <- read_csv("../code/physical/stats_off_lm.csv.gz")

# df_off$step_ratio <- df_off$step_ratio * 100
# df_off$rest <- df_off$rest * 100
# pan_NegAffect
# rand_GeneralHealth, rand_EnergyFatigue

model <- lm(rand_GeneralHealth ~ shift * efficiency, data=df_off)

print(summary(model))
print(report(model))
print(summary(lm.beta(model)))

pdf("predict/duration_off_ls.pdf", width = 10, height = 5)
par(xpd=TRUE, mar = c(5, 5, 4, 4))

text_size = 1.5
plot(x = df_off[df_off$shift == "night", ]$duration, y = df_off[df_off$shift == "night", ]$swls, xlim=c(150,700), ylim=c(0,9),
     cex.axis=text_size, cex.lab=text_size, font.lab=2, cex.main=text_size, xaxt="none", yaxt="none",
     main = "Life Satisfaction ~ Shift * Sleep Duration (Off-day)",
     pch = 19, xlab = "Sleep Duration (min)", ylab = "Life Satisfaction", col = rgb(red = 0, green = 0, blue = 1, alpha = 0.6))
points(x = df_off[df_off$shift == "day", ]$duration, y = df_off[df_off$shift == "day", ]$swls, 
       col = rgb(red = 1, green = 0, blue = 0, alpha = 0.6), pch = 19)

clip(175,650,0,10)
abline(a = coef(model)[1], b = coef(model)[3], col = "red", lwd = 2)
abline(a = coef(model)[1] + coef(model)[2], b = coef(model)[3] + coef(model)[4], col = "blue", lwd = 2)

clip(100,850,0,10)
axis(1, seq(150,650,125), font=2, cex.axis=text_size)
axis(2, seq(0,9,2), font=2, cex.axis=text_size, las = 2)
legend(595, 9, legend=c("Day shift", "Night shift"), col=c("red","blue"), lty = c(1, 1), lwd=3, text.font=2, cex = 1.1)
dev.off()

# -----------------------------------------------------------
# Positive Affect ~ Shift * Rest Activity Ratio (Off-day)
# -----------------------------------------------------------

df_work <- read_csv("../code/physical/stats_work_lm.csv.gz")
df_off <- read_csv("../code/physical/stats_off_lm.csv.gz")

df_off$step_ratio <- df_off$step_ratio * 100
df_off$rest <- df_off$rest * 100

model <- lm(pan_PosAffect ~ shift * rest, data=df_off)
print(summary(model))
print(lm.beta(model))

pdf("predict/rest_off_pos.pdf", width = 5, height = 5)
par(xpd=TRUE, mar = c(4.5, 4.5, 1.75, 1.25))

text_size = 1.35
plot(x = df_off[df_off$shift == "night", ]$rest, y = df_off[df_off$shift == "night", ]$pan_PosAffect, xlim=c(25, 105), ylim=c(0,80),
     cex.axis=text_size, cex.lab=text_size, font.lab=2, cex.main=text_size, xaxt="none", yaxt="none",
     main = "Pos. Affect ~ Shift * R.R. (Off-day)",
     pch = 19, xlab = "Rest Activity Ratio (%)", ylab = "Positive Affect", col = rgb(red = 0, green = 0, blue = 1, alpha = 0.6))
points(x = df_off[df_off$shift == "day", ]$rest, y = df_off[df_off$shift == "day", ]$pan_PosAffect, 
       col = rgb(red = 1, green = 0, blue = 0, alpha = 0.6), pch = 19)

clip(32.5,100,0,100)
abline(a = coef(model)[1], b = coef(model)[3], col = "red", lwd = 2)
abline(a = coef(model)[1] + coef(model)[2], b = coef(model)[3] + coef(model)[4], col = "blue", lwd = 2)

clip(30,100,0,100)
axis(2, seq(0, 80, 20), font=2, cex.axis=text_size, las = 2)
axis(1, seq(30, 100, 20), font=2, cex.axis=text_size)
legend(70, 80, legend=c("Day shift", "Night shift"), col=c("red","blue"), lty = c(1, 1), lwd=3, text.font=2, cex = 1.1)
dev.off()

# -----------------------------------------------------------
# Life Satisfaction ~ Shift * Walk Activity Ratio (Off-day)
# -----------------------------------------------------------

df_work <- read_csv("../code/physical/stats_work_lm.csv.gz")
df_off <- read_csv("../code/physical/stats_off_lm.csv.gz")

df_off$step_ratio <- df_off$step_ratio * 100
df_off$rest <- df_off$rest * 100

model <- lm(swls ~ shift * step_ratio, data=df_off)
print(summary(model))
print(report(model))
print(summary(lm.beta(model)))
pdf("predict/step_off_ls.pdf", width = 5, height = 5)
par(xpd=TRUE, mar = c(4.5, 4.5, 1.75, 1.25))

text_size = 1.35
plot(x = df_off[df_off$shift == "night", ]$step_ratio, y = df_off[df_off$shift == "night", ]$swls, xlim=c(0, 50), ylim=c(0,9),
     cex.axis=text_size, cex.lab=text_size, font.lab=2, cex.main=text_size, xaxt="none", yaxt="none",
     main = "Life Satisfaction ~ Shift * W.R. (Off-day)", 
     pch = 19, xlab = "Walk Activity Ratio (%)", ylab = "Life Satisfaction", col = rgb(red = 0, green = 0, blue = 1, alpha = 0.6))
points(x = df_off[df_off$shift == "day", ]$step_ratio, y = df_off[df_off$shift == "day", ]$swls, 
       col = rgb(red = 1, green = 0, blue = 0, alpha = 0.6), pch = 19)

clip(5,45,0,9)
abline(a = coef(model)[1], b = coef(model)[3], col = "red", lwd = 2)
abline(a = coef(model)[1] + coef(model)[2], b = coef(model)[3] + coef(model)[4], col = "blue", lwd = 2)

clip(0,50,0,9)
axis(1, seq(0, 50, 10), font=2, cex.axis=text_size)
axis(2, seq(0, 9, 2), font=2, cex.axis=text_size, las = 2)
legend(27.5, 9, legend=c("Day shift", "Night shift"), col=c("red","blue"), lty = c(1, 1), lwd=3, text.font=2, cex = 1.1)
dev.off()


# pdf("predict/rest_off_pos.pdf", width = 10, height = 6)
# p <- interact_plot(model, pred=rest, modx=shift, plot.points = TRUE, lwd=1.5, modx.labels=c("Day shift", "Night shift"),
#                    legend.main="Shift", colors=c("red","blue"), linetype=c("solid", "solid"),
#                    x.label = "\nRest Activity Ratio (%)", y.label = "Positive Affect\n") + theme_classic()
# p$layers[[2]]$aes_params$size <- 3
# p$layers[[2]]$aes_params$alpha <- 0.5
# p$plot_env$ltypes["Night shift"] <- "solid"
# 
# p <- p + labs(title = "Positive Affect ~ Shift * Rest Activity Ratio (Off-day)\n") + theme(plot.title = element_text(hjust = 0.5, vjust = -1))
# p <- p + theme(axis.text=element_text(size=18, face="bold", color = "black"), axis.title=element_text(size=17, face="bold"))
# p <- p + theme(title=element_text(size=15, face='bold')) + scale_linetype_manual(values=c("solid", "solid"))
# 
# p <- p + theme(legend.position = c(0.945, 1.1)) # + theme(legend.position = "none")
# p <- p + theme(legend.text = element_text(size=16, face="bold"), legend.title=element_blank())
# p <- p + theme(plot.background = element_blank(), panel.grid.major = element_blank(), panel.grid.minor = element_blank())
# p <- p + theme(axis.line = element_line(colour = "black", size = 0.5, linetype = "solid"))
# p <- p + theme(plot.margin = unit(c(1.1,1.0,0.5,0.5), "cm"))
# 
# print(p)
# dev.off()

# ----------------------------------------------------
# pdf("predict/step_off_ls.pdf", width = 10, height = 6)
# p <- interact_plot(model, pred=step_ratio, modx=shift, plot.points = TRUE, lwd=1.5, modx.labels=c("Day shift", "Night shift"),
#                    legend.main="Shift", colors=c("red","blue"), linetype=c("solid", "solid"),
#                    x.label = "\nWalk Activity Ratio (%)", y.label = "Life Satisfaction\n") + theme_classic() + ylim(0.5, 9) + xlim(7.5, 45)
# p$layers[[2]]$aes_params$size <- 3
# p$layers[[2]]$aes_params$alpha <- 0.5
# p$plot_env$ltypes["Night shift"] <- "solid"
# 
# p <- p + labs(title = "Life Satisfaction ~ Shift * Walk Activity Ratio (Off-day)\n") + theme(plot.title = element_text(hjust = 0.5, vjust = -1))
# p <- p + theme(axis.text=element_text(size=18, face="bold", color = "black"), axis.title=element_text(size=17, face="bold"))
# p <- p + theme(title=element_text(size=15, face='bold')) + scale_linetype_manual(values=c("solid", "solid"))
# 
# p <- p + theme(legend.position = c(0.945, 1.1)) # + theme(legend.position = "none")
# p <- p + theme(legend.text = element_text(size=16, face="bold"), legend.title=element_blank())
# p <- p + theme(plot.background = element_blank(), panel.grid.major = element_blank(), panel.grid.minor = element_blank())
# p <- p + theme(axis.line = element_line(colour = "black", size = 0.5, linetype = "solid"))
# p <- p + theme(plot.margin = unit(c(1.0,1.0,0.5,0.5), "cm"))
# 
# print(p)
# dev.off()


# p <- interact_plot(model, pred=duration, modx=shift, plot.points = TRUE, lwd=1.5, modx.labels=c("Day shift", "Night shift"),
#                   legend.main="Shift", colors=c("red","blue"), linetype=c("solid", "solid"),
#                   x.label = "\nSleep Duration (min)", y.label = "Life Satisfaction\n") + theme_classic() + ylim(0.5, 9) + xlim(100, 600)

# p$layers[[2]]$aes_params$size <- 3
# p$layers[[2]]$aes_params$alpha <- 0.5
# p$plot_env$ltypes["Night shift"] <- "solid"
# 
# p <- p + labs(title = "Life Satisfaction ~ Shift * Sleep Duration (Off-day)\n") + theme(plot.title = element_text(hjust = 0.5, vjust = -0.25))
# p <- p + theme(axis.text=element_text(size=18, face="bold", color = "black"), axis.title=element_text(size=17, face="bold"))
# p <- p + theme(title=element_text(size=15, face='bold')) + scale_linetype_manual(values=c("solid", "solid"))
# 
# p <- p + theme(legend.position = c(0.945, 1.1)) # + theme(legend.position = "none")
# p <- p + theme(legend.text = element_text(size=16, face="bold"), legend.title=element_blank())
# p <- p + theme(plot.background = element_blank(), panel.grid.major = element_blank(), panel.grid.minor = element_blank())
# p <- p + theme(axis.line = element_line(colour = "black", size = 0.5, linetype = "solid"))
# p <- p + theme(plot.margin = unit(c(1.0,1.0,0.5,0.5), "cm"))


# ----------------------------------------------------
# model <- lm(psqi ~ shift * efficiency, data=df_off)
# pdf("predict/efficiency_off_psqi.pdf", width = 10, height = 6)
# p <- interact_plot(model, pred=efficiency, modx=shift, plot.points = TRUE, lwd=1.5, modx.labels=c("Day shift", "Night shift"),
#                    legend.main="Shift", colors=c("red","blue"), linetype=c("solid", "solid"),
#                    x.label = "\nSleep Efficiencys (min)", y.label = "PSQI\n") + theme_classic() + ylim(0.5, 16) + xlim(88.5, 98)
# p$layers[[2]]$aes_params$size <- 3
# p$layers[[2]]$aes_params$alpha <- 0.5
# p$plot_env$ltypes["Night shift"] <- "solid"
# 
# p <- p + labs(title = "PSQI ~ Shift * Sleep Efficiencys (Off-day)\n") + theme(plot.title = element_text(hjust = 0.5, vjust = -1))
# p <- p + theme(axis.text=element_text(size=18, face="bold", color = "black"), axis.title=element_text(size=17, face="bold"))
# p <- p + theme(title=element_text(size=15, face='bold')) + scale_linetype_manual(values=c("solid", "solid"))
# 
# p <- p + theme(legend.position = c(0.945, 1.1)) # + theme(legend.position = "none")
# p <- p + theme(legend.text = element_text(size=16, face="bold"), legend.title=element_blank())
# p <- p + theme(plot.background = element_blank(), panel.grid.major = element_blank(), panel.grid.minor = element_blank())
# p <- p + theme(axis.line = element_line(colour = "black", size = 0.5, linetype = "solid"))
# p <- p + theme(plot.margin = unit(c(1.0,1.0,0.5,0.5), "cm"))
# 
# print(p)
# dev.off()
