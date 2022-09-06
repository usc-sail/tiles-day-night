# library(devtools)
# dev_mode()
# install_github('mike-lawrence/ez')
library(DescTools)


work_model = function(df_work) {
#     df_work$time <- factor(df_work$time)
#     df_work$shift <- factor(df_work$shift)
#     df_work$id <- factor(df_work$id)
#     print(df_work)
    rest_model <- ezANOVA(data=df_work, dv=rest, wid=.(id), within=.(time), between=.(shift), type=3)
    posthoc = PostHocTest(aov(rest ~ shift*time, data=df_work), method = "lsd")
#     posthoc = chisq.posthoc.test(aov(rest ~ shift*time, data=df_work), method = "lsd")
    }