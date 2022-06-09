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
df <- read_csv("../code/ground_truth/mgt_lm.csv.gz") 

# ------------------------------------------
# model for stress
# ------------------------------------------
# model = lmer(stressd ~ work + shift + shift : work  + (1 | id), data = df)
model = lmer(stressd ~ work * shift  + (1 | id), data = df)
em <- emmeans(model, "work")

text_size <- 1.75

sink("mgt/stressd_mgt.txt", append=FALSE)
print("Facial variance LMM")
print(summary(model))
print(summary(em))
print("-----------------------------------")
print("-----------------------------------")
print(report(model))
sink()

pdf("mgt/stressd.pdf", width = 10, height = 5)
par(xpd=TRUE, mar = c(5, 5, 4, 4))
df$work <- factor(df$work, levels=c("work","off"))
df$shift <- factor(df$shift, levels=c("day","night"))
boxplot(stressd~shift*work, data=df, notch=TRUE, 
        col=(c("#31a354","#756bb1")), 
        xlab="", ylab="", main = "EMA Stress",
        cex.axis=text_size, cex.lab=text_size, font.lab=2, cex.main=text_size,
        yaxt='n', xaxt='n', frame.plot=FALSE)

mtext(side=2, text="Stress", line=2.5, font=2, cex=text_size)
mtext("Workday",side=1,line=1,at=1.5, cex=text_size, font=2)
mtext("Off-day",side=1,line=1,at=3.5, cex=text_size, font=2)

axis(2, at=seq(1,5,1), labels=paste(seq(1,5,1), sep=""), las=1, font=2, cex.axis=1.6)
legend(4.25, 5.2, c("Day shift", "Night shift"), cex=1.35, fill = c("#31a354","#756bb1"), bty='n')
dev.off()


# ------------------------------------------
# model for anxieity
# ------------------------------------------
model = lmer(anxiety ~ work + shift + shift : work  + (1 | id), data = df)
em <- emmeans(model, "work")

sink("mgt/anxiety_mgt.txt", append=FALSE)
print("Facial variance LMM")
print(summary(model))
print(summary(em))
print("-----------------------------------")
print("-----------------------------------")
print(report(model))
sink()

pdf("mgt/anxiety.pdf", width = 10, height = 5)
par(xpd=TRUE, mar = c(5, 5, 4, 4))
df$work <- factor(df$work, levels=c("work","off"))
df$shift <- factor(df$shift, levels=c("day","night"))
boxplot(anxiety~shift*work, data=df, notch=TRUE, 
        col=(c("#31a354","#756bb1")), 
        xlab="", ylab="", main = "EMA Anxiety",
        cex.axis=text_size, cex.lab=text_size, font.lab=2, cex.main=text_size,
        yaxt='n', xaxt='n', frame.plot=FALSE)

mtext(side=2, text="Anxiety", line=2.5, font=2, cex=1.55)
mtext("Workday",side=1,line=1,at=1.5, cex=text_size, font=2)
mtext("Off-day",side=1,line=1,at=3.5, cex=text_size, font=2)

axis(2, at=seq(1,5,1), labels=paste(seq(1,5,1), sep=""), las=1, font=2, cex.axis=1.6)
legend(4.25, 5.2, c("Day shift", "Night shift"), cex=1.35, fill = c("#31a354","#756bb1"), bty='n')
dev.off()

# ------------------------------------------
# model for pos affect
# ------------------------------------------
model = lmer(pand_PosAffect ~ work*shift  + (1 | id), data = df)
em <- emmeans(model, "work")

sink("mgt/pand_PosAffect_mgt.txt", append=FALSE)
print("Facial variance LMM")
print(summary(model))
print(summary(em))
print("-----------------------------------")
print("-----------------------------------")
print(report(model))
sink()

