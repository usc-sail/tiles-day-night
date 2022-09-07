# library(devtools)
# dev_mode()
# install_github('mike-lawrence/ez')
library(DescTools)


diurnal_rest_work = function(df_work) {
    df_work$time <- factor(df_work$time)
    df_work$shift <- factor(df_work$shift)
    df_work$id <- factor(df_work$id)
#     print(df_work)
    rest_work_model <- ezANOVA(data=df_work, dv=rest, wid=.(id), within=.(time), between=.(shift), type=3)
    print(rest_work_model)
    posthoc = PostHocTest(aov(rest ~ shift*time, data=df_work), method = "lsd")
    print(posthoc)
#     print(paste("********* END OF diurnal_rest_work *********"))
}

diurnal_rest_off = function(df_off) {
    df_off$time <- factor(df_off$time)
    df_off$shift <- factor(df_off$shift)
    df_off$id <- factor(df_off$id)
    
    rest_off_model <- ezANOVA(data=df_off, dv=rest, wid=.(id), within=.(time), between=.(shift), type=3)
    print(rest_off_model)
    posthoc = PostHocTest(aov(rest ~ shift*time, data=df_off), method = "lsd")
    print(posthoc)
#     print(paste("********* END OF diurnal_rest_off *********"))
}

diurnal_step_ratio_work = function(df_work) {
    df_work$time <- factor(df_work$time)
    df_work$shift <- factor(df_work$shift)
    df_work$id <- factor(df_work$id)
#     print(df_work)
    step_ratio_work_model <- ezANOVA(data=df_work, dv=step_ratio, wid=.(id), within=.(time), between=.(shift), type=3)
    print(step_ratio_work_model)
    posthoc = PostHocTest(aov(step_ratio ~ shift*time, data=df_work), method = "lsd")
    print(posthoc)
#     print(paste("********* END OF diurnal_rest_work *********"))
}

diurnal_step_ratio_off = function(df_off) {
    df_off$time <- factor(df_off$time)
    df_off$shift <- factor(df_off$shift)
    df_off$id <- factor(df_off$id)
    
    step_ratio_off_model <- ezANOVA(data=df_off, dv=step_ratio, wid=.(id), within=.(time), between=.(shift), type=3)
    print(step_ratio_off_model)
    posthoc = PostHocTest(aov(step_ratio ~ shift*time, data=df_off), method = "lsd")
    print(posthoc)
#     print(paste("********* END OF diurnal_rest_off *********"))
}