pdf("mgt/pand_PosAffect.pdf", width = 10, height = 5)
par(xpd=TRUE, mar = c(5, 5, 4, 4))
df$work <- factor(df$work, levels=c("work","off"))
df$shift <- factor(df$shift, levels=c("day","night"))
boxplot(pand_PosAffect~shift*work, data=df, notch=TRUE, 
        col=(c("#31a354","#756bb1")), 
        xlab="", ylab="", main = "EMA Positive Affect",
        cex.axis=text_size, cex.lab=text_size, font.lab=2, cex.main=text_size,
        yaxt='n', xaxt='n', frame.plot=FALSE)

mtext(side=2, text="Postive Affect", line=2.5, font=2, cex=text_size)
mtext("Workday",side=1,line=1,at=1.5, cex=text_size, font=2)
mtext("Off-day",side=1,line=1,at=3.5, cex=text_size, font=2)

axis(2, at=seq(5,25,5), labels=paste(seq(5,25,5), sep=""), las=1, font=2, cex.axis=1.6)
legend(4.25, 25.2, c("Day shift", "Night shift"), cex=1.35, fill = c("#31a354","#756bb1"), bty='n')
dev.off()


# ------------------------------------------
# model for negative affect
# ------------------------------------------
model = lmer(pand_NegAffect ~ work*shift + (1 | id), data = df)
em <- emmeans(model, pairwise ~ work*shift)
posthoc <- PostHocTest(aov(pand_NegAffect ~ work*shift, data=df), method = "lsd")
# posthoc <- PostHocTest(model, method = "lsd")

sink("mgt/pand_NegAffect_mgt.txt", append=FALSE)
print("Facial variance LMM")
print(summary(model))
print(summary(em))
print(posthoc)
print("-----------------------------------")
print("-----------------------------------")
print(report(model))
sink()

pdf("mgt/pand_NegAffect.pdf", width = 10, height = 5)
par(xpd=TRUE, mar = c(5, 5, 4, 4))
df$work <- factor(df$work, levels=c("work","off"))
df$shift <- factor(df$shift, levels=c("day","night"))
boxplot(pand_NegAffect~shift*work, data=df, notch=TRUE, 
        col=(c("#31a354","#756bb1")), 
        xlab="", ylab="", main = "EMA Negative Affect",
        cex.axis=text_size, cex.lab=text_size, font.lab=2, cex.main=text_size,
        yaxt='n', xaxt='n', frame.plot=FALSE)

mtext(side=2, text="Negative Affect", line=2.5, font=2, cex=text_size)
mtext("Workday",side=1,line=1,at=1.5, cex=text_size, font=2)
mtext("Off-day",side=1,line=1,at=3.5, cex=text_size, font=2)

axis(2, at=seq(5,25,5), labels=paste(seq(5,25,5), sep=""), las=1, font=2, cex.axis=1.6)
legend(4.25, 25.2, c("Day shift", "Night shift"), cex=1.35, fill = c("#31a354","#756bb1"), bty='n')
dev.off()

# em <- emmeans(m, "Sex")
# contrast(em)
# print(contrast(em, adjust = "bonferroni"))

# print(summary(model))
# print(anova(model))
# 
# em = emmeans(model, "work")
# contrast(em, adjust = "bonferroni")

# print('------------------------------------')
# print('------------------------------------')
# print('------------------------------------')
# 
# model = lmer(pand_NegAffect ~ shift + work + (1 | id), data = d)
# print(summary(model))
# print(anova(model))
# print('------------------------------------')
# print('------------------------------------')
# print('------------------------------------')
# 
# model = lmer(stressd ~ shift + work + (1 | id), data = d)
# print(summary(model))
# print(anova(model))
# print('------------------------------------')
# print('------------------------------------')
# print('------------------------------------')
# 
# model = lmer(anxiety ~ shift + work + (1 | id), data = d)
# print(summary(model))
# print(anova(model))
# print('------------------------------------')
# print('------------------------------------')
# print('------------------------------------')

